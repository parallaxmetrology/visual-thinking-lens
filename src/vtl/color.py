"""
Color and value kernel (Color Kernel v0.4.8): OKLab lightness, chroma, hue, a
deterministic k=5 palette, and where light, dark and chroma sit in the frame.

Like the spatial kernel, these are coordinates, not grades. Centroid offsets use
image convention (negative delta_y = upper frame), range -0.5..0.5.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np
from scipy import ndimage as ndi

from ._io import ImageLike, load_rgb_float

COLOR_VERSION = "color-v0.4.8"
EPS = 1e-12
HIGH_KEY_L = 0.72      # absolute: tints, near-whites
DEEP_DARK_L = 0.35     # absolute: deep shadows, near-blacks
CHROMA_HUE_GATE = 0.02  # hue entropy ignores near-neutral pixels below this chroma


@dataclass(frozen=True)
class ColorFields:
    lab: np.ndarray
    L: np.ndarray
    C: np.ndarray
    hue: np.ndarray
    chroma_mask: np.ndarray
    light_mask: np.ndarray
    dark_mask: np.ndarray
    palette_lab: np.ndarray
    palette_weights: np.ndarray


# ── OKLab ────────────────────────────────────────────────────────────────────
def srgb_to_linear(rgb: np.ndarray) -> np.ndarray:
    return np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)


def linear_srgb_to_oklab(linear: np.ndarray) -> np.ndarray:
    lms = np.empty_like(linear, dtype=np.float32)
    r, g, b = linear[..., 0], linear[..., 1], linear[..., 2]
    lms[..., 0] = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    lms[..., 1] = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    lms[..., 2] = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (np.cbrt(np.maximum(lms, 0.0))[..., i] for i in range(3))
    lab = np.empty_like(linear, dtype=np.float32)
    lab[..., 0] = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    lab[..., 1] = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    lab[..., 2] = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return lab


def rgb_to_oklab(rgb: np.ndarray) -> np.ndarray:
    return linear_srgb_to_oklab(srgb_to_linear(rgb))


def oklab_to_linear_srgb(lab: np.ndarray) -> np.ndarray:
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    rgb = np.empty_like(lab, dtype=np.float32)
    rgb[..., 0] = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    rgb[..., 1] = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    rgb[..., 2] = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return rgb


def linear_to_srgb(linear: np.ndarray) -> np.ndarray:
    linear = np.clip(linear, 0.0, 1.0)
    return np.where(linear <= 0.0031308, linear * 12.92, 1.055 * (linear ** (1 / 2.4)) - 0.055)


def oklab_to_hex(lab: np.ndarray) -> str:
    rgb = linear_to_srgb(oklab_to_linear_srgb(np.asarray(lab, dtype=np.float32)))
    vals = np.clip(np.rint(rgb * 255), 0, 255).astype(np.uint8)
    return "#" + "".join(f"{int(v):02x}" for v in vals)


# ── Helpers ──────────────────────────────────────────────────────────────────
def entropy(values: np.ndarray, bins: int, value_range: Tuple[float, float], weights=None) -> float:
    """Shannon entropy of a histogram, normalized to [0, 1]."""
    hist, _ = np.histogram(values, bins=bins, range=value_range, weights=weights)
    total = float(hist.sum())
    if total <= EPS:
        return 0.0
    p = hist / total
    return float(-float(np.sum(p[p > 0] * np.log(p[p > 0]))) / np.log(bins))


def weighted_sdi(mask: np.ndarray, weights: np.ndarray) -> float:
    """Weighted mean distance from the weighted centroid, / farthest corner."""
    h, w = mask.shape
    yy, xx = np.mgrid[0:h, 0:w]
    mass = np.where(mask, weights, 0.0)
    total = float(mass.sum())
    if total <= EPS:
        return 0.0
    cx = float((mass * xx).sum() / total)
    cy = float((mass * yy).sum() / total)
    corners = np.array([[0, 0], [0, w - 1], [h - 1, 0], [h - 1, w - 1]], dtype=np.float32)
    max_dist = max(float(np.hypot(c[1] - cx, c[0] - cy)) for c in corners)
    return float((mass * np.hypot(xx - cx, yy - cy)).sum() / total / max(max_dist, EPS))


def weighted_offsets(mask: np.ndarray, weights: np.ndarray) -> Tuple[float, float]:
    h, w = mask.shape
    yy, xx = np.mgrid[0:h, 0:w]
    mass = np.where(mask, weights, 0.0)
    total = float(mass.sum())
    if total <= EPS:
        return 0.0, 0.0
    cx = float((mass * xx).sum() / total)
    cy = float((mass * yy).sum() / total)
    return float(cx / max(w - 1, 1) - 0.5), float(cy / max(h - 1, 1) - 0.5)


def largest_component_fraction(mask: np.ndarray) -> float:
    if not mask.any():
        return 0.0
    lbl, count = ndi.label(mask)
    if count == 0:
        return 0.0
    return float(np.bincount(lbl.ravel())[1:].max() / max(mask.sum(), 1))


def kmeans_palette(lab: np.ndarray, k: int = 5, sample_limit: int = 20000,
                   iterations: int = 18) -> Tuple[np.ndarray, np.ndarray]:
    """Deterministic k-means in OKLab: even-stride sampling, lightness-ordered seeds.
    Returns centers and weights sorted by weight (largest first)."""
    pixels = lab.reshape(-1, 3)
    if len(pixels) > sample_limit:
        pixels = pixels[np.linspace(0, len(pixels) - 1, sample_limit, dtype=np.int64)]
    if len(pixels) == 0:
        return np.zeros((k, 3), dtype=np.float32), np.zeros(k, dtype=np.float32)
    order = np.argsort(pixels[:, 0])
    centers = pixels[order[np.linspace(0, len(pixels) - 1, k, dtype=np.int64)]].copy()
    labels = np.zeros(len(pixels), dtype=np.int64)
    for _ in range(iterations):
        labels = np.argmin(np.sum((pixels[:, None, :] - centers[None, :, :]) ** 2, axis=2), axis=1)
        for i in range(k):
            cluster = pixels[labels == i]
            if len(cluster):
                centers[i] = cluster.mean(axis=0)
    counts = np.bincount(labels, minlength=k).astype(np.float32)
    weights = counts / max(float(counts.sum()), EPS)
    by_weight = np.argsort(-weights)
    return centers[by_weight], weights[by_weight]


# ── Entry points ─────────────────────────────────────────────────────────────
def measure_rgb(rgb: np.ndarray) -> Tuple[Dict, ColorFields]:
    """Color metrics for an RGB float [0,1] array."""
    lab = rgb_to_oklab(rgb)
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    C = np.hypot(a, b)
    hue = np.mod(np.arctan2(b, a), 2.0 * np.pi)

    chroma_threshold = float(np.percentile(C, 85))
    chroma_mask = C >= chroma_threshold
    # Relative masks: top/bottom 15% of THIS image's lightness (for position metrics).
    light_mask = L >= float(np.percentile(L, 85))
    dark_mask = L <= float(np.percentile(L, 15))

    palette_lab, palette_weights = kmeans_palette(lab)
    light_dx, light_dy = weighted_offsets(light_mask, L)
    dark_dx, dark_dy = weighted_offsets(dark_mask, 1.0 - L)
    chroma_dx, chroma_dy = weighted_offsets(chroma_mask, C)

    gate = C.ravel() >= CHROMA_HUE_GATE
    hue_gated, C_gated = hue.ravel()[gate], C.ravel()[gate]
    hue_hist, _ = np.histogram(hue.ravel(), bins=12, range=(0.0, 2.0 * np.pi), weights=C.ravel())
    hue_total = float(hue_hist.sum())

    m: Dict = {
        "okl_L_mean": float(L.mean()),
        "okl_L_std": float(L.std()),
        "okl_L_p05": float(np.percentile(L, 5)),
        "okl_L_p95": float(np.percentile(L, 95)),
        "light_mass_fraction": float(light_mask.mean()),
        "dark_mass_fraction": float(dark_mask.mean()),
        "high_key_fraction": float((L >= HIGH_KEY_L).mean()),
        "deep_dark_fraction": float((L <= DEEP_DARK_L).mean()),
        "midtone_fraction": float(((L > DEEP_DARK_L) & (L < HIGH_KEY_L)).mean()),
        "light_sdi": weighted_sdi(light_mask, L),
        "dark_sdi": weighted_sdi(dark_mask, 1.0 - L),
        "light_delta_x": light_dx,
        "light_delta_y": light_dy,
        "dark_delta_x": dark_dx,
        "dark_delta_y": dark_dy,
        "spotlight_concentration": largest_component_fraction(light_mask),
        "shadow_concentration": largest_component_fraction(dark_mask),
        "okc_C_mean": float(C.mean()),
        "okc_C_std": float(C.std()),
        "okc_C_p85": chroma_threshold,
        "hue_entropy": (entropy(hue_gated, bins=36, value_range=(0.0, 2.0 * np.pi), weights=C_gated)
                        if C_gated.size > 0 else 0.0),
        "chroma_entropy": entropy(C.ravel(), bins=24, value_range=(0.0, max(float(C.max()), EPS))),
        "color_sdi": weighted_sdi(chroma_mask, C),
        "chroma_delta_x": chroma_dx,
        "chroma_delta_y": chroma_dy,
        "chroma_focality": largest_component_fraction(chroma_mask),
        "lightness_contrast_p95_p05": float(np.percentile(L, 95) - np.percentile(L, 5)),
        "dominant_hue_occupancy": float(hue_hist.max() / hue_total) if hue_total > EPS else 0.0,
        "palette_compression": float(palette_weights[0]) if len(palette_weights) else 0.0,
        "effective_palette_count": float(1.0 / max(float(np.sum(palette_weights ** 2)), EPS)),
    }
    for i, (center, weight) in enumerate(zip(palette_lab, palette_weights), start=1):
        m[f"palette_{i}_weight"] = float(weight)
        m[f"palette_{i}_okl_L"] = float(center[0])
        m[f"palette_{i}_okl_a"] = float(center[1])
        m[f"palette_{i}_okl_b"] = float(center[2])
        m[f"palette_{i}_hex"] = oklab_to_hex(center)
    return m, ColorFields(lab, L, C, hue, chroma_mask, light_mask, dark_mask, palette_lab, palette_weights)


def measure_color(image: ImageLike, max_side: int = 1536, return_fields: bool = False):
    """Color metrics for one image (path, bytes, PIL image, or RGB array)."""
    m, fields = measure_rgb(load_rgb_float(image, max_side=max_side))
    m["color_version"] = COLOR_VERSION
    return (m, fields) if return_fields else m
