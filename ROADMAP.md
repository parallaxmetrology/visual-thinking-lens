# Roadmap

Rough order. Anything here is open for help. Comment on the matching issue first.

## Next for this instrument

- **Engine atlas.** A `fingerprints/` folder of contributed CSVs (one per engine, version or artist) and a page in the demo that plots them together. The fastest way for the project to learn something new.
- **Port the six-layer readout** (RCA, VCLI-G × SCI perceptual load, tonal architecture, multi-island resistance graph) as `vtl.readout`.
- **Port the perceptual mask suite** (opponency, cone ceiling, zone system, DoG blobs, orientation field…) as `vtl.masks`, each mask a pure function.
- **Color × structure joint metrics** (`compute_joint`, `regime_tags`). First decide whether they're re-based on Canon 3 or kept as a named variant ([lineage](docs/lineage.md)).
- **Noise-sensitivity sweep** from the fingerprint notebook: which metrics read real structure and which read artifacts.
- Fix the known sharp edges ([known-issues](docs/known-issues.md)) as an opt-in `canon4` without breaking `canon3-v8`.

## Meet people where they work

- **ComfyUI node:** measure every generation inline; plot the kernel across a batch.
- **Hugging Face Space:** hosted demo for people who won't install anything.
- **Agent skill / MCP server:** let Claude and other assistants call `vtl measure` and read results with the interpretation guide (a starter skill lives in `skills/`).
- **GitHub Action:** "composition regression" for model teams. Measure a fixed prompt set on each model version and flag drift in the fingerprint.
- **Evaluation libraries:** propose VTL as a metric in existing text-to-image evaluation harnesses.

## Elsewhere in Parallax Metrology

Each domain instrument gets its own repository built from the same pattern: notebook-faithful package, golden tests, CLI, demo. See [parallaxmetrology.com](https://www.parallaxmetrology.com) for the full family. Language-model telemetry (the Linguistic Kernel) is next.
