# Metric guide (kernel `canon3-v8`)

Coordinate convention: image space, origin top-left. Negative Δy = **upper** frame.

| key | what it measures | reading |
|---|---|---|
| `delta_x` | horizontal offset of the mass centroid, −0.5…0.5 | − left, + right, ≈0 centered |
| `delta_y` | vertical offset of the mass centroid, −0.5…0.5 | − upper, + lower, ≈0 centered |
| `r_v` | 1 − share of pixels with gradient ≥ 0.15 (absolute) | high = gradient-quiet field; **not** "empty space" by itself |
| `gradient_floor_85` | 85th-percentile gradient magnitude | how activated the whole field already is |
| `gradient_ceiling_97` | 97th-percentile gradient magnitude | strength of the hardest edges |
| `tail_gap` | ceiling − floor (compute it) | big = quiet field with a few strong edges; small = edge energy spread evenly |
| `rho_r` | 100 × mask area ÷ convex-hull area | ≈ 100 × `mass_fraction` when mass spans the frame; rises when mass is confined |
| `mu` | p_max × (1 − H/H_max) over 8-connected component sizes | high = one dominant body; low = fragments or equal-sized parts (a diptych reads low) |
| `x_p` | share of gradient energy in the outer 15% band | high = active edges; low = energy held inward |
| `theta` | 1 − normalized entropy of 8-bin orientation histogram on the mask | high = one dominant direction; low = omnidirectional |
| `d_s` | mean stroke thickness along the mask skeleton ÷ min(h, w) | thicker vs thinner structure |
| `sdi` | mean distance of mask pixels from their centroid ÷ diagonal | low = gathered; high = spread |
| `mass_fraction` | share of pixels in the mask | device context (≈12% by construction), not composition |

## Reading against the reference

Values live in narrow bands (see [reference-ranges.md](reference-ranges.md)). Say where a value sits, e.g. "μ is in the top 5% of the reference set" or "SDI is near the median". Don't use cutoffs like "θ > 0.7".

## Composite reads

- **One body in the middle:** Δx, Δy near 0; μ high for the reference; SDI low; xₚ low.
- **Centered by balance:** Δx, Δy near 0; μ low; SDI high. Mass sits on several sides and averages to center.
- **Distributed, edge-engaged:** SDI and xₚ high; μ low; placement may be anywhere.
- **Quiet field with accents:** r_v high, floor low, tail_gap high.
- **Activated field:** r_v low, floor high. The r_v drop comes from global edge activity, not packing.

## Allowed vs blocked (one image)

Allowed: "the mass centroid sits upper-left", "the field is gradient-quiet under the absolute threshold", "mass is broadly dispersed relative to the reference".

Blocked: "this proves collapse", "the model has a prior", "the composition is good/bad", "the prompt failed", "the subject is X".
