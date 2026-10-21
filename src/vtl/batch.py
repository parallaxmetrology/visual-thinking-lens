"""Measure many images into one table."""
from __future__ import annotations

import os
from typing import Iterable, Union

import pandas as pd

from ._io import find_images_with_roots
from .kernel import measure
from .qa import mask_qa


def measure_many(paths: Union[str, os.PathLike, Iterable], color: bool = False, radial: bool = False,
                 diffusion: bool = False, progress: bool = False) -> pd.DataFrame:
    """One row per image: kernel + mask QA, optionally color (color_*) and radial (radial_*).

    `paths` may be a file, a folder (searched recursively), or a list of either.
    Rows identify images by `filename` and by `relpath` (below the folder you gave),
    never by absolute path, so CSVs are safe to share. An image that can't be read
    gets a row with valid=0 and an `error` message instead of stopping the run.
    """
    if isinstance(paths, (str, os.PathLike)):
        paths = [paths]
    files = find_images_with_roots(*paths)
    if color:
        from .color import measure_color
    if radial:
        from .radial import measure_radial

    rows = []
    for i, (p, rel) in enumerate(files, 1):
        if progress:
            print(f"[{i}/{len(files)}] {rel}", flush=True)
        try:
            k, fields = measure(p, diffusion=diffusion, return_fields=True)
            k.pop("path", None)
            row = {"filename": p.name, "relpath": rel, **k}
            row.update({key: v for key, v in mask_qa(fields.mass_mask).items() if key != "mass_fraction"})
            if color:
                row.update({f"color_{key}": v for key, v in measure_color(p).items()})
            if radial:
                row.update({f"radial_{key}": v for key, v in measure_radial(p).items()})
        except Exception as e:  # keep going; report the file instead of losing the batch
            msg = str(e).replace(str(p), rel)  # no absolute paths in output
            row = {"filename": p.name, "relpath": rel, "valid": 0, "error": f"{type(e).__name__}: {msg}"}
            if progress:
                print(f"    skipped: {row['error']}", flush=True)
        rows.append(row)
    return pd.DataFrame(rows)
