"""
The package must reproduce the reference notebooks exactly.

tests/golden/*.json were produced by running the ORIGINAL notebook code on
examples/images (see tools/golden_from_notebooks.py). If one of these fails,
either the port drifted or a dependency changed numerics — both matter, because
comparability across runs is the point of the instrument.
"""
import json
import platform
import math
from pathlib import Path

import pytest

import vtl
from vtl.kernel import measure
from vtl.qa import mask_qa

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "examples" / "images"
GOLDEN = ROOT / "tests" / "golden"

REL, ABS = 1e-7, 1e-9

# Goldens were generated on the reference platform (macOS arm64), where the port
# must match the notebooks to 1e-7. Elsewhere OpenCV takes different SIMD paths
# (resize/Sobel), flipping ~0.5% of kernel mask pixels at the percentile
# thresholds. Measured on x86-64 Linux with tools/golden_diff.py (max abs diff):
#   delta_x 1.8e-4, delta_y 3.1e-4, mu 9.5e-4, theta 1.5e-3, rho_r 0.067,
#   mass_fraction 6.7e-4, x_p 6.9e-5, sdi 3.5e-5, r_v 5.6e-5, d_s 1.9e-6.
# Radial matched exactly; color within ~1e-7 absolute. Tolerances below are
# ~3x the measured drift, all far below interpretive resolution.
REFERENCE = platform.system() == "Darwin" and platform.machine() == "arm64"
CROSS_ABS = {
    "delta_x": 1e-3, "delta_y": 1e-3, "mu": 3e-3, "theta": 5e-3, "rho_r": 0.2,
    "mass_fraction": 2e-3, "x_p": 3e-4, "sdi": 2e-4, "r_v": 2e-4, "d_s": 1e-5,
    "gradient_ceiling_97": 1.5e-3, "gradient_floor_85": 1e-6,
    "largest_component_fraction": 0.05,
}
CROSS_REL = {"n_components": 0.03}
CROSS_DEFAULT = (1e-4, 1e-6)  # color and radial


def _tol(key):
    if REFERENCE:
        return REL, ABS
    if key in CROSS_ABS:
        return 0.0, CROSS_ABS[key]
    if key in CROSS_REL:
        return CROSS_REL[key], 0.0
    return CROSS_DEFAULT


def _load(name):
    return json.loads((GOLDEN / f"{name}.json").read_text())


def _check(got: dict, want: dict, image: str):
    for key, expected in want.items():
        assert key in got, f"{image}: missing {key}"
        actual = got[key]
        if key == "mask_sha256" and not REFERENCE:
            continue  # exact mask identity only holds on the reference platform
        if isinstance(expected, str) or isinstance(expected, bool):
            assert actual == expected, f"{image}: {key} = {actual!r}, notebook = {expected!r}"
        else:
            rel, abs_ = _tol(key)
            assert math.isclose(float(actual), float(expected), rel_tol=rel, abs_tol=abs_), \
                f"{image}: {key} = {actual!r}, notebook = {expected!r}"


KERNEL = _load("kernel")
COLOR = _load("color")
RADIAL = _load("radial")


@pytest.mark.parametrize("image", sorted(KERNEL))
def test_kernel_matches_canon3_notebook(image):
    k, fields = measure(IMAGES / image, return_fields=True)
    want = {key: v for key, v in KERNEL[image].items() if not key.startswith("qa_")}
    _check(k, want, image)
    qa = mask_qa(fields.mass_mask)
    _check(qa, {key[3:]: v for key, v in KERNEL[image].items() if key.startswith("qa_")}, image)


@pytest.mark.parametrize("image", sorted(COLOR))
def test_color_matches_v048_notebook(image):
    _check(vtl.measure_color(IMAGES / image), COLOR[image], image)


@pytest.mark.parametrize("image", sorted(RADIAL))
def test_radial_matches_rca2_notebook(image):
    _check(vtl.measure_radial(IMAGES / image), RADIAL[image], image)


def test_deterministic_mask_hash():
    a = mask_qa(measure(IMAGES / "frog.jpg", return_fields=True)[1].mass_mask)["mask_sha256"]
    b = mask_qa(measure(IMAGES / "frog.jpg", return_fields=True)[1].mass_mask)["mask_sha256"]
    assert a == b
