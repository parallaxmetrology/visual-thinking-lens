# Agent skills

Skills that teach an AI assistant (Claude Code, Claude, or any agent that reads `SKILL.md` folders) to run VTL and read its numbers carefully.

| skill | what it does |
|---|---|
| [`vtl`](vtl/) | measure images, gate on QA, read one image or a whole set; priors and center collapse at the right strength |
| [`vtl-color`](vtl-color/) | value and color structure: light/dark placement, chroma, hue breadth, palette |
| [`vtl-radial`](vtl-radial/) | RCA-2: is the composition organized around the frame center or around its own mass? |
| [`vtl-picture-this`](vtl-picture-this/) | translate a reading into felt compositional language after Molly Bang's *Picture This* |
| [`measurement-claim-auditor`](measurement-claim-auditor/) | check captions, reports and posts for claims bigger than their evidence |

All of them read values against real ranges ([`vtl/references/reference-ranges.md`](vtl/references/reference-ranges.md), built from [`fingerprints/`](../fingerprints/) by `tools/reference_ranges.py`) rather than fixed cutoffs.

## Install

Claude Code: copy a skill folder into `~/.claude/skills/` (all projects) or `.claude/skills/` (one project).

```bash
cp -r skills/vtl skills/measurement-claim-auditor ~/.claude/skills/
```

The skills call the `vtl` command, so install the package too:

```bash
pip install git+https://github.com/parallaxmetrology/visual-thinking-lens
```
