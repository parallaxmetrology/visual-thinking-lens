"""
Corpus-level readings — where the kernel's diagnostic power actually lives.

A single kernel vector locates one image. A *fingerprint* describes how a maker
(an engine, an artist, a prompt set) occupies structural space: how wide its
operating window is, where it hits walls, and whether prompts move it at all.

Ported from the Engine Behavioral Fingerprint notebook (v0.3.7). None of these
are quality judgments: a tight window is a fact about the maker, not a flaw.
"""
from __future__ import annotations

import re
from typing import Callable, Iterable, Optional, Sequence, Union

import numpy as np
import pandas as pd

from .kernel import KERNEL_KEYS

CV_WIDE = 0.30
CV_MODERATE = 0.15
WALL_HARD = 0.15
WALL_SOFT = 0.30
RIGID = 1.5
FLEXIBLE = 2.5
SIGNED_LABEL = "signed: see window"


def _is_signed(metric: str) -> bool:
    """Offsets centred on 0 (delta_x, color_light_delta_y, radial_dx, dRC...).
    CV = std/|mean| is meaningless for them: a near-zero mean makes it explode."""
    return "delta" in metric or metric.split("_")[-1] in ("dx", "dy", "dRC")


def _usable(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows the instrument itself marks unreadable (valid=0, or mask QA FAIL)."""
    if "valid" in df.columns:
        df = df[df["valid"] == 1]
    if "mask_status" in df.columns:
        df = df[df["mask_status"] != "FAIL"]
    return df


def _metrics(df: pd.DataFrame, metrics: Optional[Sequence[str]]) -> list:
    if metrics is not None:
        return list(metrics)
    return [m for m in KERNEL_KEYS if m in df.columns]


def fingerprint(df: pd.DataFrame, metrics: Optional[Sequence[str]] = None) -> pd.DataFrame:
    """One row per metric describing the corpus distribution (unreadable rows dropped).

    spread         CV = std/|mean|: wide > 0.30, tight < 0.15 (tight = locked default).
                   Not given for signed offsets (delta_x, delta_y, ...): their mean
                   sits near 0, so CV explodes. Compare window_width instead.
    wall_hardness  std/range: hard < 0.15 (rarely leaves a narrow band), soft > 0.30
    bimodal        platykurtic (kurtosis < 2) and roughly symmetric: maybe two modes
    p10..p90       the operating window; window_width = p90 - p10
    """
    df = _usable(df)
    rows = []
    for m in _metrics(df, metrics):
        v = pd.to_numeric(df[m], errors="coerce").dropna().to_numpy(dtype=float)
        if len(v) < 2:
            continue
        mean, std = v.mean(), v.std()
        signed = _is_signed(m)
        cv = float("nan") if signed else (std / abs(mean) if abs(mean) > 1e-8 else 0.0)
        rng = v.max() - v.min() if v.max() > v.min() else 1.0
        hard = std / rng
        z = (v - mean) / std if std > 0 else np.zeros_like(v)
        skew = float(np.mean(z ** 3)) if std > 0 else 0.0
        kurt = float(np.mean(z ** 4)) if std > 0 else 0.0
        p10, p50, p90 = np.percentile(v, [10, 50, 90])
        rows.append({
            "metric": m, "n": len(v), "mean": mean, "std": std, "cv": cv,
            "spread": (SIGNED_LABEL if signed else
                       "wide" if cv > CV_WIDE else "moderate" if cv > CV_MODERATE else "tight"),
            "p10": p10, "p50": p50, "p90": p90, "window_width": p90 - p10,
            "wall_hardness": hard,
            "walls": "hard" if hard < WALL_HARD else "soft" if hard > WALL_SOFT else "moderate",
            "skew": skew, "kurtosis": kurt,
            "bimodal": bool(len(v) >= 3 and kurt < 2.0 and abs(skew) < 0.8),
        })
    return pd.DataFrame(rows).set_index("metric") if rows else pd.DataFrame()


def midjourney_prompt(stem: str, separator: str = "--ar") -> str:
    """Prompt key from MidJourney-style filenames (prefix_Prompt_words_--ar_...)."""
    s = stem
    for prefix in ("rus_", "mj_", "sora_", "oa_", "dalle_"):
        if s.lower().startswith(prefix):
            s = s[len(prefix):]
    if separator and separator in s:
        s = s[:s.index(separator)]
    return s.strip("_").replace("_", " ").lower()


def rigidity(df: pd.DataFrame, group: Union[str, Callable[[str], str]],
             metrics: Optional[Sequence[str]] = None, filename_col: str = "filename"):
    """Creative rigidity: total std across all grouped images / mean within-group std.

    `group` is a column name, or a function mapping a filename stem to a group key
    (e.g. midjourney_prompt). Only groups with >= 2 images count.

    The numerator is the spread of *all* images in those groups (not of the group
    means), as in the Fingerprint notebook. If prompts don't matter, everything
    varies like re-rolls and the ratio is about 1; the more prompts move structure,
    the higher it goes.

    ratio ~1    different prompts vary no more than re-rolls of one prompt: prior dominates
    ratio > 2.5 prompts drive real structural differences

    Returns (per-metric DataFrame, overall median ratio).
    """
    df = _usable(df)
    if callable(group):
        stems = df[filename_col].astype(str).map(lambda f: re.sub(r"\.[^.]+$", "", f.split("/")[-1]))
        keys = stems.map(group)
    else:
        keys = df[group]
    groups = [g for _, g in df.groupby(keys.values) if len(g) >= 2]
    rows = []
    for m in _metrics(df, metrics):
        within = [np.var(g[m].astype(float)) for g in groups]
        cross = np.concatenate([g[m].astype(float).to_numpy() for g in groups]) if groups else np.array([])
        w_std = float(np.sqrt(np.mean(within))) if within else 0.0
        c_std = float(np.sqrt(np.var(cross))) if len(cross) else 0.0
        ratio = c_std / w_std if w_std > 1e-8 else 0.0
        rows.append({"metric": m, "within_std": w_std, "total_std": c_std, "rigidity_ratio": ratio,
                     "reading": "flexible" if ratio > FLEXIBLE else "moderate" if ratio > RIGID else "rigid"})
    out = pd.DataFrame(rows).set_index("metric")
    valid = out["rigidity_ratio"][out["rigidity_ratio"] > 0]
    return out, float(np.median(valid)) if len(valid) else 0.0


def compare(a: pd.DataFrame, b: pd.DataFrame, metrics: Optional[Sequence[str]] = None,
            labels: Iterable[str] = ("a", "b")) -> pd.DataFrame:
    """Side-by-side corpora: means, spreads, and a standardized difference (Cohen's d).
    Also reports how much of b's p10–p90 window a reaches (window_overlap)."""
    la, lb = labels
    fa, fb = fingerprint(a, metrics), fingerprint(b, metrics)
    rows = []
    for m in fa.index.intersection(fb.index):
        pooled = np.sqrt((fa.at[m, "std"] ** 2 + fb.at[m, "std"] ** 2) / 2.0)
        lo, hi = max(fa.at[m, "p10"], fb.at[m, "p10"]), min(fa.at[m, "p90"], fb.at[m, "p90"])
        wb = fb.at[m, "window_width"]
        rows.append({"metric": m,
                     f"mean_{la}": fa.at[m, "mean"], f"mean_{lb}": fb.at[m, "mean"],
                     f"cv_{la}": fa.at[m, "cv"], f"cv_{lb}": fb.at[m, "cv"],
                     "cohens_d": (fa.at[m, "mean"] - fb.at[m, "mean"]) / pooled if pooled > 0 else 0.0,
                     "window_overlap": max(0.0, hi - lo) / wb if wb > 0 else float(lo <= hi)})
    return pd.DataFrame(rows).set_index("metric")
