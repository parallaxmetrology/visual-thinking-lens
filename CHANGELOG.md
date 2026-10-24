# Changelog

## Unreleased

- New agent skill `composition-critique`: feedback on one picture against what it is meant to do. A script (`skills/composition-critique/scripts/critique.py`) measures the kernel, color and radial readings, places kernel values in the reference set, writes plain-language facts, an overlay, a three-band value map and measured crop candidates, and compares an edited version with the original (`--compare`). No package code changed.
- New agent skill `deformation-operators`: prompts for image generators that deform a body or form on purpose (coil, stretch, twist, arc, wave, depth pull, framing) so it reads as the limb itself. Nine operators with safe defaults, capsules, acceptance checks and fixes, plus GPT/Gemini and Midjourney/SDXL recipes. Adapted from the Deformation Operator Playbook; example images at https://parallaxmetrology.com/deformation_operator_playbook. No measurement involved.
- New agent skill `foreshortening-recipes`: prompts that hold strong foreshortening and depth by describing the subject in numbered stages from nearest to farthest, with gates, contact and light anchors and bans on common cheats. 30+ recipes for figures, objects and environments, a five-point checklist for reading results, and patches for long repeating chains. Adapted from the Foreshortening Recipe Book; example images at https://parallaxmetrology.com/foreshortening_recipe_book. No measurement involved.

## 0.1.0 — 2026-10-21

First release as a package. Ported from the research notebooks; outputs match them
on the sample images (see `tests/test_golden.py`).

- `vtl.measure`: kernel `canon3-v8` (Δx, Δy, rᵥ, ρᵣ, μ, xₚ, θ, dₛ, SDI) + mask QA
- `vtl.measure_color`: color/value kernel `color-v0.4.8`
- `vtl.measure_radial`: dual-center radial compliance `rca2-5.21`
- `vtl.fingerprint`, `vtl.rigidity`, `vtl.compare`: corpus readings from the Engine Fingerprint notebook
- `vtl` command line, four example notebooks, browser demo

Games in the browser demo: **Where's the weight?** (`docs/weight/`, your eye vs the lens vs a blind center tap) and **Lighter** (`docs/lighter/`, value judgment in public-domain paintings). Share-preview images for all three pages.

Agent skills (`skills/`): `vtl`, `vtl-color`, `vtl-radial`, `vtl-picture-this`, `measurement-claim-auditor`, distilled from the 2025 skill library and recalibrated to empirical reference ranges (`tools/reference_ranges.py`).

Deliberate differences from the notebooks:

- `diffusion=True` (Perona–Malik) uses κ = 0.12 on [0,1] luminance and mirrored borders. The notebooks' κ = 30 made it a plain blur that also wrapped image edges. The default kernel (diffusion off) is unchanged.
- Arrays passed to any `vtl` function are RGB (RGBA and gray accepted). PIL images are EXIF-corrected like files.
- `measure_many` writes `relpath` instead of absolute paths, and records unreadable files as `valid=0` with an `error` instead of stopping.
- `fingerprint` / `rigidity` / `compare` skip rows with mask QA `FAIL`. Rigidity's numerator is labeled `total_std`, which is what the notebook computed.
- RCA-2 labels an empty mask "No mass detected" instead of "radially ineligible".
