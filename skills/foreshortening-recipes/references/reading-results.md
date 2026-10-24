# Reading the result

Foreshortening rarely fails all at once. Look for where depth starts to come apart, then fix that stage.

## Five checks

| check | holds | fails |
|---|---|---|
| **Compression** | each part shortens progressively along one depth line; no size jumps | a limb or surface stays full size deep in the frame |
| **Overlap order** | each nearer form partly hides the one behind; clean contours | see-through parts, doubled edges, a far limb drawn over a near one |
| **Vanishing point** | floor seams, limb axes, furniture and walls converge consistently (roughly is fine) | lines run parallel or bend toward two or more points |
| **Tonal depth** | near planes higher contrast, far planes softer or hazier | inverted: bright, crisp far face with dark, soft near limbs |
| **Contact** | feet, hands and objects touching the ground show a shadow or compression there | floating limbs, shadows at mismatched angles |

Three or four overlapping planes holding shape and contact is a good result. Seven or more with steady rhythm and one vanishing point is excellent.

## Failure patterns and fixes

| what you see | name | fix |
|---|---|---|
| semi-transparent or doubled edges between stages (a forearm showing through a thigh, two trunks) | **ghosted overlap** | state the overlap explicitly per stage ("(2) overlaps and hides part of (1)"); fewer stages; "solid, opaque forms; no transparency" |
| perspective lines drift, bend or split partway back | **vanishing-point drift** | name one vanishing point and where it sits; add lines that must converge to it (floor seams, rails); "single vanishing point throughout" |
| far forms brighter or crisper than near ones with no light reason | **tonal inversion** | add the tonal ladder: "nearest highest contrast; each stage softer and less saturated; farthest hazy"; name one light direction |
| figures, trees or objects line up in vertical columns instead of receding | **columnar cheat** | add a floor plane and a shadow chain; "ban columnar textures, banding or vertical striping" |
| shrinking stops halfway; mid and far parts end up the same size | **compression stall** | shorten the chain; add explicit scale words per stage ("half the size of (2)"); stage the fade |
| late stages dissolve, repeat or turn to noise while the foreground degrades | **collapse** | cut stages; move detail into the first three; let the rest fade by design |
| torso flat, head too large | early detail overweighted | stress compression in the middle stages ("ribcage compressed to a narrow band"); "head small by visual angle" |
| light comes from several directions | long prompt diluted the light cue | one named light source, repeated in the gates ("same light for hand and face") |
| clean shapes but nothing touches the ground | no physical reference | floor plane plus contact shadows at every touch point |
| pose barely changes, angle weak | the order didn't take | stronger camera words (low front, wide lens feel, "nearest foot fills the bottom edge"); add "only after", "once established" |

## Long chains

When a repeating subject (panels, trusses, stacks) turns into stripes and a glow:

- **Floor and shadow chain:** "Include a matte floor plane. Each panel casts a distinct shadow band on the floor that gets narrower and lighter with distance. The shadows overlap in order and align to a single vanishing point. No vertical seams that are not panel edges."
- **A small ID mark per unit:** "Each panel has a small corner notch at the top right. The notch shrinks with distance and stays visible on the nearest ten panels." Something countable keeps the units distinct. Use whatever small feature the unit naturally has: a keystone on an arch, a lamp on a column, a number on a seat back, a bolt on a truss.
- **Ban the lazy solve:** "No columnar wall textures, banding or vertical striping. No flat luminous wash; far panels stay geometric until near the end."
- **Cap the count, stage the fade:** "Render 11 distinct panels; the last four go from faint geometry to line ghosts to diffuse glow."

## Testing an engine (optional)

If someone wants to know how far their engine holds depth on this kind of prompt, let their runs answer it rather than quoting a number:

- **Forward:** the recipe as written, near → far.
- **Reverse:** the same stages far → near. Usually flatter or confused; how much tells you how much the order is doing.
- **Anti-order:** every part "at equal clarity and tone". A flat baseline.
- **Overload:** a corridor with 12–15 named stages. Count how many distinct layers survive before they merge, and repeat across a few seeds before trusting the count.

Record engine, version, settings and seed with each result; models change.
