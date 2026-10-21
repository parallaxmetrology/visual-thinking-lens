"""
Report how far this machine's outputs are from tests/golden/*.json, per metric.

Golden files were generated on macOS arm64 from the original notebooks. Other
platforms (and library versions) take different float paths in OpenCV, so a
few mask pixels can flip at the percentile thresholds. This prints the size of
that drift so tolerances are chosen from evidence, not guessed.

    python tools/golden_diff.py
"""
import json
import platform
from pathlib import Path

import vtl
from vtl.qa import mask_qa

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "examples" / "images"
GOLDEN = ROOT / "tests" / "golden"


def collect():
    got = {"kernel": {}, "color": {}, "radial": {}}
    for p in sorted(IMAGES.glob("*.jpg")):
        k, f = vtl.measure(p, return_fields=True)
        got["kernel"][p.name] = {**k, **{f"qa_{a}": b for a, b in mask_qa(f.mass_mask).items()}}
        got["color"][p.name] = vtl.measure_color(p)
        got["radial"][p.name] = vtl.measure_radial(p)
    return got


def main():
    got = collect()
    print(f"platform: {platform.system()} {platform.machine()}  python {platform.python_version()}")
    for inst in ("kernel", "color", "radial"):
        want = json.loads((GOLDEN / f"{inst}.json").read_text())
        stats, mismatched = {}, set()
        for img, row in want.items():
            for key, w in row.items():
                g = got[inst][img].get(key)
                if isinstance(w, (str, bool)):
                    if g != w:
                        mismatched.add(key)
                    continue
                d = abs(float(g) - float(w))
                rel = d / max(abs(float(w)), 1e-12)
                a, r = stats.get(key, (0.0, 0.0))
                stats[key] = (max(a, d), max(r, rel))
        print(f"\n[{inst}]  max |diff|  max rel")
        for key, (a, r) in sorted(stats.items(), key=lambda kv: -kv[1][1]):
            if r > 1e-9:
                print(f"  {key:34s} {a:10.2e} {r:10.2e}")
        if mismatched:
            print("  non-numeric mismatches:", ", ".join(sorted(mismatched)))


if __name__ == "__main__":
    main()
