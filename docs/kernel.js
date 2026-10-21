// VTL kernel (canon3-v8), JavaScript port.
// Mirrors src/vtl/kernel.py and src/vtl/qa.py. Pure functions, no DOM: works in
// browsers and Node. Input is RGBA pixels already resized to the canonical size
// (long side 1536). Browsers resize differently from OpenCV, so in-browser numbers
// are close to, not identical with, the Python reference. On identical pixels the
// gray conversion is bit-exact and metrics agree within a few percent (float32
// Sobel rounding flips a few mask pixels); see tools/check_js_kernel.py.
// Python (src/vtl) is the reference implementation.

export const KERNEL_VERSION = "canon3-v8";
export const TARGET_MAX_SIDE = 1536;
const GRAD_LOW_PCT = 85, GRAD_HIGH_PCT = 97, EDGE_MARGIN_PX = 2;
const MIN_MASS_FRAC = 0.001, WARN_MASS_FRAC = 0.03, R_V_THRESHOLD = 0.15;
const PERIPHERAL_BAND = 0.15, ORIENT_BINS = 8, EPS = 1e-9;
export const KERNEL_KEYS = ["delta_x", "delta_y", "r_v", "rho_r", "mu", "x_p", "theta", "d_s", "sdi"];

// OpenCV COLOR_RGB2GRAY on uint8 (15-bit fixed point, rounded), then /255.
// Verified bit-exact against cv2 4.x on random pixels.
export function toGray(rgba, w, h) {
  const g = new Float32Array(w * h);
  for (let i = 0, j = 0; i < g.length; i++, j += 4) {
    g[i] = Math.fround(((rgba[j] * 9798 + rgba[j + 1] * 19235 + rgba[j + 2] * 3735 + 16384) >> 15) / 255);
  }
  return g;
}

// 3x3 Sobel with OpenCV's default BORDER_REFLECT_101.
export function sobel(gray, w, h) {
  const gx = new Float32Array(w * h), gy = new Float32Array(w * h), mag = new Float32Array(w * h);
  const rx = (x) => (x < 0 ? -x : x >= w ? 2 * w - 2 - x : x);
  const ry = (y) => (y < 0 ? -y : y >= h ? 2 * h - 2 - y : y);
  for (let y = 0; y < h; y++) {
    const y0 = ry(y - 1) * w, y1 = y * w, y2 = ry(y + 1) * w;
    for (let x = 0; x < w; x++) {
      const x0 = rx(x - 1), x2 = rx(x + 1);
      const a = gray[y0 + x0], b = gray[y0 + x], c = gray[y0 + x2];
      const d = gray[y1 + x0], f = gray[y1 + x2];
      const g = gray[y2 + x0], hh = gray[y2 + x], k = gray[y2 + x2];
      const sx = Math.fround((c - a) + 2 * (f - d) + (k - g));
      const sy = Math.fround((g - a) + 2 * (hh - b) + (k - c));
      const i = y1 + x;
      gx[i] = sx; gy[i] = sy; mag[i] = Math.fround(Math.sqrt(Math.fround(sx * sx) + Math.fround(sy * sy)));
    }
  }
  return { gx, gy, mag };
}

// numpy.percentile (linear interpolation) for several q at once.
function percentiles(values, qs) {
  const s = Float64Array.from(values).sort();
  return qs.map((q) => {
    const pos = (q / 100) * (s.length - 1), lo = Math.floor(pos), hi = Math.ceil(pos);
    return s[lo] + (s[hi] - s[lo]) * (pos - lo);
  });
}

export function massMask(mag, w, h) {
  const m = EDGE_MARGIN_PX, inner = new Float32Array((w - 2 * m) * (h - 2 * m));
  let k = 0;
  for (let y = m; y < h - m; y++) for (let x = m; x < w - m; x++) inner[k++] = mag[y * w + x];
  const [lo, hi] = percentiles(inner, [GRAD_LOW_PCT, GRAD_HIGH_PCT]);
  const mask = new Uint8Array(w * h);
  for (let y = m; y < h - m; y++) for (let x = m; x < w - m; x++) {
    const v = mag[y * w + x];
    if (v >= lo && v <= hi) mask[y * w + x] = 1;
  }
  return mask;
}

