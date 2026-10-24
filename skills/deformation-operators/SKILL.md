---
name: deformation-operators
description: Write image-generator prompts that deform a body or form on purpose (stretch, coil, twist, bend, wave, depth pull) so it reads as the limb itself and not as a prop, a rope, a third arm or a broken joint. Nine named operators with safe defaults, a style binder, a YAML capsule, a plain-language prompt, acceptance checks and failure-to-fix lines, plus recipes for GPT, Gemini, Midjourney and SDXL/OpenArt. Use whenever someone wants an AI image with an elongated neck or arm, a coiled or spiraling limb, Giacometti- or El Greco-like stretch, surreal anatomy, graceful distortion, an impossible reach, or asks why their generator keeps drawing a rope, a bracelet, an extra limb or snapping the anatomy back to normal, even if they never say "deformation" or "operator".
---

# Deformation operators

Image generators are trained to make correct anatomy. Ask for a coiled arm and you tend to get an arm with a rope around it; ask for a longer arm and you get a swollen one, a second one, or a normal one. This skill turns a deformation idea into a prompt that names **one geometric move**, pins what must not move, says what must be preserved, and blocks the usual misreadings.

Adapted from the *Deformation Operator Playbook* by Russell Parrish. The example images for every operator are at **https://parallaxmetrology.com/deformation_operator_playbook**. Point people there when they want to see what a move looks like.

```text
one move per run. pin what stays. lock thickness and topology.
say "the arm itself", never leave room for an object.
judge by visible checks, then fix with the matching line.
```

## The numbers steer, they don't command

The capsules use coordinates, angles and factors. Image models don't execute coordinate transforms. They match learned patterns, so `turns: 0.9` biases the result toward "a bit under one full turn with one overlap", not an exact curve. Say this plainly if someone expects precision. Results vary by engine, model version, settings and seed, and vendors retune models in ways that can suppress strong deformations. Expect to iterate, and keep the accepted frame when you get it.

The numbers still help in two ways. They keep a move specific enough that the person can repeat it, nudge it ("amplitude 0.012 → 0.014"), and know what changed. And conversational models (GPT, Gemini, Claude writing the prompt) follow them well as a structured description of intent.

## Workflow

### 1. Get the four facts

- **What deforms:** arm, forearm, hand, neck, torso, leg, or a whole animal or object.
- **The effect:** lengthen, coil, twist, bend into an arc, wave, pull toward the viewer, or the feeling behind it ("yearning", "grief", "reaching").
- **The medium:** charcoal, pastel, oil, photograph, sculpture.
- **The engine:** GPT (ChatGPT / gpt-image), Gemini, Midjourney, SDXL/OpenArt, or other.

If any is missing, pick a sensible default and say so: a clothed figure in a neutral relaxed pose, the left arm, GPT, and charcoal unless the request implies a medium (a street scene suggests a photograph or painting). Left and right are ambiguous to generators (the figure's left or the viewer's?); if the side matters, say "the arm on the right side of the image" as well. If they're fixing an earlier result, ask for the prompt they used, or assume the closest operator and say which. Neutral body plus soft light gives the deformation room to read. A busy pose or harsh light competes with it.

### 2. Pick one operator

Read `references/operators.md` for the capsule, prompt, checks and fixes of the one you choose.

| want | operator | start here because |
|---|---|---|
| a coil or spiral in a limb | **0 Segmented Coil** | the recommended starter: joint rotate + small wrist turn + short spiral, which models manage better than a pure spiral |
| a longer reach | **1 Vector Extension** | elbow anchored, thickness locked |
| a longer neck | **2 Logarithmic Scaling** | stretches more near the collar, less near the head |
| a twist without a bend | **3 Rotational Transform** | upper arm frozen, forearm rolls |
| an organic spiral, tight then open | **4 Fibonacci Coil** | only after Segmented Coil works |
| an elegant stretched arc | **5 Parabolic Extension** | elbow as the crest of one smooth curve |
| a limb pulled toward the viewer | **6 Depth Tug** | localized, not a camera change |
| a serpentine wave | **7 Sine Modulation** | pins at elbow and wrist keep it one arm |
| more tension without more distortion | **8 Viewfinder Shift** | framing only, applied after a deformation |

