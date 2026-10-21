# Changelog

## 0.1.0 — 2026-10-21

First release as a package. Ported from the research notebooks; outputs match them
on the sample images (see `tests/test_golden.py`).

- `vtl.measure`: kernel `canon3-v8` (Δx, Δy, rᵥ, ρᵣ, μ, xₚ, θ, dₛ, SDI) + mask QA
- `vtl.measure_color`: color/value kernel `color-v0.4.8`
- `vtl.measure_radial`: dual-center radial compliance `rca2-5.21`
- `vtl.fingerprint`, `vtl.rigidity`, `vtl.compare`: corpus readings from the Engine Fingerprint notebook
- `vtl` command line, four example notebooks, browser demo
