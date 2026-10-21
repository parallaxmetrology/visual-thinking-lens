"""
The package must reproduce the reference notebooks exactly.

tests/golden/*.json were produced by running the ORIGINAL notebook code on
examples/images (see tools/golden_from_notebooks.py). If one of these fails,
either the port drifted or a dependency changed numerics — both matter, because
comparability across runs is the point of the instrument.
"""
import json
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


def _load(name):
    return json.loads((GOLDEN / f"{name}.json").read_text())


def _check(got: dict, want: dict, image: str):
    for key, expected in want.items():
        assert key in got, f"{image}: missing {key}"
        actual = got[key]
        if isinstance(expected, str) or isinstance(expected, bool):
            assert actual == expected, f"{image}: {key} = {actual!r}, notebook = {expected!r}"
        else:
            assert math.isclose(float(actual), float(expected), rel_tol=REL, abs_tol=ABS), \
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
