"""
VTL kernel — the canonical gradient-field extractor (Canon 3, v8).

Image -> grayscale -> Sobel gradient -> percentile-band mass mask -> kernel vector.

The kernel is a coordinate system, not a grade. Each value locates an image in
structural space; the diagnostic signal is in how those coordinates spread (or
don't) across a set of images. See docs/interpretation.md.

Coordinate convention: image space, origin top-left.
    delta_x < 0  -> mass left of center     delta_x > 0 -> right of center
    delta_y < 0  -> mass in UPPER frame     delta_y > 0 -> LOWER frame
Plots with delta_y on a vertical axis need invert_yaxis().

Every constant below is frozen. Changing one is a new device version and breaks
comparability with earlier measurements.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import cv2
import numpy as np
from scipy.ndimage import distance_transform_edt
from scipy.spatial import ConvexHull
from skimage.measure import label
from skimage.morphology import skeletonize

from ._io import ImageLike, load_bgr

KERNEL_VERSION = "canon3-v8"

# ── Frozen device constants ──────────────────────────────────────────────────
TARGET_MAX_SIDE = 1536          # canonical working size (aspect-preserving)
GRAD_LOW_PCT = 85.0             # mass mask: keep gradients in [P85, P97]
GRAD_HIGH_PCT = 97.0
EDGE_MARGIN_PX = 2              # border guard against resize/decode artifacts
MIN_MASS_FRAC = 0.001           # below this the image is invalid
WARN_MASS_FRAC = 0.03           # below this the reading is low-confidence
R_V_ABSOLUTE_THRESHOLD = 0.15   # void ratio uses an absolute threshold on purpose
PERIPHERAL_BAND = 0.15          # x_p: outer 15% of each dimension
ORIENT_BINS = 8                 # theta: orientation histogram bins
EPS = 1e-9

# Perona–Malik anisotropic diffusion (optional, off by default).
# Turn on for JPEG-heavy, grainy, scanned or re-saved images; leave off for clean
# PNG exports and any baseline that must match earlier CSVs.
# Perona & Malik (1990), IEEE TPAMI 12(7):629–639.
PM_N_ITERATIONS = 10
PM_KAPPA = 30.0
PM_GAMMA = 0.1
PM_OPTION = 1

KERNEL_KEYS = ("delta_x", "delta_y", "r_v", "rho_r", "mu", "x_p", "theta", "d_s", "sdi")


@dataclass
class Fields:
    """Intermediate fields, for overlays and QA."""
    gray: np.ndarray
    gx: np.ndarray
    gy: np.ndarray
    gmag: np.ndarray
    mass_mask: np.ndarray


# ── Preprocessing ────────────────────────────────────────────────────────────
def perona_malik(gray: np.ndarray, n_iter: int = PM_N_ITERATIONS, kappa: float = PM_KAPPA,
                 gamma: float = PM_GAMMA, option: int = PM_OPTION) -> np.ndarray:
    """Edge-preserving smoothing on float [0,1] luminance. Deterministic."""
    u = gray.copy()
    for _ in range(n_iter):
        dn = np.roll(u, 1, axis=0) - u
        ds = np.roll(u, -1, axis=0) - u
        de = np.roll(u, -1, axis=1) - u
        dw = np.roll(u, 1, axis=1) - u
        if option == 1:
            c = [np.exp(-(d / kappa) ** 2) for d in (dn, ds, de, dw)]
        else:
            c = [1.0 / (1.0 + (d / kappa) ** 2) for d in (dn, ds, de, dw)]
        u = u + gamma * (c[0] * dn + c[1] * ds + c[2] * de + c[3] * dw)
    return np.clip(u, 0.0, 1.0)


def to_gray(img_bgr: np.ndarray, diffusion: bool = False) -> np.ndarray:
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    return perona_malik(gray) if diffusion else gray


def sobel_gradients(gray: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    return gx, gy, np.sqrt(gx * gx + gy * gy)


def mass_mask(gmag: np.ndarray, low_pct: float = GRAD_LOW_PCT, high_pct: float = GRAD_HIGH_PCT,
              edge_margin_px: int = EDGE_MARGIN_PX) -> np.ndarray:
    """Band mask [P_low, P_high] of gradient magnitude; excludes extreme specks."""
    h, w = gmag.shape
    inner = gmag[edge_margin_px:h - edge_margin_px, edge_margin_px:w - edge_margin_px].reshape(-1)
    t_low, t_high = np.percentile(inner, low_pct), np.percentile(inner, high_pct)
    m = (gmag >= t_low) & (gmag <= t_high)
    if edge_margin_px > 0:
        m[:edge_margin_px, :] = m[-edge_margin_px:, :] = False
        m[:, :edge_margin_px] = m[:, -edge_margin_px:] = False
    return m.astype(np.uint8)


# ── Metrics ──────────────────────────────────────────────────────────────────
def mass_fraction(mask: np.ndarray) -> float:
    return float(mask.sum() / float(mask.size))


def delta_x(mask: np.ndarray) -> float:
    """Horizontal placement offset in [-0.5, 0.5]."""
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return 0.0
    w = mask.shape[1]
    return float((xs.mean() - (w - 1) / 2.0) / float(w))


def delta_y(mask: np.ndarray) -> float:
    """Vertical placement offset in [-0.5, 0.5]; negative = upper frame."""
    ys, xs = np.nonzero(mask)
    if len(ys) == 0:
        return 0.0
    h = mask.shape[0]
    return float((ys.mean() - (h - 1) / 2.0) / float(h))


def void_ratio(gmag: np.ndarray, threshold: float = R_V_ABSOLUTE_THRESHOLD) -> float:
    """r_v: fraction of frame below an absolute gradient threshold."""
    return float(1.0 - float((gmag >= threshold).sum() / gmag.size))


def packing_density(mask: np.ndarray) -> float:
    """rho_r: mass area / convex hull area, x100."""
    ys, xs = np.nonzero(mask)
    if len(xs) < 3:
        return 0.0
    hull = ConvexHull(np.stack([xs, ys], axis=1).astype(np.float64))
    return float(100.0 * (len(xs) / (float(hull.volume) + EPS)))  # 2D: volume == area


def cohesion(mask: np.ndarray) -> float:
    """mu = p_max * (1 - H/H_max) over connected-component sizes (8-connected).

    Penalizes fragmentation and equal-sized multi-region layouts alike; a diptych
    of two equal halves reads low by design.
    """
    lab = label(mask > 0, connectivity=2)
    n = int(lab.max())
    if n == 0:
        return 0.0
    if n == 1:
        return 1.0
    areas = np.bincount(lab.ravel())[1:].astype(np.float64)
    p = areas / (areas.sum() + EPS)
    p_max = float(p.max())
    nz = p[p > 0]
    H = float(-(nz * np.log2(nz)).sum())
    H_max = np.log2(n)
    return float(p_max * (1.0 - H / H_max)) if H_max else p_max


def peripheral_pull(gmag: np.ndarray, band: float = PERIPHERAL_BAND) -> float:
    """x_p: share of gradient magnitude in the outer band of the frame."""
    h, w = gmag.shape
    edge = np.zeros((h, w), dtype=bool)
    edge[:int(h * band), :] = True
    edge[int(h * (1.0 - band)):, :] = True
    edge[:, :int(w * band)] = True
    edge[:, int(w * (1.0 - band)):] = True
    total = float(gmag.sum())
    return float(float(gmag[edge].sum()) / total) if total else 0.0


def orientation_stability(gx: np.ndarray, gy: np.ndarray, gmag: np.ndarray, mask: np.ndarray,
                          num_bins: int = ORIENT_BINS) -> float:
    """theta = 1 - H/H_max of the magnitude-weighted orientation histogram on mass pixels."""
    if num_bins != ORIENT_BINS:
        raise ValueError(f"Non-canonical num_bins={num_bins}; canonical is {ORIENT_BINS}.")
    m = mask > 0
    gxs, gys, mags = gx[m], gy[m], gmag[m]
    if len(gxs) == 0 or mags.sum() == 0:
        return 0.0
    ang = np.arctan2(gys, gxs) + np.pi
    idx = np.clip(np.floor(ang / (2.0 * np.pi / num_bins)).astype(int), 0, num_bins - 1)
    weights = np.bincount(idx, weights=mags.astype(np.float64), minlength=num_bins)
    total = weights.sum()
    if total == 0:
        return 0.0
    p = weights / total
    nz = p[p > 0]
    H = float(-(nz * np.log2(nz)).sum())
    return float(1.0 - H / np.log2(num_bins))


def structural_thickness(mask: np.ndarray) -> float:
    """d_s: mean stroke thickness along the skeleton, / min(h, w)."""
    if mask.sum() == 0:
        return 0.0
    m = mask > 0
    dt = distance_transform_edt(m)
    ys, xs = np.nonzero(skeletonize(m))
    if len(xs) == 0:
        return 0.0
    return float((2.0 * dt[ys, xs]).mean() / (float(min(mask.shape)) + EPS))


def spatial_dispersion(mask: np.ndarray) -> float:
    """sdi: mean distance of mass from its centroid, / image diagonal.

    Catches inward collapse that leaves delta_x, r_v and mu unchanged.
    Roughly 0.1 tight blob, 0.25 balanced, 0.4 edge-weighted.
    """
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return 0.0
    d = np.sqrt((xs - xs.mean()) ** 2 + (ys - ys.mean()) ** 2).mean()
    h, w = mask.shape
    return float(d / np.sqrt(h ** 2 + w ** 2))


# ── Entry points ─────────────────────────────────────────────────────────────
def measure_bgr(img_bgr: np.ndarray, diffusion: bool = False) -> Tuple[Dict, Fields]:
    """Kernel vector + fields for an already-standardized BGR uint8 image."""
    gray = to_gray(img_bgr, diffusion=diffusion)
    gx, gy, gmag = sobel_gradients(gray)
    mask = mass_mask(gmag)
    fields = Fields(gray, gx, gy, gmag, mask)
    mf = mass_fraction(mask)

    if mf < MIN_MASS_FRAC:
        out = {k: 0.0 for k in KERNEL_KEYS}
        out.update(r_v=void_ratio(gmag), mass_fraction=float(mf), valid=0,
                   quality_note=f"mass_fraction={mf:.6f} < MIN_MASS_FRAC={MIN_MASS_FRAC:.6f}")
        return out, fields

    out = {
        "delta_x": delta_x(mask),
        "delta_y": delta_y(mask),
        "r_v": void_ratio(gmag),
        "rho_r": packing_density(mask),
        "mu": cohesion(mask),
        "x_p": peripheral_pull(gmag),
        "theta": orientation_stability(gx, gy, gmag, mask),
        "d_s": structural_thickness(mask),
        "sdi": spatial_dispersion(mask),
        "mass_fraction": float(mf),
        "gradient_floor_85": float(np.percentile(gmag.flatten(), 85.0)),
        "gradient_ceiling_97": float(np.percentile(gmag.flatten(), 97.0)),
        "r_v_threshold": R_V_ABSOLUTE_THRESHOLD,
        "valid": 1,
        "quality_note": "",
    }
    if mf < WARN_MASS_FRAC:
        out["quality_note"] = (f"mass_fraction={mf:.4f} in low-structure band "
                               f"({MIN_MASS_FRAC:.3f}–{WARN_MASS_FRAC:.3f}); treat as low-confidence.")
    return out, fields


def measure(image: ImageLike, diffusion: bool = False, max_side: int = TARGET_MAX_SIDE,
            return_fields: bool = False):
    """Measure one image (path, bytes, PIL image, or BGR array).

    Returns the kernel dict, or (dict, Fields) with return_fields=True.

        >>> import vtl
        >>> k = vtl.measure("photo.jpg")
        >>> k["delta_x"], k["sdi"]
    """
    img, meta = load_bgr(image, max_side=max_side)
    out, fields = measure_bgr(img, diffusion=diffusion)
    out = {**meta, **out, "kernel_version": KERNEL_VERSION, "diffusion": int(diffusion)}
    return (out, fields) if return_fields else out
