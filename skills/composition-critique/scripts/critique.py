#!/usr/bin/env python3
"""Measure one image for a composition critique: VTL kernel, color and radial readings,
where each kernel value sits in a reference set, plain-language facts with the numbers,
an overlay, a three-band value map, and measured crop candidates.

    python critique.py IMAGE [--out DIR] [--no-crops] [--compare EDITED_IMAGE]

Writes DIR/critique.json, DIR/overlay.png, DIR/values.png and (unless --no-crops)
DIR/crops.png. Prints a short summary. Everything is deterministic; nothing here
judges quality. Requires: pip install git+https://github.com/parallaxmetrology/visual-thinking-lens
"""
import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

try:
    import vtl
    from vtl.viz import kernel_overlay
except ImportError:
    sys.exit("The vtl package is missing: pip install git+https://github.com/parallaxmetrology/visual-thinking-lens")

# Empirical percentiles of kernel canon3-v8 over 279 images (Adobe Firefly 100, mixed AI 63,
# museum reproductions 116), from skills/vtl/references/reference-ranges.md. A yardstick, not a norm.
REFERENCE = {
    "delta_x": [-0.0803, -0.0278, -0.0023, 0.0216, 0.0696],
    "delta_y": [-0.0864, -0.0095, 0.0383, 0.1011, 0.1957],
    "r_v":     [0.3159, 0.6222, 0.7601, 0.8703, 0.9354],
    "mu":      [0.0001, 0.0017, 0.0078, 0.0659, 0.2664],
    "x_p":     [0.3105, 0.4031, 0.4701, 0.5187, 0.5845],
    "sdi":     [0.1883, 0.2212, 0.2386, 0.2589, 0.2863],
}
PCTS = [5, 25, 50, 75, 95]
CROP_SIDE = 768  # crops are compared with the original measured at the same size


def percentile_of(key, value):
    """Approximate percentile of value in the reference set (piecewise linear between p05..p95)."""
    q = REFERENCE[key]
    if value <= q[0]:
        return "below p05"
    if value >= q[-1]:
        return "above p95"
    for (p0, v0), (p1, v1) in zip(zip(PCTS, q), zip(PCTS[1:], q[1:])):
        if v0 <= value <= v1:
            return f"~p{round(p0 + (p1 - p0) * (value - v0) / (v1 - v0 or 1e-12))}"
    return "n/a"


def side(dx, dy, tol=0.02):
    h = "right" if dx > tol else "left" if dx < -tol else ""
    v = "low" if dy > tol else "high" if dy < -tol else ""
    return " and ".join(w for w in (v, h) if w) or "at the center"


def pct(x):
    return f"{100 * x:+.0f}%"


def facts(k, c, r):
    """Deterministic, numbered observations. Interpretation is left to the reader."""
    out = []
    out.append(f"Mass centroid sits {side(k['delta_x'], k['delta_y'])}: {pct(k['delta_x'])} of the width, "
               f"{pct(k['delta_y'])} of the height from center (Δx {percentile_of('delta_x', k['delta_x'])}, "
               f"Δy {percentile_of('delta_y', k['delta_y'])} of the reference set; positive Δy = lower).")
    out.append(f"Low-structure field r_v {k['r_v']:.2f} ({percentile_of('r_v', k['r_v'])}); "
               f"read with gradient floor {k['gradient_floor_85']:.2f} / ceiling {k['gradient_ceiling_97']:.2f}.")
    out.append(f"Spread of mass around its own centroid SDI {k['sdi']:.3f} ({percentile_of('sdi', k['sdi'])}: "
               f"lower = concentrated, higher = dispersed).")
    out.append(f"Cohesion μ {k['mu']:.3f} ({percentile_of('mu', k['mu'])}: higher = one dominant body, "
               f"lower = many similar fragments).")
    out.append(f"Peripheral pull x_p {k['x_p']:.2f} ({percentile_of('x_p', k['x_p'])}): share of edge energy "
               f"in the outer 15% of the frame.")
    if c:
        key = "low" if c["okl_L_mean"] < 0.4 else "high" if c["okl_L_mean"] > 0.65 else "middle"
        out.append(f"Value: {key} key (mean OKLab L {c['okl_L_mean']:.2f}), range p05–p95 "
                   f"{c['okl_L_p05']:.2f}–{c['okl_L_p95']:.2f} (contrast {c['lightness_contrast_p95_p05']:.2f}).")
        above = "above" if c["light_delta_y"] < c["dark_delta_y"] else "below"
        out.append(f"Lights sit {side(c['light_delta_x'], c['light_delta_y'])}, darks "
                   f"{side(c['dark_delta_x'], c['dark_delta_y'])}; lights are {above} darks "
                   f"(light Δy {c['light_delta_y']:+.2f}, dark Δy {c['dark_delta_y']:+.2f}).")
        out.append(f"Light concentration {c['spotlight_concentration']:.2f}, shadow concentration "
                   f"{c['shadow_concentration']:.2f} (higher = gathered into fewer places).")
        out.append(f"Chroma: mean {c['okc_C_mean']:.3f}, focality {c['chroma_focality']:.2f} "
                   f"(higher = color gathered in one area, located {side(c['chroma_delta_x'], c['chroma_delta_y'])}); "
                   f"about {c['effective_palette_count']:.1f} effective palette colors: "
                   + ", ".join(c[f"palette_{i}_hex"] for i in range(1, 6)) + ".")
    if r:
        if r.get("radially_ineligible"):
            out.append("Radial organization (RCA-2): not asked; the mass is not compact or round enough for "
                       "rings to mean anything.")
        else:
            better = "the frame center" if r["RC_f"] > r["RC_s"] else "the mass's own centroid"
            out.append(f"Radial organization (RCA-2): mass falls off in rings around {better} slightly better "
                       f"(frame-centered fit RC_f {r['RC_f']:.2f}, mass-centered RC_s {r['RC_s']:.2f}). "
                       f"One image cannot show a default; this only says which center the rings follow.")
    return out


