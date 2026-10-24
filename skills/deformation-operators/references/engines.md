# Engines

Two families behave differently with deformation prompts.

| | GPT (ChatGPT image, gpt-image), Gemini | Midjourney, SDXL / OpenArt |
|---|---|---|
| default goal | follow the instruction literally | make a pleasing picture with correct anatomy |
| what goes wrong | over-literal reads; ignores numbers but honors words | snaps the limb back to normal, or turns "coil" into a rope around the arm |
| workflow | one prompt, refine in conversation | two steps: neutral base, then edit only the limb region |
| negatives | few, explicit | many, strong |

## GPT and Gemini (instruction-following)

These land most operators from text alone. Words carry more than numbers: GPT in particular often ignores the math in a capsule but honors the plain-language version, so write the distortion as clear anatomical sentences and keep the capsule for the person's own tuning.

- **Tone:** declarative and anatomical. "The arm itself", "the upper arm stays unchanged", "do not change the camera".
- **Structure:** binder → operator line(s) → one or two legibility cues (an overlap shadow, wrist-crease spacing, a highlight on the near edge).
- **Negatives:** minimal but explicit: no ropes or bands, no extra limbs, no text or watermarks.
- **Escalate in words:** "a little more", "slightly stronger near the wrist", "one clear overlap", "gentle", "gradual".
- **Work in conversation.** Ask for the image, then nudge from what came back; these engines keep the scene while you adjust one thing. A conversational model can also rewrite a capsule into engine-specific prose.

Follow-up template (same conversation):

> Keep this exact image, figure, pose, framing and style. Change only [the part]: [fix line]. Nothing else changes.

Mini-template:

> Charcoal study, soft diffused light, clothed figure in a neutral pose. The body itself deforms; continuous skin and believable volume. [Operator line]. [Legibility cue]. Do not change the camera. No props, no text.

## Midjourney and SDXL / OpenArt (aesthetic prior)

They can comply, but only with rails: an edit instead of a fresh generation, structure words instead of vibes, strong negatives, and (on SDXL) conditioning.

### Shared blocks

**Binder (positive):**
```text
charcoal drawing, soft diffused light, short-sleeved t-shirt and jeans, neutral pose, study on textured paper, realistic charcoal modeling, no text, no watermark
```

**Invariants (append to every edit):**
```text
the arm itself deforms (continuous flesh and bone); preserve thickness and topology; smooth C2 curvature continuity; overlap occlusion shading at self-crossings; not an added object
```

**Negatives** (MJ: after `--no`; SDXL: in the Negative Prompt box):
```text
rope, cord, wrapping, ribbon, scarf, vine, bracelet, bangle, armband, armor, prosthetic, robotic, segmented, tubes, rings, gaps, extra limbs, duplicate hands, broken anatomy, accordion folds, thin wrist collapse, gore, logo, watermark
```

"Segmented" is in the negatives to stop robotic, jointed-tube limbs, so keep the word out of every positive line (the Segmented Coil edit says "turning in stages" instead). Never put a word in both the prompt and the negatives. Drop a negative when the scene needs that thing elsewhere (no "vine" in a garden scene; say "no vine wrapped around the arm" in the prompt instead).

### Two-step workflow (every time)

1. **Base:** generate a neutral figure with binder + negatives.
2. **Edit:** select only the limb (Midjourney Vary (Region), SDXL inpaint). **Include the elbow and wrist in the mask** (on SDXL, feather it 8–16 px; Midjourney has no feather control, so select generously): if the mask is too tight the engine repairs instead of deforming. Paste invariants + one operator line.

### Midjourney

Turn on Remix. Keep `--style raw` to cut beautification and `--stylize` low.

```text
Step 1 (base)
charcoal drawing, soft diffused light, short-sleeved t-shirt and jeans, neutral pose, study on textured paper, realistic charcoal modeling, no text, no watermark --style raw --stylize 40 --chaos 0 --ar 2:3

Step 2 (Vary (Region) on elbow→wrist), one operator per run, e.g. Segmented Coil:
the left arm itself twists into a gentle coil from the elbow, turning in stages; about 0.9 turns with gentle amplitude; one clear self-overlap with occlusion shading; the coil IS the arm; <invariants block> --style raw --stylize 40 --chaos 0 --no <negatives block>
```

