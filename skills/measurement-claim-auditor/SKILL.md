---
name: measurement-claim-auditor
description: Audit captions, reports, papers, slides, posts or agent outputs that make claims from image measurements (VTL kernel, color, radial compliance, fingerprints) or any deterministic metric, before they are published or relied on. Use when checking whether a claim overreaches its evidence: quality or preference claimed from structure, model priors from one image, comparisons without matched settings, causal language, ignored QA failures, or centered composition treated as collapse. Rewrites risky claims into scoped, evidence-linked statements.
---

# Measurement Claim Auditor

Keep claims the size of their evidence. This skill audits language; it doesn't rerun measurements. If evidence is missing, say what would be needed.

## Inputs

- The text: caption, report section, paper, slide, post or agent output.
- Any evidence: metric rows, CSVs, QA fields, group sizes, settings, overlays.
- The audience, if known (public, artist, research, engineering, client).

With text only, audit the claim *form* and list evidence gaps. Don't rule on whether the analysis is true.

## Workflow

1. **Split into claims.** Label each: structural, distributional/prior, comparison, prompt-response, causal, or quality/preference.
2. **Match evidence.** Name the metric, QA field, group summary or overlay behind each claim. No evidence means unsupported.
3. **Check scope.**
   - One image supports local description only.
   - Priors, collapse and monoculture need comparable sets, with sizes stated.
   - Comparisons need matched kernel version, machine, `diffusion` setting, similar resolutions, and QA parity.
   - Prompt-response claims need prompts with several images each (`vtl.rigidity`).
4. **Check boundaries** (see [overclaim-patterns.md](references/overclaim-patterns.md)).
5. **Grade each claim.** *Blocker*: don't use as written. *Major*: needs real scoping. *Minor*: imprecise wording. *Clean*.
6. **Rewrite** (see [revision-language.md](references/revision-language.md)). Keep the intent, remove the overreach, add scope and evidence. Never make a claim *stronger* in a rewrite.

## Output

```markdown
**Claim audit:** <clean | usable with revisions | blocked>

| Severity | Claim | Issue | Safer version |
|---|---|---|---|

**Evidence gaps:** <what would be needed>
**Boundary notes:** <the limits that matter for this text>
**Revised text:** <if useful>
```

## Hard stops

- Structure alone never establishes quality, preference, beauty, intent, or meaning.
- One image never establishes a model prior, collapse pattern, or default.
- QA failures (FAIL rows, invalid masks, mixed versions) aren't footnotes. If they were ignored, the claim is blocked.
- "Causes", "proves" and "shows that the model…" become "is consistent with", "supports", or "in this set".
- A single metric doesn't carry a composite claim. Name the composite.
- Centered ≠ collapsed. Centered by one body and centered by balance are different findings.
- Every number describes a reproduction (object × reproduction chain × resolution), not the object itself.
