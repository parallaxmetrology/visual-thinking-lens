# Troubleshooting

Find the symptom, apply one fix, rerun. Operator-specific fixes are in `operators.md`; engine-specific ones in `engines.md`.

## By symptom

| what you see | why it happens | fix |
|---|---|---|
| a rope, cord, vine, bracelet or armor around the limb | "coil", "spiral", "twist" are strongly tied to objects | "the coil is the arm itself; continuous flesh and bone; not wrapping; no objects"; add skin cues ("torsion folds in the skin follow the spiral"); add object negatives |
| a third arm or duplicate hand | the model reads the wave or extension as a new limb | pin elbow and wrist; add "single continuous arm; no branching"; lower amplitude |
| the hand vanished | the move strained the limb and the model dropped the end | pin the wrist; lock thickness and topology; "hand intact" |
| stretched instead of bent | field operators read as elongation | switch to `hinge_bend` 22–30° (or `arc_bend` for a neck), then a small perspective field 0.10–0.15 |
| coil reads as a stretch | not enough turn or overlap cue | wrist pronation 8–12°; an occlusion shadow where segments cross; turns near 0.9 |
| sausage or toroid bulges | amplitude or scale too high | "lower amplitude, slightly more turns, wider falloff, C2 continuity" |
| hard crease or broken elbow | junction not smooth | "smooth transition at the elbow; no sharp corner"; continuity C2 |
| snaps back to normal anatomy | the aesthetic prior wins | on MJ/SDXL: bigger mask including joints, lower stylize or CFG; on any engine: make the move a little larger and name it once more plainly |
| swollen, giant limb | "longer" read as "bigger" | "thin and in proportion; not oversized or gigantic; keep hand size unchanged" |
| thin, collapsed wrist | stretch thinned the distal end | "keep wrist full; no thinning"; lock thickness |
| whole figure warps | the field isn't localized | falloff radius 0.10–0.16 around the target; pin the upper arm or shoulder |
| depth pull looks like ordinary foreshortening | the camera moved instead of the limb | "do not change the camera; upper arm frozen; effect only from elbow to hand"; denser wrist creases; narrow under-shadow |
| seams or breaks at the junction | blend too abrupt, medium inconsistent | gaussian falloff 0.10–0.14; "material consistency: charcoal grain applied uniformly" |
| the style swallowed the move | strong medium overrides geometry | raise continuity to C2; reduce the overall magnitude; keep the binder simple |
| framing pass changed the body | the viewfinder step was read as a new deformation | "framing only; pose and body unchanged"; preserve the earlier transform by name |

## Guardrails that prevent most failures

- **Sine:** always pin elbow and wrist together. Start at amplitude ≤ 0.012 and raise slowly.
- **Depth tug:** always localize with a falloff radius and pin the upper arm, or the whole figure leans toward the vanishing point.
- **Spirals:** start with Segmented Coil, not a pure Fibonacci spiral. Breaking the move into rotation + wrist turn + short spiral gives the model pieces it can manage.
- **One change per rerun.** Otherwise you can't tell which fix worked.
- **Keep the accepted frame.** Models and their tuning change; the same prompt may not land next month. Note engine, version and seed when the platform exposes them.

## Make the move legible

A deformation that's there but doesn't read is a failure too. One or two of these cues usually fix it:

- an occlusion shadow where the limb crosses itself;
- tighter wrist-crease spacing and slight knuckle compression (for depth);
- a faint shadow along the inner side of an arc;
- a slightly brighter near edge;
- skin folds that follow the twist, and sleeve wrinkles that lag it.