Knobs: `--stylize 25–50`, `--chaos 0`. If it repairs, select a slightly larger region and repeat. Midjourney is the weakest at region edits; expect more rerolls.

### SDXL / OpenArt

Settings: any modern 2M Karras-type sampler, CFG 5.5–6.5, 28–36 steps, 768×1152 or 896×1344. Inpaint denoise 0.35–0.45. If available, Lineart or Depth ControlNet from the base at weight 0.25–0.35 keeps anatomy while allowing the warp; even a crude depth map of the intended curve helps.

### Edit lines for the second step

| operator | edit line | extra negatives |
|---|---|---|
| 0 Segmented Coil | the left arm itself twists into a gentle coil from the elbow, turning in stages; about 0.9 turns; continuous flesh and bone; preserve thickness and topology; one visible self-overlap with occlusion shading; the coil IS the arm itself | rope, cord, wrapping, bracelet, armband, rings |
| 1 Vector Extension | the left arm itself lengthens from the elbow along a forward-right line, nearly double its reach; forearm and hand keep the same thickness and size; continuous flesh and bone | swollen arm, giant hand, stretched hand |
| 2 Logarithmic Scaling | the neck itself lengthens gradually, more near the collar and less near the head; width proportional; head size, jaw and shoulders unchanged | giraffe neck, pinched neck, small head |
| 3 Rotational Transform | upper arm fixed, elbow angle unchanged; the forearm rolls in place so the palm turns toward the torso; spiral skin folds near the elbow | bent arm, broken wrist |
| 4 Fibonacci Coil | apply a Fibonacci spiral torsion to the left arm centered at the shoulder; about 1.1 turns with golden-ratio growth (tight near shoulder, opens toward forearm); continuous flesh and bone; preserve thickness; clear self-overlap; the spiral is the arm's own mass | rope, cord, wrapping, armor, rings |
| 5 Parabolic Extension | graceful parabolic extension along the shoulder-to-wrist axis, vertex locked at the elbow; one smooth arc with the elbow as its crest; preserve thickness; subtle inner-curve occlusion shading; avoid ballooning | crease seam, rubber hose |
| 6 Depth Tug | localized non-linear depth pull on the left forearm toward a vanishing point to the right; inverse-square falloff centered mid-forearm; preserve wrist thickness and edge fullness; subtle compression at wrist and knuckles | accordion folds, thin wrist collapse |
| 7 Sine Modulation | one gentle serpentine wave runs through the existing left arm from elbow to hand; elbow and wrist anchored; the limb's mass follows the wave; single continuous arm | extra arm, branching limb, duplicate hands |
| 8 Viewfinder | same geometry as previous frame; push subject toward the left edge; enlarge right-side negative space; slight zoom-in; no new geometric deformation | (MJ: Zoom Out / Pan, or regenerate in Remix) |

### When it still won't comply

- **Draws hardware** (bracelets, armor, rings): add "torsion folds in the skin follow the spiral; no seams; no gaps; single continuous sleeve of skin; the effect is an optical anatomical distortion, not an added object."
- **Repairs to normal anatomy:** expand the mask to include elbow and wrist; lower CFG by about 1 (or stylize, on MJ); denoise near 0.4; reduce amplitude and add turns; use "smooth, continuous curve" wording.
- **Sausage bulges:** "lower amplitude, more turns, wider falloff, C2 continuity."
- **Depth tug looks like a normal pose:** shrink the field radius, raise the magnitude, add "converges toward a vanishing point on the right; compressed wrist creases."

Some platforms treat strong body deformation as low quality or unsafe and push back by design. Tell the person when an engine is the obstacle; switching to GPT or Gemini is often faster than escalating tricks.
