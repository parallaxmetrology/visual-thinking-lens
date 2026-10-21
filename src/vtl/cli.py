"""
Command line:

    vtl measure IMAGE_OR_FOLDER... [-o out.csv] [--color] [--radial] [--diffusion]
    vtl fingerprint measurements.csv [--group-by COLUMN | --mj-prompts]
    vtl compare a.csv b.csv [--labels A B]
    vtl overlay IMAGE [-o overlay.png]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd


def _cmd_measure(a):
    from .batch import measure_many
    df = measure_many(a.paths, color=a.color, radial=a.radial, diffusion=a.diffusion, progress=a.out is not None)
    if df.empty:
        sys.exit("No images found.")
    if a.out:
        df.to_csv(a.out, index=False)
        print(f"Wrote {len(df)} rows -> {a.out}")
    elif len(df) == 1 and not a.csv:
        row = df.iloc[0].to_dict()
        print(json.dumps({k: (v.item() if hasattr(v, "item") else v) for k, v in row.items()}, indent=2))
    else:
        df.to_csv(sys.stdout, index=False)


def _cmd_fingerprint(a):
    from .corpus import fingerprint, midjourney_prompt, rigidity
    df = pd.read_csv(a.csv)
    pd.set_option("display.width", 160)
    print(f"Corpus: {len(df)} images\n")
    print(fingerprint(df).round(4).to_string())
    group = a.group_by or (midjourney_prompt if a.mj_prompts else None)
    if group is not None:
        table, overall = rigidity(df, group)
        print("\nCreative rigidity (between-prompt std / within-prompt std)\n")
        print(table.round(4).to_string())
        reading = "rigid" if overall < 1.5 else "moderate" if overall < 2.5 else "flexible"
        print(f"\nOverall rigidity ratio (median): {overall:.3f}  -> {reading}")


def _cmd_compare(a):
    from .corpus import compare
    pd.set_option("display.width", 160)
    print(compare(pd.read_csv(a.a), pd.read_csv(a.b), labels=a.labels).round(4).to_string())


def _cmd_overlay(a):
    from .kernel import measure
    from .viz import kernel_overlay
    k, fields = measure(a.image, return_fields=True)
    out = a.out or str(Path(a.image).with_suffix("")) + "_vtl.png"
    kernel_overlay(fields, k).save(out)
    print(f"Wrote {out}")


def main(argv=None):
    p = argparse.ArgumentParser(prog="vtl", description="Visual Thinking Lens — measure the geometry of images.")
    sub = p.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("measure", help="kernel vector for images or folders")
    m.add_argument("paths", nargs="+")
    m.add_argument("-o", "--out", help="write CSV here (default: JSON for one image, CSV to stdout otherwise)")
    m.add_argument("--csv", action="store_true", help="CSV output even for a single image")
    m.add_argument("--color", action="store_true", help="add color/value kernel (color_*)")
    m.add_argument("--radial", action="store_true", help="add radial compliance RCA-2 (radial_*)")
    m.add_argument("--diffusion", action="store_true", help="Perona–Malik preprocessing (JPEG/grain)")
    m.set_defaults(func=_cmd_measure)

    f = sub.add_parser("fingerprint", help="how a corpus occupies structural space")
    f.add_argument("csv")
    g = f.add_mutually_exclusive_group()
    g.add_argument("--group-by", help="column holding the prompt/group key, for rigidity")
    g.add_argument("--mj-prompts", action="store_true", help="derive prompt groups from MidJourney filenames")
    f.set_defaults(func=_cmd_fingerprint)

    c = sub.add_parser("compare", help="compare two measured corpora")
    c.add_argument("a")
    c.add_argument("b")
    c.add_argument("--labels", nargs=2, default=("a", "b"))
    c.set_defaults(func=_cmd_compare)

    o = sub.add_parser("overlay", help="save mass-mask / gradient overlay PNG")
    o.add_argument("image")
    o.add_argument("-o", "--out")
    o.set_defaults(func=_cmd_overlay)

    a = p.parse_args(argv)
    a.func(a)


if __name__ == "__main__":
    main()
