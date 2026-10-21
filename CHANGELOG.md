# Changelog

## 0.1.0 — 2026-10-21

First release as a package. Ported from the research notebooks; outputs match them
on the sample images (see `tests/test_golden.py`).

- `vtl.measure`: kernel `canon3-v8` (Δx, Δy, rᵥ, ρᵣ, μ, xₚ, θ, dₛ, SDI) + mask QA
- `vtl.measure_color`: color/value kernel `color-v0.4.8`
- `vtl.measure_radial`: dual-center radial compliance `rca2-5.21`
- `vtl.fingerprint`, `vtl.rigidity`, `vtl.compare`: corpus readings from the Engine Fingerprint notebook
- `vtl` command line, four example notebooks, browser demo

Agent skills (`skills/`): `vtl`, `vtl-color`, `vtl-radial`, `vtl-picture-this`, `measurement-claim-auditor`, distilled from the 2025 skill library and recalibrated to empirical reference ranges (`tools/reference_ranges.py`).

Deliberate differences from the notebooks:

- `diffusion=True` (Perona–Malik) uses κ = 0.12 on [0,1] luminance and mirrored borders. The notebooks' κ = 30 made it a plain blur that also wrapped image edges. The default kernel (diffusion off) is unchanged.
- Arrays passed to any `vtl` function are RGB (RGBA and gray accepted). PIL images are EXIF-corrected like files.
- `measure_many` writes `relpath` instead of absolute paths, and records unreadable files as `valid=0` with an `error` instead of stopping.
- `fingerprint` / `rigidity` / `compare` skip rows with mask QA `FAIL`. Rigidity's numerator is labeled `total_std`, which is what the notebook computed.
- RCA-2 labels an empty mask "No mass detected" instead of "radially ineligible".
