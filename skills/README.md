# Agent skills

Skills that teach an AI assistant (Claude Code, Claude, or any agent that reads `SKILL.md` folders) to run VTL and read its numbers carefully, plus one that steers image generators.

| skill | what it does |
|---|---|
| [`composition-critique`](composition-critique/) | feedback on one picture against what it's meant to do: measured facts, then crops and value moves whose effect is measured (crops before you suggest them, edits with `--compare`) |
| [`deformation-operators`](deformation-operators/) | prompts that make an image generator deform a body on purpose (coil, stretch, twist, arc, wave) without ropes, extra limbs or snapping back; GPT, Gemini, Midjourney and SDXL recipes. No measurement; [example images](https://parallaxmetrology.com/deformation_operator_playbook) |
| [`vtl`](vtl/) | measure images, gate on QA, read one image or a whole set; priors and center collapse at the right strength |
| [`vtl-color`](vtl-color/) | value and color structure: light/dark placement, chroma, hue breadth, palette |
| [`vtl-radial`](vtl-radial/) | RCA-2: is the composition organized around the frame center or around its own mass? |
| [`vtl-picture-this`](vtl-picture-this/) | translate a reading into felt compositional language after Molly Bang's *Picture This* |
| [`measurement-claim-auditor`](measurement-claim-auditor/) | check captions, reports and posts for claims bigger than their evidence |

The measuring skills read values against real ranges ([`vtl/references/reference-ranges.md`](vtl/references/reference-ranges.md), built from [`fingerprints/`](../fingerprints/) by `tools/reference_ranges.py`) rather than fixed cutoffs.

## Install

Claude Code: copy a skill folder into `~/.claude/skills/` (all projects) or `.claude/skills/` (one project).

```bash
cp -r skills/composition-critique skills/vtl skills/vtl-picture-this skills/measurement-claim-auditor ~/.claude/skills/
```

The measuring skills call the `vtl` command, so install the package too (`deformation-operators` needs nothing):

```bash
pip install git+https://github.com/parallaxmetrology/visual-thinking-lens
```