def qa_of(img_path):
    k, fields = vtl.measure(img_path, return_fields=True)
    qa = vtl.mask_qa(fields.mass_mask)
    return k, fields, qa


def crop_boxes(w, h, k):
    """Candidate crops as (label, (left, top, right, bottom)) in pixels."""
    boxes = []
    t = 0.15
    boxes.append(("trim 15% left", (round(w * t), 0, w, h)))
    boxes.append(("trim 15% right", (0, 0, round(w * (1 - t)), h)))
    boxes.append(("trim 15% top", (0, round(h * t), w, h)))
    boxes.append(("trim 15% bottom", (0, 0, w, round(h * (1 - t)))))
    m = 0.10
    boxes.append(("tighten 10% all round", (round(w * m), round(h * m), round(w * (1 - m)), round(h * (1 - m)))))
    # mass centroid in pixels
    mx, my = (w - 1) / 2 + k["delta_x"] * w, (h - 1) / 2 + k["delta_y"] * h
    for name, ar in (("4:5", 4 / 5), ("1:1", 1.0), ("5:4", 5 / 4)):
        cw, ch = (w, w / ar) if w / ar <= h else (h * ar, h)
        cw, ch = cw * 0.92, ch * 0.92
        # place the centroid on the nearest thirds intersection of the crop
        best = None
        for fx in (1 / 3, 2 / 3):
            for fy in (1 / 3, 2 / 3):
                L = min(max(mx - fx * cw, 0), w - cw)
                T = min(max(my - fy * ch, 0), h - ch)
                err = math.hypot(mx - (L + fx * cw), my - (T + fy * ch))
                if best is None or err < best[0]:
                    best = (err, (round(L), round(T), round(L + cw), round(T + ch)))
        boxes.append((f"{name}, aimed at a thirds point", best[1]))
    return boxes


def light_reading(img):
    c = vtl.measure_color(img, max_side=CROP_SIDE)
    return {key: round(float(c[key]), 4) for key in ("light_delta_x", "light_delta_y", "dark_delta_x", "dark_delta_y", "okl_L_mean")}


def kernel_brief(k):
    return {key: round(float(k[key]), 4) for key in ("delta_x", "delta_y", "r_v", "mu", "x_p", "sdi")}


def measure_crops(path, k_full):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    base = vtl.measure(im, max_side=CROP_SIDE)
    rows = [{"label": "original", "box": [0, 0, w, h], "kernel": kernel_brief(base), "color": light_reading(im)}]
    for label, box in crop_boxes(w, h, k_full):
        sub = im.crop(box)
        kk = vtl.measure(sub, max_side=CROP_SIDE)
        rows.append({"label": label, "box": list(box), "valid": int(kk.get("valid", 1)),
                     "kernel": kernel_brief(kk), "color": light_reading(sub),
                     "change": {key: round(float(kk[key]) - base[key], 4) for key in ("delta_x", "delta_y", "r_v", "x_p", "sdi")}})
    return im, rows


