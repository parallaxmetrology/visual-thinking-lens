"""Overlays with Pillow only (no matplotlib needed)."""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw

from .kernel import Fields

MASS = (196, 168, 130)      # measurement gold
CENTER = (122, 158, 142)    # sage
CENTROID = (230, 110, 90)


def _to_u8(a: np.ndarray) -> np.ndarray:
    a = a.astype(np.float64)
    hi = np.percentile(a, 99.5) or 1.0
    return (np.clip(a / hi, 0, 1) * 255).astype(np.uint8)


def kernel_overlay(fields: Fields, kernel: dict, panel: int = 512) -> Image.Image:
    """Three panels: luminance with mass + centroid, gradient field, mass mask."""
    gray = (fields.gray * 255).astype(np.uint8)
    base = np.stack([gray // 2] * 3, axis=-1)
    base[fields.mass_mask > 0] = MASS
    h, w = gray.shape
    left = Image.fromarray(base)
    d = ImageDraw.Draw(left)
    r = max(5, w // 70)
    cx, cy = (w - 1) / 2, (h - 1) / 2
    d.line([(cx - 3 * r, cy), (cx + 3 * r, cy)], fill=CENTER, width=max(1, r // 2))
    d.line([(cx, cy - 3 * r), (cx, cy + 3 * r)], fill=CENTER, width=max(1, r // 2))
    mx = cx + kernel.get("delta_x", 0.0) * w
    my = cy + kernel.get("delta_y", 0.0) * h
    d.ellipse([mx - r, my - r, mx + r, my + r], fill=CENTROID)

    panels = [left, Image.fromarray(_to_u8(fields.gmag)).convert("RGB"),
              Image.fromarray((fields.mass_mask * 255).astype(np.uint8)).convert("RGB")]
    scale = panel / max(h, w)
    size = (max(1, round(w * scale)), max(1, round(h * scale)))
    panels = [p.resize(size, Image.Resampling.LANCZOS) for p in panels]
    out = Image.new("RGB", (size[0] * 3 + 16, size[1]), (10, 10, 10))
    for i, p in enumerate(panels):
        out.paste(p, (i * (size[0] + 8), 0))
    return out
