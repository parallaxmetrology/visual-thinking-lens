# Known issues and sharp edges

Things the instrument does that you should know about before trusting a number. Each one is reproduced faithfully from the reference notebooks, so changing it would be a new kernel version. Discussion is welcome in the linked issues.

## 1. The mask reads mid-strength structure, not silhouettes

The mass mask keeps gradients between the image's own 85th and 97th percentiles. The strongest 3% of edges are excluded on purpose, so that a few hard specks don't dominate. A consequence: **a crisp, flat shape on a quiet ground is measured mostly by the ground's faint texture, not by its outline.**

| synthetic test (900×600, disc on the right) | Δx | mask QA |
|---|---|---|
| flat ground, flat dark disc | −0.002 | FAIL (see #2) |
| faint noise ground, flat dark disc | +0.000 | WARN |
| faint noise ground, *textured* disc | +0.115 | WARN |

Real photographs and paintings almost always have enough texture that this works as intended. Flat vector art, logos, and heavily denoised minimal renders are where to be careful. Check with `vtl overlay`.

## 2. Perfectly flat images read as "all mass"

With zero gradient everywhere, both percentile thresholds are 0, so every pixel passes and the kernel returns `valid = 1` with `mass_fraction ≈ 0.99`. **Mask QA catches it** (`mask_status = FAIL`, "too much structure"). Filter on `mask_status != "FAIL"` in batch work.

## 3. CV is misleading for signed metrics near zero

`fingerprint` labels spread by CV = std/|mean|. For Δx and Δy, whose means sit near 0, CV explodes and everything reads "wide". Use `window_width` (p90 − p10) or `std` for those axes.

## 4. Small images are upscaled

The kernel always resizes the long side to 1536 px, *upscaling* smaller images with bicubic interpolation. That smooths gradients and can shift `r_v` and `d_s`. Compare images at similar native resolutions where possible, and record native size.

## 5. Different instruments, different masks

The kernel, color and radial instruments each use the mask and decode path of their own reference notebook (gradient band; OKLab percentile regions; edge + Otsu hybrid). Their centroids won't match exactly, and that's expected. Don't mix `delta_x` from the kernel with `dx` from RCA-2.

## 6. "Same image, same numbers" holds per platform, not across CPUs

On one machine and one set of library versions, the kernel is fully deterministic: same image, same mask hash, same numbers. **Across CPU architectures it is not bit-identical.** OpenCV's resize and Sobel take different SIMD paths on Apple Silicon and on x86-64, and that flips about 0.5% of kernel mask pixels at the percentile thresholds. Measured on the sample images (`tools/golden_diff.py`, macOS arm64 vs Linux x86-64):

| metric | max difference |
|---|---|
| Δx / Δy | 0.0002 / 0.0003 |
| μ | 0.001 (large *relative* change on very fragmented masks) |
| θ | 0.0015 |
| ρᵣ | 0.07 |
| xₚ, SDI, rᵥ | < 0.0001 |

Radial compliance matched exactly; the color kernel agreed to about 1e-7.

None of this changes how an image reads, but it does mean `mask_sha256` only matches on the same platform. The golden tests are strict (1e-7) on the reference platform (macOS arm64) and use these measured tolerances elsewhere. For a study, measure every image on the same machine and record `kernel_version` and library versions. OpenCV, scikit-image and SciPy updates can shift values too. If the drift report grows after a dependency bump, report it.
