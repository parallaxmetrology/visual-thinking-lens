"""
Mask QA: describes the mass field the kernel measured. Descriptive, not corrective —
"island soup" is expected for textured, ornamental or stochastic images.

    PASS -> REGION_FIELD   one or a few bodies carry the mass
    WARN -> TEXTURE_FIELD  mass is spread over many small islands
    FAIL -> INVALID        too little (or too much) structure to read
"""
from __future__ import annotations

import hashlib
from typing import Dict

import numpy as np
from skimage.measure import label

from .kernel import MIN_MASS_FRAC, WARN_MASS_FRAC

MAX_MASS_FRAC = 0.85
ISLAND_SOUP_COMPONENTS = 2000
ISLAND_SOUP_LCF = 0.05
TEXTURE_COMPONENTS = 10000
REGION_LCF = 0.25           # largest component >= 25% of mass -> region field
REGIME_COMP_HI = 20000
REGIME_LCF_LO = 0.01


def _as_bool(mask: np.ndarray) -> np.ndarray:
    if mask.dtype == np.bool_:
        return mask
    m = mask.astype(np.float32)
    return m > 0.5 if m.max() <= 1.0 else m > 0


def mask_sha256(mask: np.ndarray) -> str:
    """Hash of the binary mask, for determinism / regression checks."""
    return hashlib.sha256(np.ascontiguousarray(_as_bool(mask).astype(np.uint8)).tobytes()).hexdigest()


def mask_qa(mask: np.ndarray, min_mass_frac: float = MIN_MASS_FRAC,
            warn_mass_frac: float = WARN_MASS_FRAC, max_mass_frac: float = MAX_MASS_FRAC) -> Dict:
    m = _as_bool(mask)
    mf = float(m.mean())
    status, reasons = "PASS", []

    if mf < min_mass_frac:
        status = "FAIL"
        reasons.append(f"mass_fraction<{min_mass_frac:g} (too little structure)")
    elif mf < warn_mass_frac:
        status = "WARN"
        reasons.append(f"mass_fraction<{warn_mass_frac:g} (weak signal / sparse mask)")
    if mf > max_mass_frac:
        status = "FAIL" if status == "PASS" else status
        reasons.append(f"mass_fraction>{max_mass_frac:g} (too much structure / edge-snow risk)")

    lab = label(m, connectivity=1)  # 4-connected here; cohesion (mu) uses 8
    n = int(lab.max())
    if n == 0:
        status = "FAIL"
        reasons.append("no connected components")
        lcf = 0.0
    else:
        comp = np.bincount(lab.ravel())[1:]
        lcf = float(int(comp.max()) / max(int(m.sum()), 1))
        if n > ISLAND_SOUP_COMPONENTS and lcf < ISLAND_SOUP_LCF:
            status = "WARN" if status == "PASS" else status
            reasons.append("many components + tiny largest component (island soup)")
        if n > TEXTURE_COMPONENTS:
            status = "WARN" if status == "PASS" else status
            reasons.append("extremely high component count (likely texture-driven)")

    return {
        "mass_fraction": mf,
        "n_components": n,
        "largest_component_fraction": lcf,
        "mask_sha256": mask_sha256(m),
        "mask_status": status,
        "mask_reasons": "; ".join(reasons),
        "mask_mode": mask_mode(status, lcf),
        "structure_regime": structure_regime(n, lcf),
    }


def mask_mode(status: str, largest_component_fraction: float) -> str:
    if status == "FAIL":
        return "INVALID"
    return "REGION_FIELD" if largest_component_fraction >= REGION_LCF else "TEXTURE_FIELD"


def structure_regime(n_components: int, largest_component_fraction: float) -> str:
    if largest_component_fraction > REGION_LCF:
        return "region"
    if n_components > REGIME_COMP_HI and largest_component_fraction < REGIME_LCF_LO:
        return "texture"
    return "hybrid"