def draw_crops(im, rows, out_path, thumb=220):
    cols = 3
    n = len(rows)
    nrows = math.ceil(n / cols)
    sheet = Image.new("RGB", (cols * (thumb + 12) + 12, nrows * (thumb + 46) + 12), (18, 18, 18))
    d = ImageDraw.Draw(sheet)
    for i, row in enumerate(rows):
        sub = im.crop(tuple(row["box"]))
        sub.thumbnail((thumb, thumb))
        x0 = 12 + (i % cols) * (thumb + 12)
        y0 = 12 + (i // cols) * (thumb + 46)
        sheet.paste(sub, (x0, y0))
        sw, sh = sub.size
        cx, cy = x0 + sw / 2, y0 + sh / 2
        d.line([(cx - 8, cy), (cx + 8, cy)], fill=(120, 200, 255), width=2)
        d.line([(cx, cy - 8), (cx, cy + 8)], fill=(120, 200, 255), width=2)
        mx, my = cx + row["kernel"]["delta_x"] * sw, cy + row["kernel"]["delta_y"] * sh
        d.ellipse([mx - 5, my - 5, mx + 5, my + 5], fill=(255, 190, 60))
        d.text((x0, y0 + sh + 4), f"{i}. {row['label']}", fill=(230, 230, 230))
        kk = row["kernel"]
        d.text((x0, y0 + sh + 20), f"dx {kk['delta_x']:+.2f} dy {kk['delta_y']:+.2f} xp {kk['x_p']:.2f}", fill=(160, 160, 160))
    sheet.save(out_path)


def value_map(path, out_path, side_px=512):
    """Three value bands (dark / middle / light) at the image's own terciles of OKLab L: a notan-style check."""
    im = Image.open(path).convert("RGB")
    im.thumbnail((side_px, side_px))
    rgb = np.asarray(im).astype(np.float64) / 255.0
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    l = np.cbrt(0.4122214708 * lin[..., 0] + 0.5363325363 * lin[..., 1] + 0.0514459929 * lin[..., 2])
    m = np.cbrt(0.2119034982 * lin[..., 0] + 0.6806995451 * lin[..., 1] + 0.1073969566 * lin[..., 2])
    s = np.cbrt(0.0883024619 * lin[..., 0] + 0.2817188376 * lin[..., 1] + 0.6299787005 * lin[..., 2])
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    t1, t2 = np.quantile(L, [1 / 3, 2 / 3])
    bands = np.where(L < t1, 40, np.where(L < t2, 128, 225)).astype(np.uint8)
    Image.fromarray(bands).convert("RGB").save(out_path)
    return {"tercile_cuts_L": [round(float(t1), 3), round(float(t2), 3)]}


def compare(a_path, b_path):
    ka, kb = vtl.measure(a_path), vtl.measure(b_path)
    ca, cb = vtl.measure_color(a_path), vtl.measure_color(b_path)
    keys_k = ["delta_x", "delta_y", "r_v", "mu", "x_p", "sdi"]
    keys_c = ["okl_L_mean", "lightness_contrast_p95_p05", "light_delta_x", "light_delta_y", "dark_delta_y",
              "spotlight_concentration", "chroma_focality"]
    return {"before": str(a_path), "after": str(b_path),
            "kernel": {key: [round(ka[key], 4), round(kb[key], 4), round(kb[key] - ka[key], 4)] for key in keys_k},
            "color": {key: [round(ca[key], 4), round(cb[key], 4), round(cb[key] - ca[key], 4)] for key in keys_c},
            "note": "each entry is [before, after, change]; sizes or crops differ, so read direction more than decimals"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("--out", default=None, help="output folder (default: IMAGE_critique/ beside the image)")
    ap.add_argument("--no-crops", action="store_true", help="skip the measured crop candidates")
    ap.add_argument("--compare", default=None, help="an edited version to compare with IMAGE")
    a = ap.parse_args()

    path = Path(a.image)
    out = Path(a.out) if a.out else path.with_name(path.stem + "_critique")
    out.mkdir(parents=True, exist_ok=True)

    k, fields, qa = qa_of(path)
    result = {"image": str(path), "kernel_version": k.get("kernel_version"), "qa": qa,
              "kernel": {key: (round(v, 4) if isinstance(v, float) else v) for key, v in k.items() if key not in ("path",)},
              "reference_percentiles": {key: percentile_of(key, k[key]) for key in REFERENCE}}
    readable = int(k.get("valid", 1)) == 1 and qa.get("mask_status") != "FAIL"
    c = r = None
    if readable:
        c = vtl.measure_color(path)
        result["color"] = {key: (round(v, 4) if isinstance(v, float) else v) for key, v in c.items()}
        try:
            r = vtl.measure_radial(path)
            result["radial"] = {key: (round(v, 4) if isinstance(v, float) else v) for key, v in r.items()}
        except Exception as e:  # radial needs a usable mask; report rather than fail
            result["radial_error"] = str(e)
        result["facts"] = facts(k, c, r)
    else:
        result["facts"] = ["The kernel could not read this image reliably (QA failed); interpret nothing structural."]

    kernel_overlay(fields, k).save(out / "overlay.png")
    result["value_map"] = value_map(path, out / "values.png")
    if readable and not a.no_crops:
        im, rows = measure_crops(path, k)
        result["crops"] = rows
        draw_crops(im, rows, out / "crops.png")
    if a.compare:
        result["compare"] = compare(path, Path(a.compare))

    (out / "critique.json").write_text(json.dumps(result, indent=1, default=str))
    reasons = qa.get("mask_reasons") or ""
    reasons = "; ".join(reasons) if isinstance(reasons, (list, tuple)) else str(reasons)
    print(f"QA: {qa.get('mask_status')} {qa.get('mask_mode', '')} {reasons}".rstrip())
    for f in result["facts"]:
        print("- " + f)
    print(f"Wrote {out}/critique.json, overlay.png, values.png" + (", crops.png" if "crops" in result else ""))


if __name__ == "__main__":
    main()
