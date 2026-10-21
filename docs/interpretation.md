# Reading the numbers

VTL is a coordinate system, not a grading rubric. A thermometer reading 0 °C isn't good or bad; it tells you where the water is. Kernel values work the same way: they say *where* a composition sits in structural space, not whether it should sit there.

## The center is not the problem

A photographer who centers a portrait has made a choice. A model that centers *everything*, whatever the prompt, has a default. One image can't tell these apart. A set of images can.

| | Δx | μ | xₚ | θ | reads as |
|---|---|---|---|---|---|
| portrait | 0.00 | 0.85 | 0.35 | 0.65 | centered, unified, aligned |
| landscape | −0.25 | 0.30 | 0.60 | 0.12 | off-center, distributed, edge-engaged |
| street | 0.15 | 0.15 | 0.55 | 0.08 | asymmetric, fragmented, peripheral |

All three are valid. VTL places them; it doesn't rank them.

## No single score equals collapse

Collapse isn't a value. It's **low variance across varied input.** If six hundred images about six hundred different things all land within Δx ∈ [−0.05, 0.05] and μ ∈ [0.01, 0.08], the maker is exploring a very small part of the space. That's what `vtl.fingerprint` is for: look at `window_width`, `walls` and, with prompt groups, `vtl.rigidity`.

## Intent can't be read from one image

Low cohesion might be a street photographer's chosen chaos or a model's failure to unify. An omnidirectional field might be Pollock or default texture noise. Across a body of work, **variance patterns reveal authorship**: wide means the maker chooses, tight means the maker defaults.

## Silence is also a signal

If a model *never* produces Δx < −0.3, or μ > 0.7, or θ > 0.5, those regions of compositional space are unreachable for it, whatever you prompt. People collectively cover them. A missing region is a finding.

## Questions worth asking

- **Variance:** does this maker explore structural space, or sit in one spot?
- **Prompt response:** do different prompts map to different coordinates (`rigidity`)?
- **Cross-maker:** do different engines, versions or artists occupy different regions (`compare`)?
- **Decoupling:** if semantic diversity is high (say, by CLIP) while structural diversity is low, content and structure have come apart. That's the signature of a learned spatial prior.

## Reporting

- Report `r_v` alongside `gradient_floor_85` and `gradient_ceiling_97`. The *tail gap* (ceiling − floor) tells "quiet frame with a few hard accents" (big gap) from "edge energy everywhere" (small gap).
- Compare `r_v` freely within one engine. Across engines, add context: it uses an absolute threshold on purpose.
- Use `window_width` rather than CV for signed, near-zero metrics like Δx and Δy.
- Always say which `kernel_version` you used and whether `diffusion` was on.

*Further reading:* Arnheim, *Art and Visual Perception* (structural description before judgment); CIE L\*a\*b\* and OKLab as coordinate systems that don't rank colors; Stevens and signal detection theory for measuring separately from preference.
