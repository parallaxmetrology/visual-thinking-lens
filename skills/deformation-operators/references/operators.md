# Operators

Each operator has: a **capsule** (YAML, to tune or reuse), a **distortion line** (goes into the binder at `[DISTORTION]`), a **plain snippet** (one sentence for chat-style engines or quick edits), **acceptance checks** and **failure → fix** lines. Images for every operator: https://parallaxmetrology.com/deformation_operator_playbook

Contents: [capsule conventions](#capsule-conventions) · [quick starts](#quick-starts) · [0 Segmented Coil](#0-segmented-coil-recommended-starter) · [1 Vector Extension](#1-vector-extension) · [2 Logarithmic Scaling](#2-logarithmic-scaling-neck) · [3 Rotational Transform](#3-rotational-transform) · [4 Fibonacci Coil](#4-fibonacci-coil) · [5 Parabolic Extension](#5-parabolic-extension) · [6 Depth Tug](#6-depth-tug) · [7 Sine Modulation](#7-sine-modulation) · [8 Viewfinder Shift](#8-viewfinder-shift) · [bends and arcs](#bends-and-arcs) · [beyond the arm](#beyond-the-arm)

## Capsule conventions

- **Coordinates** normalized 0–1 in image space (x left → right, y top → bottom). Angles in degrees. Lengths as a fraction of the image diagonal.
- **anchors**: the fixed points (2–4 per limb: shoulder, elbow, wrist; hip, knee, ankle). If the model ignores one, name it more specifically ("left inner elbow crease") or add a `pin`.
- **select**: the region the move applies to, usually semantic (`left_arm_forearm_hand`).
- **pin** holds pose (the anchor stays put on the canvas). **locks** preserve geometry (thickness, topology, proportion) under the move.
- **falloff**: how the move blends into untouched areas (`gaussian`, radius).
- **continuity**: smoothness at the junction. C0 = connected, C1 = no corner, C2 = smooth curvature. C2 is the safe default.
- **interpret**: a plain-words reading the model should keep ("single continuous arm; no branching").
- Order: `transforms` → `constraints` → `viewfinder`.

The numbers are biases toward a look, not instructions the model executes.

## Quick starts

### Arm Extension (first try)

```yaml
vcf_capsule: 1.0
style: "charcoal, soft diffused light"
anchors:
  left_elbow: {x: 0.32, y: 0.58}
  wrist_L:    {x: 0.36, y: 0.78}
select:
  arm_L: {type: semantic, tag: "left_arm_forearm_hand"}
transforms:
  - op: pin
    target: [left_elbow, wrist_L]
    stiffness: 0.95
  - op: extend_vector
    target: arm_L
    anchor: left_elbow
    vec: {dx: 0.65, dy: 0.18}
    factor: 1.6
    locks: [thickness, topology]
    falloff: {type: gaussian, radius: 0.12}
    continuity: C1
    interpret: "single continuous arm; no branching"
constraints:
  seamless_integration: true
  material_consistency: "charcoal"
viewfinder:
  shift: {dx: -0.06, dy: +0.02}
  zoom: 1.03
```

> Charcoal, soft diffused light. A clothed female figure in a relaxed, neutral pose. Extend the left arm outward from the elbow along a vector angled slightly forward and right, to well beyond its natural length. Preserve thickness and topology, with smooth anatomical continuity through the joints. Pin elbow and wrist to keep orientation stable; ensure a single continuous arm with no branching. Integrate seamlessly into the figure, consistent with charcoal texture and shading.

### Sine Lite (safe defaults)

```yaml
vcf_capsule: 1.0
style: "charcoal, soft diffused light"
anchors:
  left_elbow: {x: 0.33, y: 0.56}
  wrist_L:    {x: 0.38, y: 0.78}
select:
  arm_L: {type: semantic, tag: "left_arm_forearm_hand"}
transforms:
  - op: pin
    target: [left_elbow, wrist_L]
    stiffness: 0.96
  - op: modulate_sine
    target: arm_L
    axis: path
    amplitude: 0.012        # raise toward 0.016-0.020 only once it stays one arm
    wavelength: 0.20
    phase: 1.57             # π/2, starts with a lateral bow
    locks: [topology, thickness]
    continuity: C2
    falloff: {type: gaussian, radius: 0.11}
    interpret: "single continuous arm; no branching"
  - op: wrist_orient
    target: hand_L
    mode: pronate
    angle_deg: 8
    continuity: C1
constraints:
  seamless_integration: true
  material_consistency: "charcoal"
  avoid: ["branching appendages", "prosthetic seams"]
viewfinder:
  shift: {dx: -0.04, dy: +0.02}
  zoom: 1.02
```

For a stronger wave in the forearm: wavelength 0.18 and `segment_weight: {upper: 0.6, forearm: 1.0, hand: 0.9}`.

---

## 0) Segmented Coil (recommended starter)

A coil built from three manageable pieces (elbow rotation, small wrist turn, short spiral) instead of one pure spiral. It lands more often than raw Fibonacci.

```yaml
# Standard
- op: segmented_coil
  target: arm_L
  elbow_rotate: 28
  wrist_pronate: 8
  spiral_turns: 0.85
  locks: [thickness, topology]
  continuity: C2
  shading: overlap_occlusion

# Minimal (bare or rolled sleeve): a little more of each so one crossing shows
- op: segmented_coil
  target: arm_L
  elbow_rotate: 30
  wrist_pronate: 12
  spiral_turns: 0.90
  locks: [thickness, topology]
  continuity: C2
  shading: overlap_occlusion
```

<details><summary>Full capsule (bare arm; keep the garment steps only if a sleeve is visible)</summary>

```yaml
vcf_capsule: 1.0
style: "charcoal, soft diffused light"
anchors:
  shoulder_L: {x: 0.30, y: 0.40}
  elbow_L:    {x: 0.33, y: 0.58}
  wrist_L:    {x: 0.37, y: 0.78}
select:
  forearm_L: {type: semantic, tag: "left_forearm"}
  hand_L:    {type: semantic, tag: "left_hand"}
  sleeve_L:  {type: semantic, tag: "left_sleeve_short"}   # omit if bare
transforms:
  - op: pin
    target: shoulder_L
    stiffness: 0.95
  - op: joint_rotate
    target: forearm_L
    hinge: elbow_L
    angle_deg: 30
    continuity: C2
    locks: [thickness, topology]
  - op: wrist_orient
    target: hand_L
    mode: pronate
    angle_deg: 12
    continuity: C2
  - op: spiral_segment
    target: [forearm_L, hand_L]
    center: elbow_L
    turns: 0.90                 # at least one clear overlap
    scale: 0.14                 # small, to avoid sausage bulges
    handedness: CW
    blend: 0.92
    falloff: {type: gaussian, radius: 0.14}
    continuity: C2
    locks: [thickness, topology]
    segment_weight: {forearm_proximal: 0.6, forearm_distal: 1.0, hand: 0.9}
  - op: self_occlusion_enhance
    target: forearm_L
    style: "charcoal"
    params: {strength: 0.72, width: 0.010}
  # garment, only if a sleeve is visible
  - op: seam_lock
    target: sleeve_L
    seams: ["armhole", "cuff"]
    tolerance: 0.12
  - op: garment_follow
    target: sleeve_L
    follow_target: forearm_L
    adherence: 0.55
    slip_bias: 0.25
    wrinkle_gen: {mode: compression, intensity: 0.50, direction: "around coil", density: 0.55}
constraints:
  seamless_integration: true
  material_consistency: "charcoal"
  interpret: "single continuous arm; no branching"
  avoid: ["rope", "cord", "wrapping", "external object"]
  anatomical_continuity: true
  require_overlap_crossing: true
viewfinder:
  shift: {dx: -0.05, dy: +0.02}
  zoom: 1.03
```
</details>

**Distortion line:** Make the left arm itself twist into a gentle anatomical coil starting at the elbow, with one clear overlap that casts a soft occlusion shadow; keep the arm's thickness and the hand intact.

**Plain snippet:** Make the left arm itself twist into a gentle coil starting at the elbow, with one clear overlap that casts a soft occlusion shadow; keep thickness and the hand intact.

**Look for:** the arm's own mass (not an object) forms the coil; one visible overlap; thickness preserved; no seams or props.

**Failure → fix**
- Rope or bracelet appears → "the coil is the arm itself; not wrapping; no objects."
- Sausage bulges → "lower amplitude; slightly more turns; smooth, continuous curve through the elbow."
- Elbow breaks → "smooth transition at the elbow; no sharp corner."
- Coil reads as a stretch → add wrist pronation 8–12° and an occlusion shadow where segments cross.
- To force it harder, replace the spiral with two steps: `joint_rotate {target: hand_L, hinge: wrist_L, angle_deg: 22}` then `path_conform {target: hand_L, path: "fibonacci", turns: 0.6, scale: 0.24, adherence: 0.85}`. Prose cues that help: "foreshortened knuckles overlap the forearm as the coil turns toward the viewer", "cast shadow from the upper coil onto the lower segment".

## 1) Vector Extension

Elbow-anchored lengthening along a direction.

```yaml
- op: extend_vector
  target: arm_L
  anchor: left_elbow
  vec: {dx: 0.65, dy: 0.18}     # toward lower right
  factor: 1.8
  locks: [thickness]
  falloff: {type: gaussian, radius: 0.12}
  continuity: C1
```

**Distortion line:** Lengthen the left arm outward from the elbow along a slight forward-right diagonal; almost double the natural length, but keep the forearm and hand the same thickness and fully connected.

**Plain snippet:** Lengthen the left arm outward from the elbow along a slight forward-right diagonal, nearly double the natural reach, keeping the forearm and hand the same thickness and fully connected.

**Look for:** elbow stays put; direction is clear; hand size intact; no tearing at sleeve or skin.

**Failure → fix**
- Hand stretches → "keep hand size and volume unchanged."
- Direction drifts → "extend along a forward-right line from the elbow."
- Looks rubbery → reduce the amount ("just under double") and add "no thinning."
- Swollen or giant → "remains thin and in proportion; not oversized or gigantic."

## 2) Logarithmic Scaling (neck)

A gradient stretch: more near the collar, less near the head.

```yaml
- op: scale_log
  target: neck
  anchor: neck_base
  k: 0.75
  axis: y
  locks: [proportions_x]
  continuity: C2
```

**Distortion line:** Stretch the neck upward gradually so it lengthens more near the collar and less near the head; keep its width proportional and the jawline and shoulders coherent; leave the rest of the body unchanged.

**Plain snippet:** Stretch the neck upward gradually, more near the collar and less near the head, keeping its width proportional; head size, jawline and shoulders unchanged.

**Look for:** gradient stretch (not uniform); believable neck width; head and shoulders stable.

**Failure → fix**
- Pinched "giraffe" neck → "keep neck width proportional; preserve throat fullness."
- Head shrinks → "head size unchanged."
- Shoulders creep up → "collarbones and shoulders stay in place."
- You wanted an arc and got plain elongation → use `arc_bend` (see [bends and arcs](#bends-and-arcs)).

## 3) Rotational Transform

The forearm rolls around its own axis; no bend, no pose change.

```yaml
- op: rotate
  target: arm_L
  anchor: left_elbow
  angle: 30
  continuity: C1
```

**Distortion line / plain snippet:** Freeze the shoulder and upper arm. Keep the elbow angle the same. Rotate the forearm in place around the elbow so the palm turns toward the torso and the thumb rolls downward; add soft spiral skin folds near the elbow and a few sleeve wrinkles that lag the twist.

**Look for:** upper arm unmoved; elbow angle unchanged; twist reads in the forearm; thickness preserved.

**Failure → fix**
- Looks like a whole-arm pose → "upper arm stays fixed; rotation happens only at the forearm."
- Reads as a bend, not a twist → "no extra bend; palm turns inward; subtle spiral crease elbow to wrist."
- Wrist collapses → "keep wrist full; no thinning."

## 4) Fibonacci Coil

Organic spiral: tight near the shoulder, opening toward the hand. Try Segmented Coil first.

```yaml
- op: spiral_fibonacci
  target: arm_L
  center: shoulder_L
  turns: 1.1                 # more over-wraps and crowds
  scale: 0.16                # bigger bulges into "sausage"
  handedness: CW
  phi_ratio: 1.618
  blend: 0.90
  falloff: {type: gaussian, radius: 0.18}
  continuity: C2
  locks: [thickness, topology]
  segment_weight: {proximal: 0.7, distal: 1.0}
  require_overlap_crossing: true
  avoid: ["rope", "cord", "external wrapping"]
  anatomical_continuity: true
```

**Distortion line:** Form a graceful spiral in the left arm that is tighter near the shoulder and opens wider toward the forearm and hand; show one visible overlap; the spiral is the arm itself, not something wrapped around it.

**Look for:** tighter spacing at the origin, wider toward the hand; a visible overlap; continuous arm mass; no props.

**Failure → fix**
- Even, toroid bulges → "tighter near shoulder, wider toward hand."
- Rope → "not wrapping; no rope, band or bracelet."
- Hard break at the shoulder → "smoothly blends into the upper arm."

## 5) Parabolic Extension

One smooth arc from shoulder to wrist with the elbow as its crest.

```yaml
- op: extend_parabolic
  target: arm_L
  axis: {mode: "from_to", from: shoulder_L, to: wrist_L}
  factor: 0.42               # Grace variant: 0.36, falloff radius 0.19, softer
  vertex_lock: elbow_L
  continuity: C2
  locks: [thickness, topology]
  curvature_tension: 0.72
  falloff: {type: gaussian, radius: 0.14}
  distal_taper: 0.80
  proximal_weight: 0.70
  self_occlusion_enhance: {strength: 0.70, width: 0.012, side: "inner_curve"}
  anatomical_continuity: true
  avoid: ["ballooning", "crease seam"]
```

**Distortion line:** Shape the left arm into a smooth, graceful U-shaped arc with the elbow smoothed into the high point (no joint). The curve runs from shoulder to wrist as one continuous sweep. Keep the arm full: no bulges, no hard crease. Add a faint shadow along the inner side of the arc so the curve reads.

**Look for:** elbow clearly the crest; one continuous arc; no bulge or kink; volume preserved.

**Failure → fix**
- Reads straight → "increase the arc; make the elbow visibly the highest point."
- Kink at the elbow → "no sharp corner; smooth handoff from shoulder to forearm."
- Bulging → "gentle arc; keep thickness even; avoid ballooning."

## 6) Depth Tug

A local pull toward the viewer, as if the forearm alone sits in stronger perspective. Not a camera change.

```yaml
- op: pin
  target: shoulder_L
  stiffness: 0.95
- op: hinge_lock
  target: elbow_L
  stiffness: 0.85
- op: perspective_inverse_square
  target: arm_L
  center: forearm_mid_L
  vanishing: {x: 0.85, y: 0.42}    # just right of the figure
  magnitude: 0.44                  # conservative: 0.40, radius 0.18
  continuity: C2
  locks: [topology]
  thickness_lock: 0.90
  falloff: {mode: inverse_square, radius: 0.16}
  distal_scale_comp: 0.92          # protects wrist and hand fullness
  depth_occlusion_enhance: {strength: 0.68, width: 0.010, region: "under forearm to wrist"}
  require_vanishing_convergence: true
  avoid: ["accordion fold", "thin wrist collapse"]
```

**Distortion line:** Do not change the camera. Modify only the left forearm (elbow to hand): pull it forward toward the viewer, toward a small point just right of the frame, so its top and bottom edges subtly converge, strongest near the wrist. Upper arm and elbow stay unchanged. Keep the wrist and hand full. Add tighter wrist-crease spacing, a narrow soft shadow under the forearm and a slightly brighter near edge to sell the depth.

**Look for:** convergence strongest at the wrist; upper arm untouched; slight compression at wrist and knuckles; a slim under-shadow.

**Failure → fix**
- Looks like ordinary foreshortening → "upper arm frozen; effect only from elbow to hand; camera unchanged."
- No depth → "denser wrist creases and slight knuckle compression; narrow under-forearm shadow."
- Wrist thins → "keep wrist full; no thin-wrist collapse."
- Whole figure warps → the field isn't local: shrink the radius and pin the upper arm.

## 7) Sine Modulation

One gentle serpentine wave along the limb. The pins are what keep it a single arm.

```yaml
- op: pin
  target: [left_elbow, wrist_L]
  stiffness: 0.95
- op: modulate_sine
  target: arm_L
  axis: path
  amplitude: 0.012       # 0.010-0.016 safe; start low
  wavelength: 0.18
  phase: 1.57            # π/2, lateral bow start
  locks: [thickness, topology]
  continuity: C2
  falloff: {type: gaussian, radius: 0.10}
  interpret: "single continuous arm; no branching"
- op: wrist_orient
  target: hand_L
  mode: pronate
  angle_deg: 8
```

**Distortion line:** Apply a single continuous serpentine wave along the existing left arm (not an extra limb). Elbow and wrist are anchored, keeping the hand intact. Gentle undulation; preserve thickness and topology; slight wrist pronation so foreshortening sells the wave. No duplication, no branching, no seams.

**Plain snippet:** Add one gentle serpentine wave running from elbow to hand; joints feel pinned and continuous; the limb's mass follows the wave, not just surface wrinkles; hand remains intact.

**Look for:** one crest and trough across the forearm; joints connected; volume intact.

**Failure → fix**
- A second arm appears → keep both pins, keep the interpret line, drop amplitude to 0.010.
- Surface wrinkles only → "the limb's mass follows the wave; not just skin."
- Too subtle → amplitude 0.014–0.018 with both pins on, plus a light occlusion shadow at the inner turns.
- Over-wobble → "smaller wave; one gentle undulation only."

## 8) Viewfinder Shift

Framing only, after a deformation is accepted. Pushing the subject toward one edge with a large void on the other raises tension without touching anatomy.

```yaml
viewfinder:
  shift: {dx: -0.20, dy: +0.06}    # subject toward the left edge
  zoom: 1.10
  edge_proximity: {left: 0.85}
  void_bias: {right: 1.25}         # keep a large right-side void
  crop_allowance: {shoulder: 0.02, forearm: 0.03}
constraints:
  interpret: "no geometric deformation added; framing only"
  preserve_transforms: ["extend_parabolic"]   # whichever operator made the accepted frame
```

**Prompt:** Generate a second shot of the same scene with identical pose and geometry; change only the framing: push the subject left, keep a large right-side negative space, slight zoom; no anatomical changes.

**Look for:** identical geometry; subject near the left edge; big negative space on the right.

**Failure → fix**
- Geometry changed → restate "framing only; pose and body unchanged."
- Too mild → increase shift or zoom slightly.
- Harsh crop → "allow a small trim on shoulder and forearm; keep the face unobstructed."

---

## Bends and arcs

When a field operator stretches instead of bending, set the bend explicitly first, then add a small field so it reads as depth rather than a mechanical joint.

```yaml
- op: hinge_bend
  target: forearm_L
  hinge: left_elbow
  arc_degrees: 26                 # 22-30
  radius: 0.22
  plane_bias: {toward: {x: 0.85, y: 0.42}, weight: 0.7}
  locks: [thickness, topology]
  continuity: C2
- op: perspective_inverse_square  # small, optional
  target: forearm_L
  vanishing: {x: 0.85, y: 0.42}
  magnitude: 0.15                 # 0.10-0.15
  falloff: {type: gaussian, radius: 0.10}
```

Neck arc (instead of plain elongation):

```yaml
- op: arc_bend
  target: neck
  hinge: neck_base
  arc_degrees: 34                 # 32-36
  radius: 0.24                    # 0.22-0.26
  orientation: up
  continuity: C2
  locks: [topology, width]
- op: head_chin_tilt
  target: head
  pivot: jaw_pivot
  angle_deg: 8                    # head commits to the arc plane
```

Prose cues: "chin follows the neck's arc, slight lift toward the bend"; shading hints at the neck muscle and the notch above the breastbone.

Levers: more bend → raise `arc_degrees` (or the field's magnitude); keep the bend near the joint → smaller radius; avoid stretch → keep thickness and topology locks with C2.

## Beyond the arm

The same rules carry to other parts, animals and objects: name the part, anchor its two ends, say the form itself deforms, keep everything else intact.

**Sculpted coil template.** On instruction-following engines (GPT, Gemini) this plain-language form often lands as well as a capsule, and it generalizes:

> The figure's left arm is a distinct, sculpted coil that spirals away from the body with the hand at the end. The arm is a piece of flexible form, with a taut skin surface and an internal spiraling torsion that does not enlarge. This coiled form keeps its connection to the shoulder and hand. The entire composition is a single, seamless image, with no visible seams or joints, where the organic body meets the spiraling, unresolvable form.

Swap the part ("legs … with the feet at the end, in proportion to the body"; "torso … linking the lower body with the upper, connected at chest and hip"), or the subject ("the elephant's midsection … maintain all parts of the elephant"; "the car's midsection … connection from hood to trunk"). Add "thin" and "in proportion" when it swells.

**In a scene.** Give the deformation a reason and keep the scene consistent: an arm extended about 1.7× to reach a cup across a café table, elbow resting on the table, sleeve following the extension, other patrons in soft focus. Or a coiled arm in a garden whose curve rhymes with vine tendrils, with negatives "NOT a vine wrapped around the arm; NOT rope or a decorative element". Close with "the extended arm reads as a graceful impossibility within a realistic scene."

**For a feeling.** Elongation can carry mood without numbers: a neck painfully lengthened and bowed for grief, arms stretching toward a distant farmhouse for longing, a figure stretched toward the top and bottom of the frame in the manner of Giacometti. Keep "thin and in proportion; graceful, not monstrous" in the prompt.
