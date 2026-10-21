"""
Regenerate tests/golden/*.json by running the ORIGINAL Colab notebooks' code.

The package in src/vtl is a port of those notebooks. This script executes the
notebook cells that define the measurement functions (Colab-only lines are
stripped), runs them on examples/images, and records the outputs. The test suite
then checks that the package reproduces those numbers.

You only need this if you change the reference notebooks. Usage:

    python tools/golden_from_notebooks.py --notebooks /path/to/notebook/folder
"""
import argparse
import json
import re
import sys
import types
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
IMAGES = sorted((ROOT / "examples" / "images").glob("*.jpg"))
OUT = ROOT / "tests" / "golden"

# notebook filename -> code cell indices that hold the measurement definitions
SOURCES = {
    "kernel": ("Canon3_v8_updated_(1).ipynb", [5, 8, 10, 12, 14, 26]),
    "color": ("Color_Kernel_v048_updated.ipynb", [4, 7, 11]),
    "radial": ("RCA2_Dual_Center_fixed_canon5_21.ipynb", [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]),
}

COLAB_LINE = re.compile(r"^\s*(%|!|from google\.colab|import google\.colab|from IPython)")


def load_namespace(nb_path: Path, cells):
    # IPython is imported for display() in some cells; give them a stub.
    stub = types.ModuleType("IPython.display")
    stub.display = stub.Markdown = stub.Image = lambda *a, **k: None
    sys.modules.setdefault("IPython.display", stub)

    nb = json.loads(nb_path.read_text())
    ns = {"__name__": "notebook"}
    plt.show = lambda *a, **k: None
    for i in cells:
        src = "".join(nb["cells"][i]["source"])
        src = "\n".join(line for line in src.splitlines() if not COLAB_LINE.match(line))
        try:
            exec(compile(src, f"{nb_path.name}[{i}]", "exec"), ns)
        except Exception as e:  # trailing demo code in a cell may need uploads
            print(f"  note: {nb_path.name} cell {i} stopped after defs ({type(e).__name__}: {e})")
    return ns


def clean(d):
    out = {}
    for k, v in d.items():
        if isinstance(v, (np.floating, float)):
            out[k] = float(v)
        elif isinstance(v, (np.integer, int, bool, np.bool_)):
            out[k] = v.item() if hasattr(v, "item") else v
        elif isinstance(v, str):
            out[k] = v
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--notebooks", type=Path, required=True)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    print("kernel (Canon 3 v8)")
    ns = load_namespace(args.notebooks / SOURCES["kernel"][0], SOURCES["kernel"][1])
    rows = {}
    for p in IMAGES:
        metrics, fields, meta = ns["compute_kernel_metrics_from_path"](str(p))
        row = clean(metrics)
        row.update({f"qa_{k}": v for k, v in clean(ns["mask_qa"](fields["mass_mask"])).items()})
        rows[p.name] = row
    (OUT / "kernel.json").write_text(json.dumps(rows, indent=1, sort_keys=True))

    print("color (Color Kernel v0.4.8)")
    ns = load_namespace(args.notebooks / SOURCES["color"][0], SOURCES["color"][1])
    rows = {}
    for p in IMAGES:
        rgb = ns["load_rgb"](p) if "load_rgb" in ns else None
        if rgb is None:
            raise RuntimeError("load_rgb not found in color notebook cells")
        metrics, _ = ns["compute_color"](rgb)
        rows[p.name] = clean(metrics)
    (OUT / "color.json").write_text(json.dumps(rows, indent=1, sort_keys=True))

    print("radial (RCA-2)")
    ns = load_namespace(args.notebooks / SOURCES["radial"][0], SOURCES["radial"][1])
    rows = {}
    for p in IMAGES:
        rgb = ns["read_image_rgb"](str(p))
        rows[p.name] = clean(ns["analyze_single"](rgb))
        plt.close("all")
    (OUT / "radial.json").write_text(json.dumps(rows, indent=1, sort_keys=True))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
