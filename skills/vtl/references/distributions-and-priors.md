# Distributions and priors

## Order of operations

1. **Comparability:** same kernel version, same machine, same `diffusion` setting, similar native resolutions, QA separated.
2. **Shape before names:** per group, give the median and window (`p10–p90`, `window_width`), plus spread, clusters, outliers and the mask-mode mix.
3. **Only then** consider a named prior, at the weakest status that fits.

Sample-size guide: n < 5 means not enough data; n < 20 supports a candidate at most; n ≥ 50 can support a stable description.

## Status ladder (use the weakest that fits)

- **Invalid comparison:** settings differ, QA not separated, groups not comparable.
- **Not enough data:** too few comparable rows.
- **No prior evidence:** metrics move with content or prompt as expected; no stable low-variance axis.
- **Candidate prior:** a recurring tendency on a named axis; limited n or diversity.
- **Likely distributional prior:** the tendency persists across prompts or seeds where variation was expected, with QA and mode accounted for.
- **Collapse signature:** variance compresses on a named, meaningful axis, and recurs across a comparable cohort. Low variance alone isn't enough: name the axis and say why it matters.

## Pattern catalogue

| pattern | evidence | common confounds |
|---|---|---|
| center prior | Δx, Δy windows narrow around 0; recurs across prompts | small n; subject-matched sets centered on purpose |
| one-body center | centered **and** μ high, SDI low | a single centered subject asked for by the prompt |
| balanced center | centered **and** μ low, SDI high | not a collapse: masses offset each other |
| quiet-field | r_v high, floor low, recurs | low-detail inputs; minimal prompts; denoising |
| activated-field | r_v low, floor high | detail-heavy prompts; textured subjects |
| edge/frame | xₚ high, recurs | borders, crops, watermarks, frames in reproductions |
| fragmentation | μ low, many components, TEXTURE_FIELD | crowds, foliage, fine texture |
| flat rendering | tail_gap low | low-contrast sources; flat styles |
| isolated edges | tail_gap high | line art, silhouettes, product shots |

## Center collapse, carefully

Requires: (a) centroid near center, (b) SDI low **relative to a comparable baseline or cohort**, (c) concentration (μ or largest-component share), and (d) no contradiction from spread (high SDI, high xₚ).

- Single image: at most "center-weighted" or "center-collapse candidate".
- Cohort: "center-collapse pattern" only with recurrence and low centroid variance.
- If the centroid is off-center, it's off-center dominance, not center collapse.
- If μ is low and SDI high, it's balanced center (see the pattern catalogue).

## Prompt rigidity

`vtl.rigidity(df, group)` = total std ÷ mean within-prompt std. About 1 means prompts move structure no more than re-rolls do; above 2.5 means prompts drive structure. It needs several images per prompt.

## Always report

Group sizes; dropped rows; mask-mode mix; `kernel_version`; platform; what the result doesn't show (intent, quality, semantic fidelity).
