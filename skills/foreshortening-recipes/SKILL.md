---
name: foreshortening-recipes
description: Write image-generator prompts that hold strong foreshortening and depth (a foot or hand thrust toward the camera, a reclining figure seen from the feet, a crouch, a reach, a motorbike head-on, a pencil or bridge receding, a corridor) by describing the subject in numbered stages from nearest to farthest, with gates, contact and light cues, and bans on the usual cheats. Includes 30+ ready recipes for figures, objects and environments, and a checklist for reading what came back. Use whenever someone wants extreme perspective or a low or close camera angle in an AI image, says their figure looks flat, limbs are the wrong size, parts float or overlap wrongly, or asks how to get depth, foreshortening or "coming at the camera" shots from GPT, Gemini, Midjourney or SDXL, even if they never say "foreshortening".
---

# Foreshortening recipes

Generators tend to build a figure as a flat arrangement of familiar silhouettes. Ask for a foot thrust at the camera and you get a normal-sized foot, a torso that doesn't recede, limbs that float or see through each other. This skill writes the prompt as a walk through space: start at the nearest point and move back, stage by stage, so each part has the previous one to overlap and shrink behind.

Adapted from the *Foreshortening Recipe Book* by Russell Parrish. Example images for the recipes are at **https://parallaxmetrology.com/foreshortening_recipe_book**. Point people there when they want to see what a recipe produces.

```text
nearest first. one stage per part, in order. each stage overlaps and shrinks behind the last.
anchor it: floor plane, contact shadows, one light, one vanishing point.
ban the cheats: no montage, no clones, no floating parts, no flat glow at the far end.
```

## Why the order helps (and what not to claim)

Order in a prompt tends to become order in depth: early, detailed stages land as the foreground anchor, later ones recede. Continuity verbs (continue, extend, taper, emerge, reveal) encourage a smooth decay in size and contrast rather than jumps. That's a practical observation, not a mechanism: nobody outside the vendors knows how a given model allocates a prompt, and results vary by engine, version and seed. Say so if someone expects a guarantee.

## The spine

Every recipe is built from five parts. Use them in this order:

1. **Frame header:** `Single still frame. No cuts. Naturalistic lens. Realistic depth cues. Respect the numbered order.`
2. **Camera and focus:** a lens feel (a wide lens with the camera close to the nearest part exaggerates foreshortening; a long lens from farther back flattens it: 24–28 mm for drama, 35 mm for figures in a space, 50–70 mm for a natural recline, 85 mm for flattened compression), a camera position (low front, top-down, ground height), and where the anchor sits (`foreground anchor in the lower third`). Focus that deepens or softens with distance. `Occlusion, not floating.`
3. **Numbered stages, nearest to farthest:**
   - `(1) Nearest: … dominates the lower third, crisp texture and edge.`
   - `(2) … continues back, overlapping (1); clear scale decay.`
   - `(3) … extends, grounded by a cast shadow on the floor.`
   - `(4) … compressed in perspective.`
   - `(5) Farthest: … smallest by visual angle, softest, least saturated.`
4. **Gates:** `Do not show (2) unless (1) is established.` `Final stage smallest by scale and softest by contrast or haze.` `All parts connected; single vanishing point.`
5. **Drift guards:** `Not a montage. No duplicates or clones. No floating limbs. No style change mid-frame.`

A rider and their board or bike are one chain: the object's nearest end first, then the rider. A moving subject works the same way; show speed through compression, not motion blur.

The spine works for any subject with a long axis: a figure (foot → knee → torso → head), a tree (trunk → branches → canopy → sky), an object (pencil tip → barrel → eraser), a place (nearest beam → repeating trusses → haze).

## Workflow

### 1. Get the facts

- **Subject and pose:** reclining, crouched, seated, reaching, running; or an object or a place.
- **Nearest point:** what should be closest to the camera (the soles, a knee, a hand, a wheel, a bell). If they don't say, pick the end that makes the most dramatic overlap and say so.
- **Medium and setting:** photo, painting, drawing; studio, hallway, street.
- **Engine:** GPT (ChatGPT / gpt-image), Gemini, Midjourney, SDXL, or other.

