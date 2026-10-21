# Metrics

All instruments are deterministic: no randomness, no learned parameters, fixed constants. Same image in, same numbers out.

## Kernel (`vtl.measure`, version `canon3-v8`)

**Pipeline:** decode (OpenCV) → resize so the long side is 1536 px (INTER_AREA down, INTER_CUBIC up) → grayscale [0,1] → Sobel 3×3 gradient → **mass mask** → metrics.

**Mass mask.** Pixels whose gradient magnitude lies between the image's own 85th and 97th percentiles (a 2 px border is excluded). Percentiles make the mask insensitive to global contrast. The band deliberately excludes the strongest 3% of edges so that a few very hard boundaries don't dominate. The mask therefore represents *mid-strength structure* (texture, marks, modelling), not silhouettes. See [known-issues.md](known-issues.md).

| key | definition | range |
|---|---|---|
| `delta_x` | (mean x of mask − frame center x) / width | −0.5…0.5, + = right |
| `delta_y` | (mean y of mask − frame center y) / height | −0.5…0.5, + = **lower** |
| `r_v` | 1 − share of pixels with gradient ≥ 0.15 (absolute threshold, *not* percentile) | 0…1 |
| `rho_r` | 100 × mask area / convex-hull area of mask | 0…100 |
| `mu` | p_max × (1 − H/H_max) over 8-connected component sizes | 0…1 |
| `x_p` | Σ gradient in outer 15% band / Σ gradient | 0…1 |
| `theta` | 1 − H/H_max of the magnitude-weighted 8-bin orientation histogram on the mask | 0…1 |
| `d_s` | mean of 2 × distance-transform along the mask skeleton / min(h, w) | ~0…0.05 |
| `sdi` | mean distance of mask pixels from their centroid / image diagonal | possible ~0.1…0.45; real images mostly 0.19–0.29 |

Diagnostics also returned: `mass_fraction`, `gradient_floor_85`, `gradient_ceiling_97` (report these with `r_v`: a drop in `r_v` can come from global edge activation rather than packing), `valid`, `quality_note`.

**Optional preprocessing.** `diffusion=True` applies Perona–Malik anisotropic diffusion (10 iterations, κ = 0.12 on [0,1] luminance, γ = 0.1, mirrored borders) before the gradient. It smooths noise inside regions and keeps edges. Use it for JPEG-heavy, grainy, scanned or re-saved images; leave it off for clean exports and any baseline that must match earlier CSVs. This deliberately differs from the Canon 3 notebook (see [known-issues](known-issues.md) #7).

### Mask QA (`vtl.mask_qa`)

`mask_status` PASS / WARN / FAIL, with `mask_reasons`; `n_components` (4-connected); `largest_component_fraction`; `mask_sha256` for regression checks; `mask_mode` (REGION_FIELD if the largest component holds ≥ 25% of mass, TEXTURE_FIELD otherwise, INVALID on FAIL); `structure_regime` (region / hybrid / texture).

## Color & value (`vtl.measure_color`, version `color-v0.4.8`)

Decoded with Pillow (EXIF-corrected), downscaled to ≤1536 px with Lanczos, converted to OKLab.

- **Lightness:** `okl_L_mean`, `okl_L_std`, `okl_L_p05`, `okl_L_p95`, `lightness_contrast_p95_p05`
- **Absolute value bands:** `high_key_fraction` (L ≥ 0.72), `deep_dark_fraction` (L ≤ 0.35), `midtone_fraction`
- **Relative light/dark regions** (top and bottom 15% of this image's L): `light_mass_fraction`, `dark_mass_fraction`, their centroids `light_delta_x/y` and `dark_delta_x/y`, dispersion `light_sdi`, `dark_sdi`, and `spotlight_concentration` / `shadow_concentration` (largest connected share)
- **Chroma:** `okc_C_mean`, `okc_C_std`, `okc_C_p85`, `chroma_entropy`, `color_sdi`, `chroma_delta_x/y`, `chroma_focality`
- **Hue:** `hue_entropy` (36 bins, chroma-weighted, ignores C < 0.02), `dominant_hue_occupancy` (12 bins)
- **Palette:** deterministic k = 5 k-means in OKLab. `palette_i_{weight, okl_L, okl_a, okl_b, hex}`, `palette_compression` (largest weight), `effective_palette_count` (1/Σw²)

## Radial compliance (`vtl.measure_radial`, version `rca2-5.21`)

Native resolution. The mask is a hybrid of edges and Otsu, closed and opened, keeping the largest component. In `subject` mode (the default) it is border-penalized and narrowed to the most compact, central component.

Radial mass profiles (60 bins, radius normalized to the farthest corner) are taken around the **frame center** and around the **mass centroid**, and each is compared with its best-fitting exponential decay:

- `RC_f`, `RC_s` = 1 − Jensen–Shannon distance (frame / subject centered); `alpha_f`, `alpha_s` are the decay rates
- `dRC` = RC_s − RC_f: positive means rings follow the subject, negative means the frame center wins
- `dx`, `dy`, `dr`: mass centroid offset from frame center
- `E_s` eligibility = 0.35·(1 − angular variance) + 0.35·isotropy + 0.30·compactness. Below 0.38, don't interpret RC_s.
- `radial_label`: one of six descriptive categories
- `default_prior`: the RDC gate (E_s ≥ 0.55, dr ≤ 0.12, RC_f ≥ 0.70, dRC ≤ 0.03). True means "reads as a center-default composition".

## Corpus (`vtl.fingerprint`, `vtl.rigidity`, `vtl.compare`)

Per metric across a set of images:

- `mean`, `std`, `cv` = std/|mean| → `spread` (tight < 0.15 < moderate < 0.30 < wide). Signed offsets (Δx, Δy, centroid offsets, dRC) get no CV and `spread = signed: see window`.
- `p10`, `p50`, `p90`, `window_width` = p90 − p10 (the operating window)
- `wall_hardness` = std/range → `walls` (hard < 0.15, soft > 0.30)
- `skew`, `kurtosis` (Pearson), `bimodal` = kurtosis < 2 and |skew| < 0.8

`rigidity(df, group)`: std across all grouped images / mean within-group std, per metric, plus the median overall (as in the Fingerprint notebook). About 1 means re-rolls of one prompt vary as much as different prompts do. Above 2.5, prompts drive structure.

`fingerprint`, `rigidity` and `compare` drop rows with `valid = 0` or `mask_status = FAIL` before computing.

`compare(a, b)`: means, CVs, Cohen's d and the overlap of the two operating windows.
