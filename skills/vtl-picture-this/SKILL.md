---
name: vtl-picture-this
description: Translate a VTL kernel reading into felt compositional language using the principles in Molly Bang's Picture This (weight, position, edges, open space, direction), anchored to where the measured values sit relative to real images. Use when an artist, illustrator, teacher or writer wants measured structure explained in bodily, spatial terms ("heavy and low", "pressing at the edge", "held breath"), or wants to talk about a composition's felt force with the numbers behind it.
---

# Picture This × VTL

The kernel measures geometry. Molly Bang's *Picture This: How Pictures Work* explains how geometry is felt: weight, height, edges, open space, direction. This skill connects the two. It's a **translation**: the numbers are measured, and the felt reading is an interpretation offered on top of them, so label it that way.

## Inputs

A kernel reading: `vtl measure image.jpg` (JSON) or a CSV row. Minimum: `delta_x`, `delta_y`, `r_v`, `mu`, `x_p`, `sdi`; better with `theta`, `d_s`, `gradient_floor_85`, `gradient_ceiling_97`. Without measurements, say so and work only from a description, labeled **approximate**.

## Workflow

1. **Gate on QA.** FAIL means no reading. With TEXTURE_FIELD, talk about the field's weight and spread, not an object's.
2. **Place each value against the reference set** (see [bang-mapping.md](references/bang-mapping.md) and [../vtl/references/reference-ranges.md](../vtl/references/reference-ranges.md)). The quartiles of real images matter here: almost every real image has θ < 0.06 and ρᵣ ≈ 12, so absolute cutoffs would give every picture the same reading.
3. **Translate** each notable value (top or bottom quartile) into its felt counterpart. Skip middling values or call them neutral; don't invent drama.
4. **Synthesize** one paragraph: what the picture does to a body looking at it. Where weight rests, what the open space does, whether the edges press or hold, whether the image settles or keeps tension.
5. **Name the governing principle**: the one Bang idea that most explains this reading.
6. **Limits:** one image; a reproduction; felt readings are interpretation, not measurement; meaning and subject are outside the kernel.

## Output

```text
PICTURE THIS × VTL  (measured | approximate)
Values vs reference: Δx … (pXX) · Δy … · r_v … · μ … · xₚ … · SDI … · θ …
Felt reading (interpretation):
- <principle>: <one or two sentences>
- …
The picture as a body feels it: <one paragraph>
Governing principle: <one>
Limits: <single image, reproduction, interpretation>
```

## Voice

Use bodily, spatial language: weight, pressure, breath, gravity, escape, confinement, rest, precariousness. No aesthetic verdicts (beautiful, successful, dynamic). If a value sits on a boundary, give both readings.

## Source

Molly Bang, *Picture This: How Pictures Work* (Chronicle Books, rev. ed. 2016). The principles here are paraphrased. Read the book; it's short and wonderful.