Stack moves only once each one lands alone. Order is always **transforms → constraints → viewfinder**.

### 3. Fill the binder

Every prompt sits inside the binder, with the operator line where it says `[DISTORTION]`. Swap figure and part as needed, and keep the continuity and thickness language. When swapping the medium, change the material line too:

| medium | material line |
|---|---|
| charcoal / pastel | charcoal (pastel) grain and tonal shading applied uniformly across the figure and the deformed limb |
| oil / painting | the same brushwork, paint handling and light across the figure and the deformed limb |
| photograph | consistent skin texture, lighting and focus across the body and the deformed limb; sleeve or clothing follows the deformation |
| sculpture | the same material surface (bronze, plaster, clay) continuous across the form |

If the person is getting a specific object (ribbon, scarf, vine), add that word to the negatives and keep it out of the positive prompt entirely.

```text
A charcoal drawing, soft diffused light. A female clothed figure in a neutral, relaxed pose.
Seamless integration between body and any distortion; no seams or joins. [DISTORTION]
Maintain original thickness across the figure. Keep anatomy and proportions elsewhere.
Material consistency: charcoal grain and tonal shading applied uniformly across the figure and
the deformed limb. Avoid grotesque enlargement; aim for graceful distortion with coherent volume
and shadow.
```

### 4. Write the prompt for the engine

Give the person:

1. **The prompt to paste**: binder plus the operator's natural prompt line, written for their engine (`references/engines.md`). For GPT and Gemini that is one declarative paragraph. For Midjourney and SDXL it is a two-step recipe: generate a neutral base, then inpaint or Vary (Region) the limb with the operator line and strong negatives.
2. **The capsule** (YAML) when they want something to tune, reuse or hand to a conversational model. Leave it out if they just want a picture.
3. **Acceptance checks**: two to four things to look for in the result.
4. **If it goes wrong**: the two or three failure → fix lines most likely for this operator.

### 5. Iterate from what came back

When the person reports or shows a result, check it against the acceptance checks and apply the matching fix from the operator or from `references/troubleshooting.md`. Change one thing at a time (a single failure → fix line counts as one change, even when it has several parts). On GPT and Gemini, edit in the same conversation rather than regenerating: start with "Keep this exact image, figure, pose, framing and style; change only …". Most fixes are words ("the coil is the arm itself; not wrapping"), a smaller amplitude, an extra pin, or (on Midjourney/SDXL) a bigger mask.

If the idea carries a feeling (grief, longing), land the deformation first and let pose, gaze and light carry the mood; add a second move (a neck arc, a bow) as a later pass.

### 6. Frame last

If they want more tension, use Operator 8 after the deformation is accepted: same geometry, subject pushed toward one edge, wide negative space on the other, slight zoom. It adds no new deformation. If the `composition-critique` skill is installed, `python ../composition-critique/scripts/critique.py BEFORE --compare AFTER` will show the mass moving off-center.

## Output

```text
**Operator:** <name>, and why it fits the idea

**Prompt** (<engine>)
<paste-ready text; for MJ/SDXL, Step 1 base and Step 2 edit>

**Capsule** (optional, to tune or reuse)
<yaml>

**Look for:** <acceptance checks>

**If it…** <failure> → <add this>
```

## Keep it honest and safe

- **Not CAD.** It is systematic prompting. Payoff is repeatability and clarity, not pixel control.
- **Stay graceful, not gory.** The playbook's moves are elegant impossibilities. Keep "no gore, no broken anatomy" in negatives, and don't steer toward body horror unless the person clearly wants it for their own art, and even then not graphic injury.
- **Default to clothed figures.** The playbook works with clothed or short-sleeved figures. Bare arms are fine; nudity isn't needed for any operator.
- **Use their own assets and follow each platform's terms.** Some platforms treat strong body deformation as low quality or unsafe and will resist; say so instead of escalating tricks.

## Related skills

`composition-critique` (measure a result, or check that a viewfinder shift did what was meant) · `vtl-picture-this` (felt language for what a placement does).