### 2. Start from a recipe

Find the closest one in `references/recipes.md` (quick recipes for a first try, spine capsules for strict control, environments for a figure in a place) and adapt it. Writing from the spine directly is fine when nothing fits.

### 3. Set the stage count and fit the engine

Four to six stages is the reliable range. Long chains tend to blur in the middle: later stages merge into one depth, lines drift, the far end turns into a glow. Repeating structures (a corridor, arches, a bridge, a stack) are the exception: 9–11 stages can hold, but only with all of the long-chain patches in `references/reading-results.md` together: a floor and shadow chain, a small ID mark on each unit, a ban on stripes and glow, and the last few stages **faded on purpose** ("barely readable but still geometric", then "soft glow") instead of full detail all the way back.

**Engine notes.**
- *GPT and Gemini:* the numbered spine as written; refine in the same conversation.
- *Midjourney:* three or four stages written as one ordered sentence (it mostly ignores numbering and gates). Move the bans into `--no` as plain nouns (`--no montage, duplicates, floating limbs, motion blur, stripes`) rather than "no X" phrases in the prompt, since Midjourney tends to draw words it reads. Add `--style raw` to cut beautification and an aspect ratio that gives the depth room (`--ar 2:3` for a figure toward camera, `--ar 3:2` for a corridor).
- *SDXL:* three or four stages; bans go in the negative prompt; a depth ControlNet from a rough sketch of the pose helps more than any wording.

**Soft media** (watercolor, pastel, charcoal) fight the tonal ladder. Ask for it in the medium's terms: nearest forms darker, wetter pigment and sharper edges; far forms pale, dry washes and lost edges.

### 4. Add the anchors

Depth needs something countable. Most failures come from a missing one:

- a visible **floor plane** with **contact shadows** where feet, hands or objects touch it;
- **one light source** named by direction ("light from upper left");
- **one vanishing point**, and lines that should converge to it (floor seams, rails, walls, bench edges);
- a **tonal ladder**: near forms higher contrast, far forms softer, hazier or less saturated. When the light sits deep in the scene (a bright doorway, a window, a low sun behind the subject), name it, so a bright far end reads as light and not as a mistake.

### 5. Give the prompt and what to check

Hand over the prompt ready to paste, then three to five of the checks from `references/reading-results.md` that matter most for this subject (contact for anything on a floor, vanishing point for places, overlap for coiled or crouched figures, compression always). When the person reports or shows a result, name the failure, apply the matching fix, and change one thing at a time. On GPT and Gemini, refine in the same conversation ("keep this exact image; change only …").

### 6. Harden only if it drifts

- **Causal connectors:** "only after", "once established", "then".
- **Priorities:** "stage (1) priority 1.0 … stage (6) priority 0.3".
- **Bans:** "no duplicates, no cutaways, no montage, no cloned objects".
- **Video:** "one continuous shot; no zoom cuts; camera static; change comes from composition, not editing."

## Output

```text
**Recipe:** <name or "from the spine">, and why it fits

**Prompt** (<engine>)
<paste-ready text>

**Check:** <3–5 checks for this subject>

**If it…**
- <failure> → <fix> (two or three, most likely first)
```

## Keep it honest

- **Prompting, not geometry control.** The recipes pressure a model toward coherent depth; they don't guarantee it.
- **No ceilings as facts.** "Most engines hold about six stages" is a rule of thumb from use, not a measured limit. If someone wants to know their engine's limit, give them the forward / reverse / overload test in `references/reading-results.md` and let their own runs answer it.
- **Default to clothed figures.** None of the recipes need nudity; bare feet and hands are fine.
- **Read failures as information.** A blur or repeat at stage 7 tells you where that engine gives up on this prompt; shorten the chain or stage the fade.

## Related skills

`deformation-operators` (Depth Tug pulls one limb toward the viewer without changing the camera) · `composition-critique` (feedback on the result's framing and value structure).