// Connected components (union–find). conn = 4 or 8. Returns component sizes.
function componentSizes(mask, w, h, conn) {
  const parent = new Int32Array(w * h).fill(-1);
  const find = (i) => { while (parent[i] !== i) { parent[i] = parent[parent[i]]; i = parent[i]; } return i; };
  const union = (a, b) => { a = find(a); b = find(b); if (a !== b) parent[b] = a; };
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const i = y * w + x;
    if (!mask[i]) continue;
    parent[i] = i;
    if (x > 0 && mask[i - 1]) union(i - 1, i);
    if (y > 0) {
      if (mask[i - w]) union(i - w, i);
      if (conn === 8) {
        if (x > 0 && mask[i - w - 1]) union(i - w - 1, i);
        if (x < w - 1 && mask[i - w + 1]) union(i - w + 1, i);
      }
    }
  }
  const sizes = new Map();
  for (let i = 0; i < parent.length; i++) if (parent[i] >= 0) { const r = find(i); sizes.set(r, (sizes.get(r) || 0) + 1); }
  return Array.from(sizes.values());
}

// Convex hull area of mask pixels (per-row extremes suffice), via monotone chain.
function hullArea(mask, w, h) {
  const pts = [];
  for (let y = 0; y < h; y++) {
    let lo = -1, hi = -1;
    for (let x = 0; x < w; x++) if (mask[y * w + x]) { if (lo < 0) lo = x; hi = x; }
    if (lo >= 0) { pts.push([lo, y]); if (hi !== lo) pts.push([hi, y]); }
  }
  if (pts.length < 3) return 0;
  pts.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const cross = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
  const lower = [], upper = [];
  for (const p of pts) { while (lower.length >= 2 && cross(lower[lower.length - 2], lower[lower.length - 1], p) <= 0) lower.pop(); lower.push(p); }
  for (let i = pts.length - 1; i >= 0; i--) { const p = pts[i]; while (upper.length >= 2 && cross(upper[upper.length - 2], upper[upper.length - 1], p) <= 0) upper.pop(); upper.push(p); }
  const hull = lower.slice(0, -1).concat(upper.slice(0, -1));
  let a = 0;
  for (let i = 0; i < hull.length; i++) { const p = hull[i], q = hull[(i + 1) % hull.length]; a += p[0] * q[1] - q[0] * p[1]; }
  return Math.abs(a) / 2;
}

// Exact Euclidean distance transform (Felzenszwalb–Huttenlocher) to nearest 0.
function edt(mask, w, h) {
  const INF = 1e20, f = new Float64Array(Math.max(w, h)), d = new Float64Array(w * h);
  const v = new Int32Array(Math.max(w, h)), z = new Float64Array(Math.max(w, h) + 1);
  const pass = (n, get, set) => {
    for (let q = 0; q < n; q++) f[q] = get(q);
    let k = 0; v[0] = 0; z[0] = -INF; z[1] = INF;
    for (let q = 1; q < n; q++) {
      let s = ((f[q] + q * q) - (f[v[k]] + v[k] * v[k])) / (2 * q - 2 * v[k]);
      while (s <= z[k]) { k--; s = ((f[q] + q * q) - (f[v[k]] + v[k] * v[k])) / (2 * q - 2 * v[k]); }
      k++; v[k] = q; z[k] = s; z[k + 1] = INF;
    }
    k = 0;
    for (let q = 0; q < n; q++) { while (z[k + 1] < q) k++; set(q, (q - v[k]) * (q - v[k]) + f[v[k]]); }
  };
  for (let i = 0; i < w * h; i++) d[i] = mask[i] ? INF : 0;
  for (let x = 0; x < w; x++) pass(h, (y) => d[y * w + x], (y, val) => { d[y * w + x] = val; });
  for (let y = 0; y < h; y++) pass(w, (x) => d[y * w + x], (x, val) => { d[y * w + x] = val; });
  for (let i = 0; i < d.length; i++) d[i] = Math.sqrt(d[i]);
  return d;
}

// Zhang–Suen thinning (skimage's 2D skeletonize is a lookup-table variant of it).
function skeletonize(mask, w, h) {
  const s = Uint8Array.from(mask), del = [];
  let changed = true;
  while (changed) {
    changed = false;
    for (let step = 0; step < 2; step++) {
      del.length = 0;
      for (let y = 1; y < h - 1; y++) for (let x = 1; x < w - 1; x++) {
        const i = y * w + x;
        if (!s[i]) continue;
        const p2 = s[i - w], p3 = s[i - w + 1], p4 = s[i + 1], p5 = s[i + w + 1];
        const p6 = s[i + w], p7 = s[i + w - 1], p8 = s[i - 1], p9 = s[i - w - 1];
        const B = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9;
        if (B < 2 || B > 6) continue;
        const A = (!p2 && p3) + (!p3 && p4) + (!p4 && p5) + (!p5 && p6) + (!p6 && p7) + (!p7 && p8) + (!p8 && p9) + (!p9 && p2);
        if (A !== 1) continue;
        if (step === 0 ? (p2 * p4 * p6 || p4 * p6 * p8) : (p2 * p4 * p8 || p2 * p6 * p8)) continue;
        del.push(i);
      }
      if (del.length) { changed = true; for (const i of del) s[i] = 0; }
    }
  }
  return s;
}

