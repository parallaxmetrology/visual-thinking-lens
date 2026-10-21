"""
Radial compliance, dual-center (RCA-2).

Asks whether visual mass falls off in rings, and around which center: the frame
center (a global basin — the "default" prior) or the mass's own centroid (rings
follow the subject). Compliance RC = 1 - Jensen–Shannon distance between the
observed radial mass profile and the best-fitting exponential decay.

Eligibility E_s gates interpretation: a line-like or sprawling mask can't be
"radial" in a meaningful way, and its RC_s should not be read.

Runs at native resolution (no resize), as in the reference notebook.
"""
from __future__ import annotations

from typing import Dict, Tuple

import cv2
import numpy as np
from scipy.optimize import minimize_scalar
from scipy.spatial.distance import jensenshannon

from ._io import ImageLike, load_rgb_u8

RADIAL_VERSION = "rca2-5.21"
DEFAULT_MASK_MODE = "subject"
DEFAULT_BORDER_STRENGTH = 1.5
DEFAULT_NBINS = 60

# Default-prior gate (RDC): "is this a plausible center-default reading?"
# Failing it is not "bad" — it means the image isn't a default-prior case.
RDC_MASK_AREA_MIN = 0.001
RDC_ELIGIBILITY_MIN = 0.55
RDC_DELTA_R_MAX = 0.12
RDC_RCF_MIN = 0.70
RDC_DRC_MAX = 0.03


# ── Masks ────────────────────────────────────────────────────────────────────
def mask_from_otsu(img_rgb: np.ndarray) -> np.ndarray:
    gray = cv2.GaussianBlur(cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY), (5, 5), 0)
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    if th.mean() > 127:
        th = 255 - th
    return (th > 0).astype(np.uint8)


def mask_from_edges(img_rgb: np.ndarray) -> np.ndarray:
    gray = cv2.GaussianBlur(cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY), (5, 5), 0)
    edges = cv2.dilate(cv2.Canny(gray, 50, 150), np.ones((3, 3), np.uint8), iterations=1)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    cnts, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask = np.zeros_like(gray, dtype=np.uint8)
    cv2.drawContours(mask, cnts, -1, 255, thickness=cv2.FILLED)
    return (mask > 0).astype(np.uint8)


def keep_largest_component(mask: np.ndarray) -> np.ndarray:
    mask = mask.astype(np.uint8)
    num, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    if num <= 1:
        return mask
    return (labels == 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])).astype(np.uint8)


def mask_hybrid_field(img_rgb: np.ndarray) -> np.ndarray:
    m = np.clip(mask_from_edges(img_rgb) + mask_from_otsu(img_rgb), 0, 1).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    return keep_largest_component(m)


def border_penalty(mask: np.ndarray, strength: float = 2.0) -> np.ndarray:
    h, w = mask.shape
    yy, xx = np.mgrid[0:h, 0:w]
    d_edge = np.minimum.reduce([yy / max(h - 1, 1), (h - 1 - yy) / max(h - 1, 1),
                                xx / max(w - 1, 1), (w - 1 - xx) / max(w - 1, 1)])
    return mask.astype(np.float64) * np.clip(d_edge ** strength, 0, 1)


def keep_compact_center_component(mask_bin: np.ndarray) -> np.ndarray:
    mask_bin = mask_bin.astype(np.uint8)
    num, labels, stats, cents = cv2.connectedComponentsWithStats(mask_bin, 8)
    if num <= 1:
        return mask_bin
    h, w = mask_bin.shape
    fx, fy = (w - 1) / 2, (h - 1) / 2
    best_i, best_score = None, -1
    for i in range(1, num):
        x, y, wc, hc, area = stats[i]
        touches_edge = (x == 0) or (y == 0) or (x + wc >= w - 1) or (y + hc >= h - 1)
        dist = np.hypot(cents[i][0] - fx, cents[i][1] - fy)
        score = (area * (area / (wc * hc + 1e-9)) * (0.5 if touches_edge else 1.0)) / (1.0 + dist)
        if score > best_score:
            best_i, best_score = i, score
    if best_i is None:
        return keep_largest_component(mask_bin)
    return (labels == best_i).astype(np.uint8)


def compute_mask(img_rgb: np.ndarray, mode: str = DEFAULT_MASK_MODE,
                 border_strength: float = DEFAULT_BORDER_STRENGTH) -> Tuple[np.ndarray, np.ndarray]:
    """Returns (binary mask, mass weights).

    mode='field'   dominant field/plane mass (floors and water can win)
    mode='subject' biased toward compact interior mass; falls back to field if empty
    """
    base = mask_hybrid_field(img_rgb)
    if mode == "field":
        return base.astype(np.uint8), base.astype(np.float64)
    if mode == "subject":
        bw = keep_compact_center_component((border_penalty(base, border_strength) > 0.12).astype(np.uint8))
        if bw.mean() < 0.001:
            return base.astype(np.uint8), base.astype(np.float64)
        return bw.astype(np.uint8), border_penalty(bw, border_strength).astype(np.float64)
    raise ValueError("mode must be 'field' or 'subject'")


