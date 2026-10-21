# Bang principles ↔ kernel values

These are **analogies**: each kernel value is a geometric fact, and the felt reading is a reasonable translation, not a measurement of feeling. Bands are quartiles of the reference set (`skills/vtl/references/reference-ranges.md`, 279 images), approximate as of the current fingerprints.

| principle (paraphrased from Bang) | kernel value | low (≤ p25) | high (≥ p75) |
|---|---|---|---|
| **The center is the most stable spot; distance from it adds tension.** | `delta_x`, `delta_y` (for placement, "near" = inside the p25–p75 window, "far" = outside p05–p95) | near center (Δx within ≈ −0.03…0.02): stable, held, possibly trapped | far from center (Δx beyond ≈ −0.08 or 0.07; Δy outside ≈ −0.09…0.20): precarious, escaping, unfinished |
| **The upper half feels lighter, freer, more precarious; the lower half heavier, more grounded.** | `delta_y` (negative = upper) | below ≈ −0.01: weight lifted, airy or unstable | above ≈ 0.10: weight sinking, grounded, settled or burdened |
| **Edges and corners carry tension; a picture pressing at its frame feels like something leaving or arriving.** | `x_p` | below ≈ 0.40: energy held inward, self-contained | above ≈ 0.52: edges alive, pressure at the frame, escape or containment stress |
| **Open space is active, not neutral; it gives breath or isolation.** | `r_v` with `tail_gap` | below ≈ 0.62: crowded, little breath | above ≈ 0.87: much quiet; with a high tail_gap (≥ 0.44), a few hard accents in silence |
| **One large shape reads as power; many equal shapes spread attention.** | `mu` | below ≈ 0.002: no single body leads; attention is distributed | above ≈ 0.066 (and especially ≥ 0.27): one body dominates the field |
| **Gathered shapes press together; scattered shapes dissolve or expand.** | `sdi` | below ≈ 0.22: gathered, compressed, focused | above ≈ 0.26: spread, expansive, dissolving |
| **Diagonals and strong directions imply motion; no direction implies rest or indecision.** | `theta` | below ≈ 0.002: no declared direction (rest or diffusion) | above ≈ 0.018 (and especially ≥ 0.06): a dominant direction, implied movement |
| **Thick, rounded forms feel safe; thin, sharp forms feel threatening.** | `d_s` | below ≈ 0.0016: thin, sharp, wiry | above ≈ 0.0020: broad, heavier strokes |

## Notes

- Middle-band values (p25–p75) are neutral; say so rather than forcing a reading.
- Shape *type* (pointed vs round) isn't measured directly. `theta` and `d_s` are partial proxies, so phrase them cautiously.
- Combine before concluding: centered + high μ + low SDI is one body held at center (stable, maybe static); centered + low μ + high SDI is balance across the field (calm through counterweight). Same placement, different feeling.
- Color and value change the felt weight a lot (a small dark shape can outweigh a large pale one). If `vtl-color` was run, use light/dark placement too.