function entropyNorm(p) {
  let H = 0;
  for (const v of p) if (v > 0) H -= v * Math.log2(v);
  return H;
}

export function measureFields(gray, w, h) {
  const { gx, gy, mag } = sobel(gray, w, h);
  const mask = massMask(mag, w, h);
  let n = 0, sx = 0, sy = 0;
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) if (mask[y * w + x]) { n++; sx += x; sy += y; }
  const massFraction = n / (w * h);

  let covered = 0;
  for (let i = 0; i < mag.length; i++) if (mag[i] >= R_V_THRESHOLD) covered++;
  const r_v = 1 - covered / mag.length;
  const out = { mass_fraction: massFraction, r_v, kernel_version: KERNEL_VERSION, w, h };
  if (massFraction < MIN_MASS_FRAC) {
    for (const k of KERNEL_KEYS) if (!(k in out)) out[k] = 0;
    return { kernel: { ...out, valid: 0 }, fields: { gray, mag, mask } };
  }

  const cx = sx / n, cy = sy / n;
  out.delta_x = (cx - (w - 1) / 2) / w;
  out.delta_y = (cy - (h - 1) / 2) / h;
  out.rho_r = 100 * (n / (hullArea(mask, w, h) + EPS));

  const sizes8 = componentSizes(mask, w, h, 8);
  if (sizes8.length === 1) out.mu = 1;
  else {
    const tot = sizes8.reduce((a, b) => a + b, 0), p = sizes8.map((s) => s / (tot + EPS));
    out.mu = Math.max(...p) * (1 - entropyNorm(p) / Math.log2(sizes8.length));
  }

  const bx0 = Math.trunc(w * PERIPHERAL_BAND), bx1 = Math.trunc(w * (1 - PERIPHERAL_BAND));
  const by0 = Math.trunc(h * PERIPHERAL_BAND), by1 = Math.trunc(h * (1 - PERIPHERAL_BAND));
  let edge = 0, total = 0;
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const v = mag[y * w + x]; total += v;
    if (y < by0 || y >= by1 || x < bx0 || x >= bx1) edge += v;
  }
  out.x_p = total ? edge / total : 0;

  const bins = new Float64Array(ORIENT_BINS), bw = (2 * Math.PI) / ORIENT_BINS;
  let wsum = 0, dsum = 0;
  for (let i = 0; i < mask.length; i++) if (mask[i]) {
    const b = Math.min(ORIENT_BINS - 1, Math.max(0, Math.floor((Math.atan2(gy[i], gx[i]) + Math.PI) / bw)));
    bins[b] += mag[i]; wsum += mag[i];
  }
  out.theta = wsum ? 1 - entropyNorm(Array.from(bins, (b) => b / wsum)) / Math.log2(ORIENT_BINS) : 0;

  const dt = edt(mask, w, h), sk = skeletonize(mask, w, h);
  let skN = 0;
  for (let i = 0; i < sk.length; i++) if (sk[i]) { skN++; dsum += 2 * dt[i]; }
  out.d_s = skN ? dsum / skN / (Math.min(w, h) + EPS) : 0;

  let rsum = 0;
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) if (mask[y * w + x]) rsum += Math.hypot(x - cx, y - cy);
  out.sdi = rsum / n / Math.hypot(w, h);

  const sizes4 = componentSizes(mask, w, h, 4);
  out.qa = maskQA(massFraction, sizes4, n);
  out.valid = 1;
  return { kernel: out, fields: { gray, mag, mask } };
}

export function maskQA(mf, sizes4, nOn) {
  let status = "PASS"; const reasons = [];
  if (mf < MIN_MASS_FRAC) { status = "FAIL"; reasons.push("too little structure"); }
  else if (mf < WARN_MASS_FRAC) { status = "WARN"; reasons.push("weak signal / sparse mask"); }
  if (mf > 0.85) { if (status === "PASS") status = "FAIL"; reasons.push("too much structure"); }
  const nc = sizes4.length, lcf = nc ? Math.max(...sizes4) / Math.max(nOn, 1) : 0;
  if (nc === 0) { status = "FAIL"; reasons.push("no connected components"); }
  if (nc > 2000 && lcf < 0.05) { if (status === "PASS") status = "WARN"; reasons.push("island soup"); }
  if (nc > 10000) { if (status === "PASS") status = "WARN"; reasons.push("texture-driven"); }
  const mode = status === "FAIL" ? "INVALID" : lcf >= 0.25 ? "REGION_FIELD" : "TEXTURE_FIELD";
  return { status, reasons, n_components: nc, largest_component_fraction: lcf, mask_mode: mode };
}

export function measureRGBA(rgba, w, h) {
  return measureFields(toGray(rgba, w, h), w, h);
}