# ── Geometry ─────────────────────────────────────────────────────────────────
def frame_center(shape) -> Tuple[float, float]:
    h, w = shape[:2]
    return (w - 1) / 2.0, (h - 1) / 2.0


def mask_centroid(mask_bin: np.ndarray) -> Tuple[float, float]:
    m = (mask_bin > 0).astype(np.float32)
    total = m.sum()
    if total <= 1e-9:
        h, w = mask_bin.shape
        return w / 2.0, h / 2.0
    ys, xs = np.indices(mask_bin.shape)
    return float((xs * m).sum() / total), float((ys * m).sum() / total)


def radial_profile(M: np.ndarray, cx: float, cy: float, nbins: int = DEFAULT_NBINS):
    """Mass-weighted radial histogram, radius normalized by farthest corner.
    Returns (r_centers, p, r_norm, theta)."""
    h, w = M.shape
    ys, xs = np.where(M > 0)
    if len(xs) == 0:
        return np.linspace(0, 1, nbins), np.ones(nbins) / nbins, np.array([]), np.array([])
    dx, dy = xs - cx, ys - cy
    r_max = max(np.hypot(x - cx, y - cy) for x, y in [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]) + 1e-9
    r_norm = np.sqrt(dx * dx + dy * dy) / r_max
    theta = np.arctan2(dy, dx)
    bins = np.linspace(0, 1, nbins + 1)
    idx = np.clip(np.searchsorted(bins, r_norm, side="right") - 1, 0, nbins - 1)
    p = np.bincount(idx, weights=M[ys, xs].astype(np.float64), minlength=nbins)
    p = p / (p.sum() + 1e-12)
    return (bins[:-1] + bins[1:]) / 2.0, p, r_norm, theta


def angular_variance(r_norm: np.ndarray, theta: np.ndarray, nbins: int = DEFAULT_NBINS) -> np.ndarray:
    """Circular variance (1 - R) of angle per radial ring; NaN where a ring has <10 px."""
    if len(r_norm) == 0:
        return np.zeros(nbins)
    bins = np.linspace(0, 1, nbins + 1)
    out = []
    for i in range(nbins):
        t = theta[(r_norm >= bins[i]) & (r_norm < bins[i + 1])]
        if len(t) < 10:
            out.append(np.nan)
            continue
        out.append(1.0 - np.hypot(np.mean(np.cos(t)), np.mean(np.sin(t))))
    return np.array(out, dtype=np.float64)


def fit_exponential(r: np.ndarray, p: np.ndarray) -> Tuple[np.ndarray, float]:
    """Best exp(-alpha r) profile (normalized) by MSE, alpha in [0.1, 200]."""
    r, p = r.astype(np.float64), p.astype(np.float64)

    def loss(alpha):
        q = np.exp(-alpha * r)
        return np.mean((q / (q.sum() + 1e-12) - p) ** 2)

    alpha = float(minimize_scalar(loss, bounds=(0.1, 200.0), method="bounded", options={"xatol": 0.01}).x)
    return np.exp(-alpha * r), alpha  # unnormalized, as in the reference


def compliance(p: np.ndarray, q: np.ndarray) -> Tuple[float, float]:
    jsd = float(jensenshannon(p + 1e-12, q + 1e-12))
    return max(0.0, min(1.0, 1.0 - jsd)), jsd


def _compactness(mask_bin: np.ndarray) -> float:
    ys, xs = np.where(mask_bin > 0)
    if len(xs) == 0:
        return 0.0
    return float(len(xs)) / (float((xs.max() - xs.min() + 1) * (ys.max() - ys.min() + 1)) + 1e-9)


def _isotropy(mask_bin: np.ndarray) -> float:
    ys, xs = np.where(mask_bin > 0)
    if len(xs) < 10:
        return 0.0
    X = np.stack([xs - xs.mean(), ys - ys.mean()], axis=0)
    l1, l2 = np.linalg.eigvalsh((X @ X.T) / (X.shape[1] + 1e-9))
    return 0.0 if l2 <= 1e-9 else float(np.clip(l1 / (l2 + 1e-9), 0.0, 1.0))


def eligibility(mask_bin: np.ndarray, angv: np.ndarray, w_ang: float = 0.35, w_iso: float = 0.35,
                w_comp: float = 0.30) -> Dict:
    comp, iso = _compactness(mask_bin), _isotropy(mask_bin)
    if angv is None or len(angv) == 0:
        ang_mean = 1.0
    else:
        ang_mean = float(np.nanmean(angv[:max(5, int(0.60 * len(angv)))]))
        if np.isnan(ang_mean):
            ang_mean = 1.0
    E = float(np.clip(w_ang * (1.0 - np.clip(ang_mean, 0.0, 1.0)) + w_iso * iso + w_comp * comp, 0.0, 1.0))
    return {"E_s": E, "ang_mean": ang_mean, "compactness": float(comp), "isotropy": float(iso),
            "radially_ineligible": bool(E < 0.38 or iso < 0.22 or comp < 0.08)}


