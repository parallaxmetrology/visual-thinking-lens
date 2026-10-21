---
name: vtl-color
description: Measure and read an image's value and color structure with the VTL color kernel (OKLab lightness and chroma, value bands, where light, dark and chroma sit in the frame, hue breadth, and a deterministic five-color palette). Use when someone asks about value structure, light and dark placement, palette, chroma, hue range, or how color behaves across a set of images or paintings, including comparing AI and human-made work.
---

# VTL Color

Color and value as field behavior: how much light and dark there is, where it sits, how concentrated it is, and how wide the hue range runs. These are coordinates, not harmony grades.

## Measure

```bash
pip install git+https://github.com/parallaxmetrology/visual-thinking-lens
vtl measure image.jpg --color          # adds color_* fields
vtl measure folder/ -o out.csv --color
```

In Python: `vtl.measure_color("image.jpg")` (keys without the `color_` prefix).

## What the fields mean

| group | keys | reading |
|---|---|---|
| value overall | `okl_L_mean`, `okl_L_std`, `okl_L_p05`, `okl_L_p95`, `lightness_contrast_p95_p05` | key and value range (OKLab L, 0–1) |
| value bands (absolute) | `high_key_fraction` (L ≥ 0.72), `deep_dark_fraction` (L ≤ 0.35), `midtone_fraction` | how much of the frame is genuinely light, dark or middle |
| light & dark placement | `light_delta_x/y`, `dark_delta_x/y` | centroids of the lightest and darkest 15% of *this* image; negative y = upper |
| light & dark gathering | `light_sdi`, `dark_sdi`, `spotlight_concentration`, `shadow_concentration` | spread of each, and how much of it is one connected region |
| chroma | `okc_C_mean`, `okc_C_std`, `okc_C_p85`, `chroma_entropy` | colorfulness and how evenly it is distributed |
| chroma placement | `chroma_delta_x/y`, `color_sdi`, `chroma_focality` | where the most saturated 15% sits and whether it's one patch |
| hue | `hue_entropy` (36 bins, chroma-weighted, ignores near-neutrals), `dominant_hue_occupancy` | hue breadth; share of the dominant hue family |
| palette | `palette_1..5_{hex, weight, okl_L, okl_a, okl_b}`, `palette_compression`, `effective_palette_count` | five deterministic OKLab clusters, largest first; 1/Σw² = how many colors really carry the image |

## Workflow

1. **Value first.** Key, range, and where light sits relative to dark (`light_delta_y` vs `dark_delta_y`: light above dark is the sky-over-ground and lit-face arrangement).
2. **Concentration.** Is the light one spotlight or scattered? (`spotlight_concentration`, `light_sdi`.) Same for shadow.
3. **Chroma as mass.** How much, where, and whether it's a focal patch or an atmosphere (`chroma_focality`, `color_sdi`).
4. **Hue breadth and palette.** Read hue entropy as breadth, not quality. Read hex values as approximate display colors, not pigment claims.
5. **Relate to structure** if the kernel was run too: does the light or chroma sit where the structural mass is?
6. **Limits:** one image is a coordinate; reproductions shift color (camera, white balance, compression); screen color isn't pigment.

## Output skeleton

```text
Value: key, range, light vs dark placement
Light & shadow: concentration and spread
Chroma: amount, placement, focal vs atmospheric
Hue & palette: breadth, effective color count, main hexes
With structure (optional): agreement or counterpoint
Limits
```

## Boundaries

- No harmony verdicts ("complementary, so it works"). Describe the measured roles.
- Light/dark masks are relative to each image (top/bottom 15% of its own range). Use the absolute value bands to compare how light or dark images actually are.
- Color-structure coupling, salience and regime tags exist in the research notebook but aren't in the package yet. Don't cite them.
