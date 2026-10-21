"""Measure many images into one table."""
from __future__ import annotations

import os
from typing import Iterable, Union

import pandas as pd

from ._io import find_images
from .kernel import measure
from .qa import mask_qa


def measure_many(paths: Union[str, os.PathLike, Iterable], color: bool = False, radial: bool = False,
                 diffusion: bool = False, progress: bool = False) -> pd.DataFrame:
    """One row per image: kernel + mask QA, optionally color (color_*) and radial (radial_*).

    `paths` may be a file, a folder (searched recursively), or a list of either.
    """
    if isinstance(paths, (str, os.PathLike)):
        paths = [paths]
    files = find_images(*paths)
    if color:
        from .color import measure_color
    if radial:
        from .radial import measure_radial

    rows = []
    for i, p in enumerate(files, 1):
        if progress:
            print(f"[{i}/{len(files)}] {p.name}", flush=True)
        k, fields = measure(p, diffusion=diffusion, return_fields=True)
        row = {"filename": p.name, **k}
        row.update({key: v for key, v in mask_qa(fields.mass_mask).items() if key != "mass_fraction"})
        if color:
            row.update({f"color_{key}": v for key, v in measure_color(p).items()})
        if radial:
            row.update({f"radial_{key}": v for key, v in measure_radial(p).items()})
        rows.append(row)
    return pd.DataFrame(rows)
