---
name: vtl-radial
description: Measure and read radial organization with RCA-2 (dual-center radial compliance): whether an image's mass falls off in rings around the frame center or around its own mass centroid, gated by whether the mass is round and compact enough for that question to mean anything. Use when someone asks if a composition is organized around the center, whether centering comes from the frame or from the subject, or wants to separate a center default from a subject-driven layout.
---

# VTL Radial (RCA-2)

One question: **where does radial structure exist, and around which center?** RCA-2 compares two anchors: the frame center (a global default basin) and the mass centroid (the subject organizing the frame). It doesn't identify subjects, attention or intent.

```text
Subject location is not the same as radial organization.
```

## Measure

```bash
vtl measure image.jpg --radial          # adds radial_* fields
```

In Python: `vtl.measure_radial("image.jpg")`, or `return_fields=True` for the profiles.

## Fields

| key | meaning |
|---|---|
| `RC_f`, `RC_s` | radial compliance (1 − Jensen–Shannon distance to the best exponential falloff) around the frame center and around the mass centroid |
| `dRC` | `RC_s − RC_f`: > 0 rings follow the subject; < 0 the frame center wins |
| `dx`, `dy`, `dr` | mass centroid offset from frame center (negative dy = upper) |
| `E_s` | eligibility: 0.35·(1 − angular variance) + 0.35·isotropy + 0.30·compactness |
| `radial_label` | the instrument's own classification (below) |
| `default_prior` | RDC gate: True when it reads as a center-default composition |
| `void_ratio` | share of the frame outside the RCA-2 mask (a different mask from the kernel's) |

## Workflow

1. **Eligibility gate.** If `E_s` < 0.38 or `radially_ineligible`, don't interpret `RC_s`. Report the mask as not round or compact enough. "No mass detected" means nothing to read.
2. **Use `radial_label` as the classification:** field-dominant collapse (frame wins), subject-dominant (rings follow mass), dual-center/near-tie, vignette/gradient with a sparse subject, or weak/unclear.
3. **Read the two centers together.** When `dRC ≈ 0`: if `dr` is small, the two centers coincide (subject sits at center) and the tie means little. If `dr` is large and both RCs are clearly present, the image has two competing attractors.
4. **`default_prior`.** True means this image is a plausible member of a center-default set. False is not "good", only "not a default-prior case". Reasons are in `default_prior_reasons`.
5. **For sets:** compare the share of `default_prior` = True and the distribution of `dRC` across comparable groups. One image is never a prior.

## Boundaries

- RCA-2 uses its own mask (edges + Otsu, subject mode, native resolution). Its `dx` is not the kernel's `delta_x`. Name the instrument when you quote a number.
- Radial compliance describes falloff shape, not importance or attention.
- A centered subject with strong frame rings can be a deliberate choice. The diagnostic signal is in a set that does this regardless of prompt.
