---
name: vtl
description: Measure and read the compositional structure of images with the Visual Thinking Lens kernel (placement, void, packing, cohesion, peripheral pull, orientation, thickness, dispersion), check run quality, and read a folder of images as a fingerprint. Use when someone asks where the weight sits in an image, why generated images look samey or default, whether a set shows a center or other structural prior, how two engines, prompt sets or artists differ structurally, or wants composition numbers for one image or a batch.
---

# Visual Thinking Lens

Deterministic measurement of image structure: no model in the loop, same image and machine, same numbers. The kernel locates an image in structural space. It does not grade it.

```text
kernel values locate structure; they do not grade it.
one image is a coordinate; a pattern needs a comparable set.
```

## Setup

```bash
pip install git+https://github.com/parallaxmetrology/visual-thinking-lens
```

## Measure

| task | command |
|---|---|
| one image | `vtl measure image.jpg` (JSON) |
| a folder | `vtl measure folder/ -o out.csv` |
| add color / radial | `--color`, `--radial` |
| corpus fingerprint | `vtl fingerprint out.csv` (add `--mj-prompts` or `--group-by COLUMN` for rigidity) |
| two sets | `vtl compare a.csv b.csv --labels A B` |
| visual check | `vtl overlay image.jpg` → `image_vtl.png` |

Look at the overlay before trusting a surprising number. Gold is what was measured.

## Workflow

1. **Gate on QA first** (see [qa-and-reproducibility.md](references/qa-and-reproducibility.md)).
   - `valid = 0` or `mask_status = FAIL`: report the failure, interpret nothing else.
   - `WARN`: read, but name the reason (`mask_reasons`).
   - `mask_mode = TEXTURE_FIELD` is normal (about 97% of real images). Placement and dispersion still apply, but describe the structural field, not an object.
2. **Read one image descriptively**, metric group by metric group (see [metric-guide.md](references/metric-guide.md)):
   placement (Δx, Δy) · field activity (r_v with the gradient package) · packing and cohesion (ρᵣ, μ) · edge, orientation, thickness (xₚ, θ, dₛ) · dispersion (SDI).
   Place each value against [reference-ranges.md](references/reference-ranges.md) ("upper quartile of the reference set"). Don't use absolute cutoffs.
3. **Centered is not a finding.** A centered centroid can mean one body in the middle or masses balancing across it. Separate them with μ and SDI, and radial compliance if available. The kernel does not detect counterbalance directly.
4. **For a set, read distributions** (see [distributions-and-priors.md](references/distributions-and-priors.md)): describe shape before naming any prior; use `window_width` for Δx/Δy; use the weakest status that fits.
5. **State limits**: what the numbers don't show (quality, intent, meaning, subject), sample size, reproduction chain, platform.

## Output for one image

```text
VTL read: <one-sentence structural summary>
QA: valid, mask_status (+ reasons), mask_mode
Placement: Δx, Δy, and where they sit in the reference
Field: r_v with gradient_floor_85 / gradient_ceiling_97 / tail_gap
Packing & cohesion: ρᵣ, μ
Edge / orientation / thickness: xₚ, θ, dₛ
Dispersion: SDI
Limits: single image; no quality, intent or prior claims
```

## Hard stops

- No quality, beauty, success or failure language from kernel values.
- No prior, collapse or monoculture claim from one image or from a non-comparable set.
- Don't read `r_v` as "empty space" without the gradient package.
- Don't fold several metrics into one vague label ("complex", "dynamic").
- Don't compare numbers across `kernel_version`s, `diffusion` settings, or (for exact matching) different CPU platforms without saying so.
- The kernel reads mid-strength structure (85th–97th percentile gradients). Crisp flat shapes on blank grounds can mislead; check the overlay.

## Related skills

`measurement-claim-auditor` before publishing any claim · `vtl-color` for value and color · `vtl-radial` for frame- vs subject-centered organization · `vtl-picture-this` to translate a reading into felt compositional language.
