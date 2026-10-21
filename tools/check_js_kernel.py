"""
Check docs/kernel.js against the Python kernel on identical pixels.

Feeds the exact standardized image that vtl.measure uses (after OpenCV resize)
to the JS port via Node, and reports the largest difference per metric.
Gray conversion is bit-exact; Sobel differs from OpenCV's SIMD path in the last
float32 bit, which flips a few hundred mask pixels at the percentile thresholds.
Hull-based rho_r and component-based mu are the most sensitive to that. In the
browser the bigger difference is resizing (canvas vs INTER_AREA/INTER_CUBIC).

    python tools/check_js_kernel.py
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import cv2
import numpy as np

import vtl
from vtl._io import load_bgr

ROOT = Path(__file__).resolve().parents[1]
RUNNER = """
import { readFileSync } from "node:fs";
import { measureRGBA, KERNEL_KEYS } from "%s";
const jobs = JSON.parse(readFileSync(process.argv[2], "utf8"));
const out = {};
for (const j of jobs) {
  const rgba = new Uint8ClampedArray(readFileSync(j.file));
  const { kernel } = measureRGBA(rgba, j.w, j.h);
  out[j.name] = Object.fromEntries(KERNEL_KEYS.map(k => [k, kernel[k]]));
  out[j.name].mask_mode = kernel.qa.mask_mode;
}
console.log(JSON.stringify(out));
""" % (ROOT / "docs" / "kernel.js").as_uri()


def main():
    tol = 0.10  # see module docstring: float32 Sobel rounding flips a few mask pixels
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        jobs, py = [], {}
        for p in sorted((ROOT / "examples" / "images").glob("*.jpg")):
            bgr, _ = load_bgr(p)
            rgba = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGBA)
            f = td / f"{p.stem}.rgba"
            f.write_bytes(np.ascontiguousarray(rgba).tobytes())
            jobs.append({"name": p.name, "file": str(f), "w": rgba.shape[1], "h": rgba.shape[0]})
            k, fields = vtl.measure(p, return_fields=True)
            py[p.name] = {**{m: k[m] for m in vtl.KERNEL_KEYS}, "mask_mode": vtl.mask_qa(fields.mass_mask)["mask_mode"]}
        (td / "jobs.json").write_text(json.dumps(jobs))
        (td / "run.mjs").write_text(RUNNER)
        js = json.loads(subprocess.run(["node", str(td / "run.mjs"), str(td / "jobs.json")],
                                       check=True, capture_output=True, text=True).stdout)

    worst = {m: 0.0 for m in vtl.KERNEL_KEYS}
    worst_abs = {m: 0.0 for m in vtl.KERNEL_KEYS}
    for name in py:
        for m in vtl.KERNEL_KEYS:
            d = abs(js[name][m] - py[name][m])
            worst_abs[m] = max(worst_abs[m], d)
            worst[m] = max(worst[m], d / max(abs(py[name][m]), 0.05))
        if js[name]["mask_mode"] != py[name]["mask_mode"]:
            print(f"mask_mode differs on {name}: js={js[name]['mask_mode']} py={py[name]['mask_mode']}")
    print("JS vs Python on identical pixels:  max |diff|   max rel (floor 0.05)")
    bad = False
    for m, d in worst.items():
        flag = "" if d <= tol else "  <-- check"
        bad |= bool(flag)
        print(f"  {m:8s} {worst_abs[m]:12.2e} {d:12.2e}{flag}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