def classify(RCf: float, RCs: float, dRC: float, Es: float, void_ratio: float = None) -> str:
    if void_ratio is not None and 1.0 - void_ratio < RDC_MASK_AREA_MIN:
        return "No mass detected (nothing to interpret)"
    if Es < 0.38:
        return "Mass present but radially ineligible (do not interpret RC_s)"
    if void_ratio is not None and void_ratio > 0.85 and abs(dRC) < 0.03 and max(RCf, RCs) > 0.75:
        return "Field-dominant radial (vignette/gradient, sparse subject)"
    if dRC < -0.06:
        return "Field-dominant radial collapse (global basin wins)"
    if dRC > 0.06:
        return "Subject-dominant radial (rings follow mass)"
    if max(RCf, RCs) > 0.62:
        return "Radial present (dual-center / near-tie)"
    return "Weak/unclear radial (eligible mask, low coherence)"


def default_prior_gate(s: Dict) -> Tuple[bool, str]:
    """RDC gate: does this read as a center-default (prior) composition?"""
    reasons = []
    if 1.0 - s["void_ratio"] < RDC_MASK_AREA_MIN:
        reasons.append(f"mask_area<{RDC_MASK_AREA_MIN:g}")
    if not s["E_s"] >= RDC_ELIGIBILITY_MIN:
        reasons.append(f"E_s<{RDC_ELIGIBILITY_MIN:g}")
    if not s["dr"] <= RDC_DELTA_R_MAX:
        reasons.append(f"delta_r>{RDC_DELTA_R_MAX:g}")
    if not s["RC_f"] >= RDC_RCF_MIN:
        reasons.append(f"RC_f<{RDC_RCF_MIN:g}")
    if not s["dRC"] <= RDC_DRC_MAX:
        reasons.append(f"dRC>{RDC_DRC_MAX:g} (subject-dominant / engineered)")
    return not reasons, "; ".join(reasons)


# ── Entry points ─────────────────────────────────────────────────────────────
def measure_radial_rgb(img_rgb: np.ndarray, mask_mode: str = DEFAULT_MASK_MODE,
                       border_strength: float = DEFAULT_BORDER_STRENGTH, nbins: int = DEFAULT_NBINS,
                       return_fields: bool = False):
    mask_bin, M = compute_mask(img_rgb, mode=mask_mode, border_strength=border_strength)
    h, w = mask_bin.shape
    fx, fy = frame_center(mask_bin.shape)
    sx, sy = mask_centroid(mask_bin)

    r, pf, _, _ = radial_profile(M, fx, fy, nbins)
    _, ps, r_norm_s, theta_s = radial_profile(M, sx, sy, nbins)
    qf, af = fit_exponential(r, pf)
    qs, a_s = fit_exponential(r, ps)
    RCf, JSDf = compliance(pf, qf)
    RCs, JSDs = compliance(ps, qs)
    dRC = RCs - RCf

    dx, dy = (sx - fx) / max(w, 1), (sy - fy) / max(h, 1)
    angv = angular_variance(r_norm_s, theta_s, nbins)
    elig = eligibility(mask_bin, angv)
    void = float(1.0 - mask_bin.mean())

    s = {
        "mask_mode": mask_mode,
        "RC_f": RCf, "JSD_f": JSDf, "alpha_f": af,
        "RC_s": RCs, "JSD_s": JSDs, "alpha_s": a_s,
        "dRC": dRC, "dx": dx, "dy": dy, "dr": float(np.hypot(dx, dy)),
        "void_ratio": void,
        "E_s": elig["E_s"], "compactness": elig["compactness"], "isotropy": elig["isotropy"],
        "ang_mean": elig["ang_mean"], "radially_ineligible": elig["radially_ineligible"],
        "radial_label": classify(RCf, RCs, dRC, elig["E_s"], void),
    }
    s["default_prior"], s["default_prior_reasons"] = default_prior_gate(s)
    s["radial_version"] = RADIAL_VERSION
    if return_fields:
        return s, {"mask": mask_bin, "mass": M, "frame_center": (fx, fy), "mass_center": (sx, sy),
                   "r": r, "p_frame": pf, "p_mass": ps, "q_frame": qf, "q_mass": qs, "angular_variance": angv}
    return s


def measure_radial(image: ImageLike, **kwargs):
    """Radial compliance for one image (path, bytes, PIL image, or RGB array)."""
    return measure_radial_rgb(load_rgb_u8(image), **kwargs)
