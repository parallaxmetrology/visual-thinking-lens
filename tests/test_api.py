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
    assert set(fp["spread"]) <= {"wide", "moderate", "tight", "signed: see window"}


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


def test_arrays_are_rgb_everywhere():
    p = IMAGES / "portrait.jpg"
    rgb = np.asarray(Image.open(p).convert("RGB"))
    assert vtl.measure(rgb)["mu"] == vtl.measure(Image.open(p))["mu"]
    rgba = np.dstack([rgb, np.full(rgb.shape[:2], 255, np.uint8)])
    assert vtl.measure(rgba)["delta_x"] == vtl.measure(rgb)["delta_x"]


def test_batch_has_no_absolute_paths_and_survives_bad_files(tmp_path):
    sub = tmp_path / "set" / "a"
    sub.mkdir(parents=True)
    (sub / "frog.jpg").write_bytes((IMAGES / "frog.jpg").read_bytes())
    (tmp_path / "set" / "frog.jpg").write_bytes((IMAGES / "frog.jpg").read_bytes())
    (tmp_path / "set" / "broken.png").write_bytes(b"not an image")
    hidden = tmp_path / "set" / ".ipynb_checkpoints"
    hidden.mkdir()
    (hidden / "x.jpg").write_bytes((IMAGES / "frog.jpg").read_bytes())
    df = vtl.measure_many(tmp_path / "set")
    assert sorted(df["relpath"]) == ["a/frog.jpg", "broken.png", "frog.jpg"]
    assert "path" not in df.columns
    assert str(tmp_path) not in df.to_csv()
    bad = df[df.relpath == "broken.png"].iloc[0]
    assert bad["valid"] == 0 and "broken.png" in bad["error"]
    assert len(vtl.fingerprint(df)) == len(vtl.KERNEL_KEYS)  # bad row ignored


def test_fingerprint_drops_qa_failures():
    df = pd.DataFrame([{**{k: 0.1 * i for k in vtl.KERNEL_KEYS}, "valid": 1,
                        "mask_status": "FAIL" if i == 0 else "PASS"} for i in range(5)])
    assert vtl.fingerprint(df).loc["mu", "n"] == 4


def test_radial_blank_image_label():
    s = vtl.measure_radial(np.full((200, 300, 3), 128, np.uint8))
    assert s["radial_label"].startswith("No mass detected")


def test_diffusion_preserves_edges_and_does_not_wrap():
    from vtl.kernel import perona_malik
    g = np.zeros((64, 64), np.float32)
    g[:, 32:] = 1.0
    out = perona_malik(g)
    assert out[10, 31] < 0.01 and out[10, 32] > 0.99   # edge kept
    assert out[10, 0] < 0.01 and out[10, 63] > 0.99    # no wraparound


def test_signed_metrics_get_no_cv_spread_label():
    rng = np.random.default_rng(2)
    df = pd.DataFrame({"delta_x": rng.normal(0, 0.01, 50), "sdi": rng.normal(0.25, 0.01, 50)})
    fp = vtl.fingerprint(df, metrics=["delta_x", "sdi"])
    assert fp.loc["delta_x", "spread"] == "signed: see window" and np.isnan(fp.loc["delta_x", "cv"])
    assert fp.loc["sdi", "spread"] == "tight"
