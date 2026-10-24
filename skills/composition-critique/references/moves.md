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

## Recomposition (when the person can reshoot or regenerate)

Crops only rearrange what is already in the frame. When the picture is AI-generated, or the scene can be shot again, bigger moves are on the table. Describe the move in words the person can act on (a shot change or a prompt change), name the signature you expect, and measure the new version with `--compare`.

The signatures below come from 16 before/after pairs made by this project's author, measured with `scripts/move_signatures.py` (full report: `move-signatures-example.md`). Counts describe those pairs, mostly one or a few per move; treat them as expectations to check, not rules.

| move | pairs | signature observed |
|---|---|---|
| Shrink the subject, move it off-center, give it open space | 4 | farther from center 4/4; edge energy up 4/4; light gathered into fewer places 4/4 (median +0.38); color more focused 3/4; spread down 3/4; contrast down 3/4 |
| Add a foreground anchor (rocks, ground, a near object) | 1 | mass drops (Δy 0.03 → 0.10); edge energy jumps (x_p 0.33 → 0.53); one block becomes many pieces (μ 0.15 → 0.05); lights pushed above darks |
| Change viewpoint to add a leading curve (a shoreline, a path) | 1 | like a foreground anchor, plus color gathers (chroma focality 0.22 → 0.54) |
| Move closer to the subject (portrait) | 1 | less quiet field; mass rises toward the face; contrast up; color gathers on the face (focality 0.46 → 0.98) |
| Add atmosphere behind the subject (fog, haze, bright sky) | 1 | lights go high and gather (light-over-dark +0.11 → +0.51); the subject stops dominating the field statistics (μ 0.25 → 0.003, background becomes texture) |
| Simplify and blur the background, light from one side | 1 | one dominant body (μ 0.14 → 0.38); light gathers on the lit side; darks settle low |
| Restage (new light, pose, setting) | 1 | busier frame (r_v 0.74 → 0.57); contrast nearly doubled; lights above darks; color less focused |
| Change the gesture (a body in action instead of standing) | 2 | busier field 2/2 (r_v about −0.10); mass more gathered 2/2; lighter with more contrast 2/2; lights above darks 2/2; color more focused 2/2; θ unchanged in both, so the instrument doesn't see gesture as direction |
| Split the frame into light and dark (a dark doorway against a warm sky) | 1 | color gathers sharply (chroma focality 0.45 → 0.96); edge energy down |
| Simplify the light (one soft gradient instead of a busy light pattern) | 1 | color spreads (focality 0.79 → 0.29); lights move above darks |
| Pull one element away as a separated accent (a lone balloon) | 1 | one dominant body splits in two (μ 0.61 → 0.10); mass rises; edge energy down; color gathers |
| Shift the mood (muted color, storm sky, weathering) | 1 | one dominant body again (μ 0.10 → 0.43); mass sinks; edge energy up; lights back above darks |
| Add a diagonal (a leaning post, crossing stems, a receding stair) | 3 | **not reliably measured**: θ fell in two and rose in one. θ reads how strongly one direction dominates, not tilt. Judge diagonals by eye |

Across all 16 pairs, lights moved further above darks in 11 and edge energy rose in 11; those two are the most common side effects of recomposing in this set, so check them whatever the move. Recomposing changes many things at once, so a measured change can't be pinned on one ingredient. Report the overall signature and whether it moved toward the stated intent.

To calibrate on your own work, list before/after pairs with a move label in a CSV and run `python scripts/move_signatures.py pairs.csv`.

## What none of these measure

- **Where a viewer actually looks.** No gaze or attention is measured. Say "light and contrast gather at X", not "the eye goes to X".
- **What the subject is or why it matters.** You can see that yourself; label it as your observation, separate from the numbers.
- **Whether it's good.** Conventions (rule of thirds, lights above darks, odd numbers) are conventions. Offer them as options that serve the stated intent, never as rules.
