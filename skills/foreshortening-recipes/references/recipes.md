# Recipes

Copy, then adapt subject, medium and setting. Images: https://parallaxmetrology.com/foreshortening_recipe_book

Contents: [primary capsules](#primary-capsules) · [quick recipes](#quick-recipes) · [spine capsules](#spine-capsules) · [environments](#environments) · [long chains: the corridor](#long-chains-the-corridor)

## Primary capsules

The full pattern on three different subjects.

### Foreshortened figure (6 stages)

> A single continuous shot, no cuts. Naturalistic studio lighting, 50–70 mm lens feel. Render the subject as a full-body figure reclining toward the viewer, built step by step:
> (1) Foreground: the soles and toes are nearest, dominating the lower third of the frame.
> (2) Continue back through shins and knees, preserving strong scale decay and overlap.
> (3) Reveal thighs and pelvis, grounded with cast shadow contact.
> (4) Show ribcage and abdomen, compressed in perspective.
> (5) Add shoulders and neck, tapering along the depth axis.
> (6) Finally, resolve the head farthest from camera: smallest by visual angle, sharp yet least saturated.
> Do not render later stages unless prior ones are correctly established. No montage, no disjointed limbs, no symbolic insertions.

### Tree canopy, looking up (5 stages)

> A single continuous shot looking upward, 24–28 mm wide-angle feel. Build the composition in vertical depth order:
> (1) Start with the tree trunk closest to camera, bark texture crisp and detailed.
> (2) Extend into primary thick branches splitting from the trunk with strong occlusion.
> (3) Continue into secondary thinner branches, creating a radial lattice.
> (4) Add a semi-translucent leaf canopy forming an overhead plane.
> (5) Finally, reveal a small sunburst peeking through the gaps, flare controlled and leaf detail intact.
> No sun until the canopy exists. Flare must not overpower detail. All stages appear continuous and physically connected.

The order follows how you'd actually look up a tree (trunk → branch → canopy → sky), so it reads naturally.

### Pencil on a desk (5 stages)

> A single static shot, shallow depth of field, natural studio light. Sequence the object from nearest to farthest:
> (1) Foreground: the graphite tip in sharp focus, bevels and chips visible.
> (2) Progress into the sharpened wooden cone, clean helical cut.
> (3) Extend along the yellow hexagonal barrel, receding with perspective lines aligned to the desk grain.
> (4) Show the metal ferrule with knurling and specular reflections.
> (5) End with the pink eraser, farthest and slightly softer.
> Barrel must read continuous. Ferrule cannot appear before barrel. Only one pencil, no duplicates.

## Quick recipes

Short skeletons for a first try. Each has a use and what to check.

| recipe | prompt skeleton | check |
|---|---|---|
| **Recline** (classic figure depth) | Low front camera. Nearest foot or knee dominates lower frame. Body reclines away, each joint overlapping the next. Light from upper left, floor plane visible. No motion blur, no floating limbs. | scale decay, overlap order, tonal depth |
| **Curl** (compact, looping) | Top-down view. Figure curled inward; nearest limb overlaps torso. Body forms a closed loop; far side softened by haze. Single diffuse light from above. | inner overlaps correct, self-occlusion continuous |
| **Reach** (one limb at the lens) | Single still frame. One hand or arm reaching toward camera, fingers sharp. Forearm, shoulder and face recede along one line. Depth shown by focus falloff and scale, not blur streaks. | limb proportion, hand has thickness (no pancake palm) |
| **Crawl** (four contacts, crossing diagonals) | Low-angle view of a crouched figure on hands and feet. Nearest hand and knee crisp, far limbs fade into tone. Diagonals cross; ground plane consistent. | all four contacts on one plane, near and far limbs not swapped |
| **Stack** (objects, depth rhythm) | Series of identical solid objects (boxes, books, chairs). Foremost fully visible, each one behind smaller, on the same axis. Floor shadows aligned, no floating. 6–9 units, last merges with haze. | even spacing, one vanishing point, haze gradient, no rear object popping larger |
| **Coil** (organic path toward camera) | Snake-like or rope-like form looping toward camera. Overlaps alternate light and dark; contact shadows visible. Haze increases along the coil. | the path keeps its direction, curves compress with distance |
| **Tandem** (two figures compared) | Two figures on the same axis. Foreground one cropped; background one full-body. Shared light; no tangent merges. | relative scale, clear separation, one light |

**Variants for any recipe** (useful when testing an engine, see `reading-results.md`): Reverse (describe far → near), Baseline (drop the order words: "a line of …"), Anti-order (demand equal clarity for every part), Haze and shadow ladder (add explicit per-stage shadow bands and haze steps).

## Spine capsules

Stricter numbered versions.

**Reclining figure (classic perspective)**
> A single still frame, neutral studio light, 50–70 mm lens feel. (1) Foreground: nearest foot dominates lower third, sharp texture and edge. (2) Shins and knees overlap the foot; scale decay clear. (3) Thighs and pelvis continue backward; cast shadow anchors to floor. (4) Abdomen compresses in perspective; lighting consistent. (5) Chest and shoulders taper; focus softens slightly. (6) Farthest: head small by angle, least saturation, gaze off-frame. Gates: all limbs connected, no floating elements, single vanishing point.

**Crouched figure (diagonal compression)**
> Single still frame, 35 mm lens feel. (1) Foremost: bent knee and hand planted near camera, in crisp focus. (2) Torso twists back, forming a diagonal path toward the far shoulder. (3) Far knee and foot partly hidden, scale reduced. (4) Face and upper torso align to the same perspective; light continuous. Focus shallow near the knee, deeper toward the head; shadows unify across the floor.

Works in a painterly style too: "a single Degas-style painting of a dancer" followed by the same stages.

**Seated figure, low view**
> Low camera angle at ground height. (1) Nearest foot fills bottom edge. (2) Legs fold toward body; overlap gradual. (3) Torso upright; arms resting on knees. (4) Head and shoulders farthest, compressed in perspective. Consistent three-point lighting; no background clutter; depth from body geometry only.

**Running, freeze-frame**
> Single exposure, 85 mm lens, low front angle. (1) Foremost: reaching hand extended toward camera, sharp. (2–3) Arm and torso recede; depth shown by foreshortened limb lengths. (4–5) Rear leg trails into haze; ground contact shadow continuous. Capture energy through linear compression, not motion blur.

**Trumpet**
> Single still frame, neutral studio light, 70 mm lens. (1) Bell of the trumpet nearest, dominating lower third, metallic reflections crisp. (2–4) Tubing and valves recede; highlight streaks continuous. (5) Player's face farthest, framed by the instrument; focus softens gradually. Gates: brass reflections aligned; no duplicate bells.

**Motorbike head-on**
> Low front camera, 35 mm wide feel. (1) Nearest wheel rim crisp, dominating frame. (2) Forks and body shrink toward the seat; reflections aligned. (3) Rider's torso and helmet farthest, reduced contrast. Lighting cool neutral; single vanishing point centered; ground shadow continuous.

**Artist's hand toward the canvas**
> Single frame, shallow depth of field. (1) Foreground hand with brush nearly touches the lens, crisp detail. (2) Brush shaft recedes along the depth line. (3) Canvas surface occupies the mid-plane; strokes visible. (4) Artist's face farthest, half-blurred. Gates: same light source for hand and face; no duplicated tools.

**Bridge truss**
> Side-angle perspective. (1) Foremost beam intersection dominant; rivets crisp. (2–7) Repeating triangular trusses diminish toward the horizon; haze increases. (8) Final section faint, merges with sky. Consistent metal specularity; no duplicate geometry.

**Two figures in one depth chain**
> (1) Nearest figure cropped at the shoulders, crisp. (2) Second figure behind, full-body visible, softer. (3) Environment fades into diffuse tone. Keep eye-lines continuous; single color temperature.

## Environments

A figure in a place: the setting supplies the vanishing lines and the tonal falloff.

| scene | prompt skeleton |
|---|---|
| **Hallway rest** | A person sits against a corridor wall, one knee bent and nearest to the camera, foot oversized from perspective. The hallway recedes into cool light, vanishing point centered behind the figure. Shadows run along the floor, light from an overhead source. Walls parallel; tone softens with distance. (Also works as "a painting of a woman sitting against a corridor wall …") |
| **Doorway lean** | Low-angle shot inside a dim room. Foreground: a hand resting on a doorframe edge near camera. Torso and face lean outward into brighter hallway light. Depth shown by the shift in temperature, warm interior to cool exterior. Keep the doorframe vertical and floor perspective lines consistent. |
| **Studio stretch** | Wide lens, neutral light, wood floor visible. Person stretching forward, nearest hand extended to the lens, torso compressed, far leg fading into haze. Floor reflections subtle; walls diffuse gray. Keep limb continuity and light falloff natural. |
| **Subway seat** | Low front view of a person on a subway bench, one boot nearest to camera, filling the foreground. Legs and torso taper toward the back seats; the train interior repeats evenly behind. Fluorescent strips create linear perspective; reflections fade along the ceiling. No fisheye distortion. |
| **Rain street** | Street at dusk, wet reflective pavement. Foreground: a person stepping forward, foot close to camera, splash visible. Torso and background compress toward the horizon; distant lights blur slightly. Realistic scale compression and a single vanishing line from the streetlights. |
| **Chair in window light** | Studio interior, soft side light. Foremost hand rests on a chair arm near the lens; the seated figure recedes toward the window. Pale back wall; floor shadows consistent. No exaggerated lens warp; subtle reflection gradients. |
| **Alley run** | Narrow alley, low front camera. Running figure mid-stride, nearest foot in sharp focus, torso receding, far leg soft. Brick walls converge toward a single vanishing point. Morning light from behind; mild atmospheric haze. |
| **Field recline** | Outdoor midday light. A person reclining in grass, one knee raised toward the lens, horizon faint behind the shoulders. Depth from sharp foreground blades fading to a soft horizon. Consistent scale; no floating body parts. |
| **Workshop** | Interior with a workbench. Foreground: an extended arm holding a tool toward camera; focus on the hand and metal. Mid-ground: torso leaning forward; background shelves soft and warm. Shadows align along the bench plane; single neutral light. |
| **Pirate plank** | Far out on a plank of a pirate ship, a snake-like form loops toward camera beside a pirate's boots; another pirate stands far in the background. Overlaps alternate light and dark; contact shadows visible; haze increases along the coil. Dark and moody. |
| **Motorcycle jump** | Low front camera, 35 mm wide feel. A motorcycle launching off a cliff, as if stopped in motion. (1) Nearest wheel rim crisp, dominating frame. (2) Forks and body shrink toward the seat; reflections aligned; rider leaning forward. (3) Rider's torso and helmet farthest, reduced contrast. Single vanishing point centered; ground shadow continuous; background diffused with speed. For drama: sunset light with glare, the bike tilted into a turn, torque in the rider. |
| **Falling tree** | Low front camera, 35 mm wide feel. A tree tipping off a cliff, stopped in motion. (1) Roots nearest, dominating the frame. (2) Trunk, then branches, then leaves toward the back; leaves fly off in the wind. (3) Leaves farthest, reduced contrast. Sunset light; single vanishing point; background diffused with speed; the tree has the torque of falling. |

## Long chains: the corridor

Repeating structures (glass panels, columns, chairs) invite long chains. Asked for fifteen distinct panels, engines typically hold the first several, then compress the rest into vertical stripes and a glow. A nine-stage version with a shadow chain holds much better:

> Single still frame. Cool neutral light.
> (1) Foreground glass panel edge touching the frame; floor shadow band 1.
> (2–4) Panels recede; each adds a narrower shadow band aligned to the same vanishing point.
> Each panel has a small corner notch at the top right that shrinks with distance.
> (5–7) Haze increases; reflections dim; corner notches shrink.
> (8) Penultimate panel barely readable but still geometric.
> (9) Final panel falls into soft glow, geometry almost gone.
> Render 9 distinct panels. Ban columns, banding and a flat glowing wash; all depth must come from the panels and the shadow chain.

For arches, columns or seats, swap the panel and its notch for the unit and its own small feature (a keystone, a lamp, a seat number). The patches behind this recipe, and what to do if it still breaks, are in `reading-results.md` under "Long chains".
