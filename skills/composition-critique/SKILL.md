---
name: composition-critique
description: Give grounded composition feedback on a photo, painting, drawing, illustration, design or AI-generated image, using the Visual Thinking Lens instruments (where visual mass and light actually sit, how open or crowded the frame is, value grouping, color focus) instead of opinion, and propose concrete changes (crops, value shifts, where to add or remove weight) whose effect is measured. Use whenever someone shares an image and asks what's working, how to improve it, where to crop, why it feels off, whether it's balanced, how to make it calmer or more dramatic, or how to lead attention to a subject, even if they don't mention composition, VTL or measurement.
---

# Composition critique

A critique a person can act on, backed by an instrument. The VTL kernel measures where structure and light sit in the frame; you look at the picture yourself and know what's in it. Put the two together, and only suggest changes whose effect you can name and check.

```text
measure first, then interpret, and keep the two visibly apart.
judge against the person's intent, not against a rulebook.
every suggested move names the reading it should change; crops are measured before you recommend them.
```

## 1. Get the image and the intent

Ask one short question if the intent isn't clear: *what should the picture feel like, and where should attention land?* (Calm, tense, intimate, grand; "the figure", "the light on the water".) If the person doesn't want to say, critique against what the picture already seems to attempt, and say that's what you did.

## 2. Measure

```bash
pip install git+https://github.com/parallaxmetrology/visual-thinking-lens   # once
python scripts/critique.py IMAGE --out IMAGE_critique
```

This writes `critique.json` (all readings, reference percentiles, numbered facts, measured crops), `overlay.png` (measured mass in gold, frame center cross, mass centroid dot), `values.png` (three value bands, a notan check) and `crops.png` (each crop candidate with its own measured centroid). It takes a few seconds.

- **Gate on QA.** If `qa.mask_status` is `FAIL` or `kernel.valid` is 0, say the instrument couldn't read the image and give only a visual critique, clearly labeled as unmeasured. `TEXTURE_FIELD` is normal for most real images: describe a structural field, not an object.
- **Look at the image, the overlay and the value map yourself.** Check that the gold mass covers what you'd expect. If the measurement and your eye disagree (crisp flat shapes on blank grounds can fool the kernel), trust what you can see, and say why.

## 3. Read it

Use the `facts` list as your measured base: each one carries its number and where it sits among 279 reference images (museum reproductions and AI images; a yardstick, not a norm). For what a placement or spread tends to *feel* like, use `../vtl-picture-this/references/bang-mapping.md`, and label that layer as interpretation.

Combine before concluding. A centered centroid can be one body held in the middle (high μ, low SDI) or masses balancing across the frame (low μ, high SDI): same number, different picture. Value often outweighs mass: a small dark shape can carry more weight than a large pale one.

## 4. Suggest moves

Pick two to four moves that serve the stated intent, using `references/moves.md` to name what each should change. For framing, choose from the measured `crops` and quote their actual numbers ("trimming 15% off the right moves the mass from +5% to +12% right of center"). Show `crops.png` when a crop is part of the advice. Don't promise a crop does something its measurement doesn't show.

Look at `crops.png` before recommending any crop. The candidates are placed from measured mass alone, which knows nothing about meaning: in a mountain-lake picture the mass can sit on the shoreline, and an "aimed at a thirds point" crop will happily cut off the peaks. Reject any crop that loses the subject or something the intent depends on, and say why if it looked attractive in the numbers.

For value, weight and color moves, the person has to make the change. Say what you expect to move, and offer to check it: `python scripts/critique.py ORIGINAL --compare EDITED` reports before, after and change for each reading.

## Output

```text
**What the picture is doing** (measured)
- 3–5 points, each with its number and reference position, in plain words.

**Against what you're after** (interpretation)
- How those facts serve or work against the stated intent. Your own observations of content go here, marked as yours.

**Try this**
1. Move — what it should change — evidence (measured crop numbers, or "check with --compare").
2. …

**What this can't tell you**
- One line: no gaze or attention measured, no quality grade, single image.
```

Attach or show `overlay.png`, `values.png` and, when used, `crops.png`.

## Keep it honest

- **No grades.** Not "good composition" or "weak composition"; say what it does and whether that serves the intent. Centered is a valid choice.
- **No attention claims.** Say "light and contrast gather on the face", not "the eye goes to the face". Nothing here tracks gaze.
- **No defaults from one image.** Words like *collapse*, *prior* or *AI default* need a comparable set of images (the `vtl` skill handles sets).
- **Conventions are options.** Rule of thirds, lights above darks and the like are tools to reach an intent, not laws.
- **Color has no reference set here.** Read color and value in their own units (OKLab lightness 0–1) and relative to the image itself.

## Example

> **What the picture is doing**
> - The mass sits a little high and right of center (6% right, 12% up: higher than 95% of the reference set). With low spread (SDI 0.19, ~p7) it reads as one gathered body, the head and shoulders.
> - The frame is mostly quiet (r_v 0.94, above p95), and little edge energy reaches the frame (x_p 0.37, ~p18).
> - Low key: lights high and right, darks low and left, so light sits above dark.
>
> **Against what you're after** (*an intimate, direct portrait*): the quiet frame and gathered mass support intimacy. My own read: the face is the lightest large shape, so contrast already gathers there.
>
> **Try this**
> 1. Trim 15% off the bottom: the mass moves from 11% to 5% above center and fills more of the frame (measured). Closer and more direct.
> 2. Darken the lower-left shirt area slightly to group the darks into one shape: light concentration should rise. Check with `--compare`.
>
> **What this can't tell you:** where people actually look, or whether it's good; this is one image.

## Related skills

`vtl` (sets, priors, QA details) · `vtl-color` · `vtl-radial` · `vtl-picture-this` (felt language) · `measurement-claim-auditor` (before publishing claims drawn from these numbers).
