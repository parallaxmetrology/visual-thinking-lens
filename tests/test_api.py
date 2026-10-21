from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

import vtl
from vtl.cli import main

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "examples" / "images"


def test_inputs_agree_path_bytes_pil():
    p = IMAGES / "portrait.jpg"
    a = vtl.measure(p)
    b = vtl.measure(p.read_bytes())
    assert a["delta_x"] == b["delta_x"] and a["sha256"] == b["sha256"]
    c = vtl.measure(Image.open(p))
    assert abs(c["delta_x"] - a["delta_x"]) < 0.01


def test_flat_image_is_flagged_by_qa():
    # Known Canon 3 behaviour (docs/known-issues.md): with zero gradient both percentile
    # thresholds are 0, so the band mask covers the whole frame and the kernel reports
    # valid=1. Mask QA is what catches it. Kept as-is for comparability with the notebook.
    k, fields = vtl.measure(np.full((256, 256, 3), 128, np.uint8), return_fields=True)
    assert vtl.mask_qa(fields.mass_mask)["mask_status"] == "FAIL"


def test_synthetic_placement():
    # a textured disc on the right, on a quiet ground, should read right-of-center.
    # (A crisp flat disc would NOT: the P85–P97 band skips the strongest edges —
    # see docs/known-issues.md.)
    rng = np.random.default_rng(1)
    yy, xx = np.mgrid[:600, :900]
    disc = (xx - 700) ** 2 + (yy - 300) ** 2 < 120 ** 2
    g = np.where(disc, 120 + rng.normal(0, 40, disc.shape), 230) + rng.normal(0, 3, disc.shape)
    k = vtl.measure(np.stack([np.clip(g, 0, 255).astype(np.uint8)] * 3, -1))
    assert k["delta_x"] > 0.08
    assert abs(k["delta_y"]) < 0.05


def test_measure_many_and_fingerprint():
    df = vtl.measure_many(IMAGES, color=True)
    assert len(df) == len(list(IMAGES.glob("*.jpg")))
    assert {"mask_status", "color_okl_L_mean", "structure_regime"} <= set(df.columns)
    fp = vtl.fingerprint(df)
    assert set(fp.index) == set(vtl.KERNEL_KEYS)
    assert set(fp["spread"]) <= {"wide", "moderate", "tight"}


def test_rigidity_and_compare():
    rng = np.random.default_rng(0)
    rows = []
    for g in range(6):  # prompts move delta_x a lot, re-rolls barely
        for _ in range(4):
            rows.append({"filename": f"p{g}.png", "prompt": g, "valid": 1,
                         **{k: rng.normal(0, 0.01) for k in vtl.KERNEL_KEYS}, "delta_x": g * 0.1 + rng.normal(0, 0.01)})
    df = pd.DataFrame(rows)
    table, overall = vtl.rigidity(df, "prompt")
    assert table.loc["delta_x", "reading"] == "flexible"
    assert table.loc["mu", "reading"] == "rigid"
    cmp = vtl.compare(df, df.assign(delta_x=df.delta_x + 1))
    assert cmp.loc["delta_x", "cohens_d"] < -1


def test_midjourney_prompt_key():
    assert vtl.midjourney_prompt("rus_A_red_chair_--ar_3:2_abc") == "a red chair"


def test_cli(tmp_path, capsys):
    out = tmp_path / "m.csv"
    main(["measure", str(IMAGES), "-o", str(out), "--radial"])
    df = pd.read_csv(out)
    assert "radial_RC_f" in df.columns
    main(["fingerprint", str(out)])
    assert "delta_x" in capsys.readouterr().out
    main(["overlay", str(IMAGES / "frog.jpg"), "-o", str(tmp_path / "o.png")])
    assert (tmp_path / "o.png").exists()
