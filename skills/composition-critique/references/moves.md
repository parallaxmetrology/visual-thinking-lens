# Moves and what they measurably change

A move is only worth suggesting if you can say which reading it should shift and in which direction, so the result can be checked. The left column is the painter's or photographer's action; the right columns are what the kernel or color reading should do if the move works. "Feels" language comes from `skills/vtl-picture-this/references/bang-mapping.md` and is interpretation, so label it that way.

## Framing (verifiable now: the script measures crops)

| move | expected change | check in `crops` |
|---|---|---|
| Trim the side the mass leans away from | centroid moves further off-center toward the remaining edge; Δx magnitude grows | `change.delta_x` has the predicted sign |
| Trim the side the mass leans toward | centroid moves toward center; calmer placement | `change.delta_x` shrinks toward 0 |
| Trim the top | mass sits relatively higher in the new frame (Δy goes more negative) | `change.delta_y` < 0 |
| Trim the bottom | mass sits relatively lower (Δy goes more positive), more grounded | `change.delta_y` > 0 |
| Tighten all round | less quiet field (r_v down), more edge energy (x_p up) | `change.r_v` < 0, `change.x_p` > 0 |
| Aspect crop aimed at a thirds point | centroid moves off-center by roughly a sixth of the frame | read the measured Δx/Δy: crops rarely land exactly, because cropping changes where the mass is |

Report the measured numbers, not the label. If a crop didn't do what its name says, say so; that's the point of measuring it.

## Value (verify with `--compare` after the person edits)

| move | expected change |
|---|---|
| Group values into fewer, larger shapes (simplify the middle) | values map shows bigger connected bands; `spotlight_concentration` / `shadow_concentration` rise |
| Darken the corners or edges | light concentration rises; light centroid moves toward the area kept light |
| Lighten or darken the main subject against its surround | larger local contrast where the subject is; light or dark centroid moves toward it |
| Put lights above darks (sky over ground) or reverse it | sign of `light_delta_y − dark_delta_y`: negative = lights above |
| Raise or lower the key overall | `okl_L_mean` up or down; contrast range (`lightness_contrast_p95_p05`) widens or narrows |

## Weight and structure (verify with `--compare`)

| move | expected change |
|---|---|
| Add a counterweight (texture, dark shape or detail) on the empty side | centroid moves back toward center; SDI rises (mass spread across the frame) |
| Remove clutter or texture from the background | r_v rises (more quiet field); μ rises if one body remains |
| Merge small scattered shapes into one | μ rises; SDI falls |
| Bring a shape to, or off, the frame edge | x_p rises or falls |
| Add one strong directional line (a diagonal, a road, a limb) | θ rises (compare relatively; it is small for most images) |

## Color

| move | expected change |
|---|---|
| Concentrate saturated color on the subject, neutralize elsewhere | `chroma_focality` rises; chroma centroid moves toward the subject |
| Narrow the palette | `effective_palette_count` and `hue_entropy` fall |

## What none of these measure

- **Where a viewer actually looks.** No gaze or attention is measured. Say "light and contrast gather at X", not "the eye goes to X".
- **What the subject is or why it matters.** You can see that yourself; label it as your observation, separate from the numbers.
- **Whether it's good.** Conventions (rule of thirds, lights above darks, odd numbers) are conventions. Offer them as options that serve the stated intent, never as rules.
