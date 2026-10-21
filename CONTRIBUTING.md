# Contributing

Thanks for looking. This project grows when people measure things and argue about what they find, so all of the following count as contributions.

## Ways in

**Share a fingerprint.** Measure a set of images (an engine, a model version, a prompt set, an artist's body of work) and open a [Discussion](https://github.com/parallaxmetrology/visual-thinking-lens/discussions) or a *Fingerprint* issue with:

- the CSV from `vtl measure folder/ -o out.csv`
- how the images were made (engine and version, prompts or prompt source, count, settings)
- what surprised you

You don't need to share the images themselves if you can't.

**Report a wrong reading.** If the numbers clearly disagree with what the image is doing, open a *Wrong reading* issue with the image (or a description), the output, and what you expected. These are the most useful reports we get.

**Port an instrument.** Several research instruments are still notebook-only. Issues labeled `port` describe each one, its source notebook, and what "done" looks like.

**Implement elsewhere.** A JavaScript, Rust or Julia kernel that reproduces `tests/golden/kernel.json` is very welcome.

## Development

```bash
git clone https://github.com/parallaxmetrology/visual-thinking-lens
cd visual-thinking-lens
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## The one firm rule: don't move the ruler silently

The kernel is a measuring device. Results are only comparable if the device doesn't change.

- **Bug fixes, speedups, refactors:** fine, as long as `tests/test_golden.py` still passes unchanged.
- **Anything that changes a number** (a threshold, a resize, a mask rule): propose it in an issue first. If accepted, it ships as a new `kernel_version` with regenerated golden files and a CHANGELOG entry that explains the difference. The old behavior stays reproducible.
- New metrics are welcome as **additional** keys or new modules. Don't redefine existing ones.

## Style

- Plain functions over classes; NumPy in, dicts or DataFrames out.
- Docstrings say what a number *reads*, not whether it's good.
- Run `ruff check` before opening a PR.

## Conduct

Be kind and specific. Disagree with numbers, not people. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
