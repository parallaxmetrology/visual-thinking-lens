#!/usr/bin/env python3
"""Count what composition moves measurably do, from before/after image pairs.

    python move_signatures.py pairs.csv [--root DIR] [--out signatures.md]

pairs.csv columns: before, after, move (a short label such as offcenter-negative-space),
and an optional note. Each pair is measured with the VTL kernel and color instruments.
The report gives every pair's changes and, for each move label, how many pairs moved each
reading up or down. Use it to calibrate the moves in references/moves.md on your own
pictures. Counts from a handful of pairs describe those pairs; they are not laws.
"""
import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import vtl

KERNEL = ["delta_x", "delta_y", "r_v", "mu", "x_p", "sdi", "theta"]
COLOR = ["okl_L_mean", "lightness_contrast_p95_p05", "spotlight_concentration", "shadow_concentration",
         "chroma_focality", "okc_C_mean"]
DERIVED = {
    "off_center": "distance of the mass centroid from the frame center (hypot of Δx, Δy)",
    "light_over_dark": "dark Δy minus light Δy (positive = lights sit above darks)",
}
# A change smaller than this counts as "no change" for the up/down tally (in each reading's own units).
TOL = {"delta_x": 0.01, "delta_y": 0.01, "off_center": 0.01, "r_v": 0.01, "mu": 0.005, "x_p": 0.01,
       "sdi": 0.005, "theta": 0.002, "okl_L_mean": 0.01, "lightness_contrast_p95_p05": 0.02,
       "spotlight_concentration": 0.02, "shadow_concentration": 0.02, "chroma_focality": 0.02,
       "okc_C_mean": 0.005, "light_over_dark": 0.02}


def reading(path):
    k, c = vtl.measure(path), vtl.measure_color(path)
    r = {key: float(k[key]) for key in KERNEL}
    r.update({key: float(c[key]) for key in COLOR})
    r["off_center"] = math.hypot(r["delta_x"], r["delta_y"])
    r["light_over_dark"] = float(c["dark_delta_y"]) - float(c["light_delta_y"])
    r["valid"] = int(k.get("valid", 1))
    return r


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pairs")
    ap.add_argument("--root", default=None, help="folder the image paths are relative to (default: the CSV's folder)")
    ap.add_argument("--out", default=None, help="markdown report (default: beside the CSV)")
    a = ap.parse_args()
    csv_path = Path(a.pairs)
    root = Path(a.root) if a.root else csv_path.parent
    rows = list(csv.DictReader(csv_path.open()))
    keys = ["off_center"] + KERNEL + COLOR + ["light_over_dark"]

    cache, pairs = {}, []
    for row in rows:
        for side in ("before", "after"):
            p = root / row[side]
            if p not in cache:
                cache[p] = reading(p)
        b, f = cache[root / row["before"]], cache[root / row["after"]]
        pairs.append({"before": row["before"], "after": row["after"], "move": row["move"].strip(),
                      "note": row.get("note", ""), "valid": min(b["valid"], f["valid"]),
                      "change": {k: f[k] - b[k] for k in keys}, "before_values": {k: b[k] for k in keys},
                      "after_values": {k: f[k] for k in keys}})

    by_move = defaultdict(list)
    for p in pairs:
        by_move[p["move"]].append(p)

    lines = ["# Move signatures", "",
             f"{len(pairs)} before/after pairs, {len(by_move)} move labels. For each move: how many pairs moved each "
             "reading up (↑) or down (↓) by more than a small tolerance, and the median change. Counts describe these "
             "pairs only.", ""]
    summary = {}
    for move, ps in sorted(by_move.items(), key=lambda kv: -len(kv[1])):
        lines += [f"## {move} ({len(ps)} pair{'s' if len(ps) != 1 else ''})", "",
                  "| reading | ↑ | ↓ | ~ | median change |", "|---|---|---|---|---|"]
        summary[move] = {}
        for k in keys:
            ch = sorted(p["change"][k] for p in ps)
            up = sum(c > TOL[k] for c in ch)
            down = sum(c < -TOL[k] for c in ch)
            med = ch[len(ch) // 2] if len(ch) % 2 else 0.5 * (ch[len(ch) // 2 - 1] + ch[len(ch) // 2])
            summary[move][k] = {"up": up, "down": down, "flat": len(ch) - up - down, "median": round(med, 4)}
            lines.append(f"| `{k}` | {up} | {down} | {len(ch) - up - down} | {med:+.3f} |")
        lines += [""]
    lines += ["## Pairs", "", "| move | before → after | off-center | Δy | r_v | μ | x_p | θ | light over dark | chroma focality |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for p in pairs:
        b, f = p["before_values"], p["after_values"]
        lines.append(f"| {p['move']} | {p['before']} → {p['after']} | {b['off_center']:.2f}→{f['off_center']:.2f} | "
                     f"{b['delta_y']:+.2f}→{f['delta_y']:+.2f} | {b['r_v']:.2f}→{f['r_v']:.2f} | {b['mu']:.3f}→{f['mu']:.3f} | "
                     f"{b['x_p']:.2f}→{f['x_p']:.2f} | {b['theta']:.3f}→{f['theta']:.3f} | "
                     f"{b['light_over_dark']:+.2f}→{f['light_over_dark']:+.2f} | {b['chroma_focality']:.2f}→{f['chroma_focality']:.2f} |")
    lines += ["", "Derived readings: " + "; ".join(f"`{k}` = {v}" for k, v in DERIVED.items()) + "."]

    out = Path(a.out) if a.out else csv_path.with_name("move_signatures.md")
    out.write_text("\n".join(lines) + "\n")
    out.with_suffix(".json").write_text(json.dumps({"pairs": pairs, "summary": summary}, indent=1))
    print(f"Wrote {out} and {out.with_suffix('.json')}")


if __name__ == "__main__":
    main()
