---
name: vtl
description: Measure the compositional structure of images with the Visual Thinking Lens (placement, void, cohesion, peripheral pull, dispersion, color/value, radial compliance) and read a folder of images as a fingerprint. Use when someone asks where the weight sits in an image, why generated images look samey or "default", how two engines or artists differ structurally, or wants composition numbers for a batch.
---

# Visual Thinking Lens

Deterministic measurement of image structure. No model in the loop: same image, same numbers.

## Setup (once)

```bash
pip install git+https://github.com/parallaxmetrology/visual-thinking-lens
```

## Measure

- One image: `vtl measure path/to/image.jpg` (JSON)
- With color and radial: `vtl measure image.jpg --color --radial`
- A folder: `vtl measure folder/ -o out.csv`
- Corpus fingerprint: `vtl fingerprint out.csv` (add `--mj-prompts` for MidJourney filenames to get prompt rigidity)
- Two sets: `vtl compare a.csv b.csv --labels A B`
- Visual check: `vtl overlay image.jpg` writes `image_vtl.png`. Look at it before trusting a surprising number.

## Read

Coordinates, not grades. Never call a value good or bad on its own.

| key | reads |
|---|---|
| `delta_x`, `delta_y` | mass centroid offset, −0.5…0.5; negative `delta_y` = UPPER frame |
| `r_v` | void ratio (absolute threshold); report with `gradient_floor_85` / `gradient_ceiling_97` |
| `rho_r` | packing density, mass ÷ convex hull ×100 |
| `mu` | cohesion: one body (→1) vs equal fragments (→0) |
| `x_p` | share of gradient energy in the outer 15% band |
| `theta` | orientation stability: one direction (→1) vs omnidirectional (→0) |
| `sdi` | dispersion from own centroid: ~0.1 tight, ~0.25 balanced, ~0.4 spread |

- **One image:** describe where mass sits and how it's organized. Note `mask_status`. WARN/TEXTURE_FIELD is normal for textured images; FAIL means don't interpret.
- **Many images:** the finding is the *distribution*. Use `window_width` (p90 − p10) and `walls` from `vtl fingerprint`. A narrow window across varied subjects suggests a learned default. Use window width, not CV, for `delta_x`/`delta_y`.
- **Radial:** `dRC` > 0 means rings follow the subject; < 0 means the frame center wins. Ignore `RC_s` when `E_s` < 0.38.

## Steering (only if asked to improve a composition)

Point at the coordinate, then suggest a concrete compositional move: e.g. Δx ≈ 0 across a batch → "place the subject in the left third, with open space to the right"; low `x_p` → "let forms crop at the frame edges"; very high `mu` with low `sdi` → "break the mass into two separated groups". Re-measure after regenerating, and report the change in numbers, not adjectives.

## Limits

The mask reads mid-strength structure (P85–P97 gradient band), not silhouettes. Flat vector art and crisp shapes on blank grounds can mislead; check the overlay. Details: `docs/known-issues.md` in the repository.
