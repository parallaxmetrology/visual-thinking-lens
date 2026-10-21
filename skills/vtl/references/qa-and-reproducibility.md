# QA and reproducibility

## Per-row gates

| field | value | what to do |
|---|---|---|
| `valid` | 0 | report why (`quality_note` or `error`); interpret nothing |
| `mask_status` | FAIL | interpret nothing; flat or near-empty images land here |
| `mask_status` | WARN | read with the named reason (sparse mask, island soup, texture-driven) |
| `mask_mode` | TEXTURE_FIELD | normal; describe field behavior, not objects |
| `mask_mode` | REGION_FIELD | one component holds ≥ 25% of mass; object-like reads are reasonable |
| `quality_note` | non-empty | low-structure band (mass 0.1–3%); lower confidence |

`vtl.fingerprint`, `rigidity` and `compare` already drop `valid = 0` and FAIL rows. In a report, still say how many were dropped.

## Batch checks

- Report the counts of PASS/WARN/FAIL and REGION/TEXTURE. Don't hide them behind averages.
- If one group is mostly TEXTURE_FIELD and another mostly REGION_FIELD, say so: it changes what the numbers describe.
- Object-placement claims over a mostly TEXTURE_FIELD set are an overclaim.

## Reproducibility

- Same image, same machine, same library versions: identical numbers and identical `mask_sha256`. Different values on a re-run means something changed. Check the version, the `diffusion` setting, the decode path, and dependencies.
- **Across CPU architectures the kernel is not bit-identical.** Apple Silicon vs x86-64 differ by up to about 0.0003 in Δx/Δy and 0.001 in μ, and mask hashes won't match. Don't treat that as drift. For a study, measure everything on one machine and record `kernel_version` and library versions.
- `sha256` is the hash of the input file: identical files give identical hashes. It's the right key for spotting duplicates.
- Don't compare across `kernel_version`s or `diffusion` on/off without saying so.

## Run status

- **PASS:** QA fields present, failures excluded or reported, one platform, consistent version.
- **WARN:** WARN-heavy, texture-dominant with object language, missing version or platform notes.
- **FAIL:** FAIL rows used as evidence, a mixed-version comparison presented as clean, unexplained same-machine drift.
- **UNKNOWN:** not enough metadata to tell.
