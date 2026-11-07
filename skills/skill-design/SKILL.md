---
name: skill-design
description: Create, revise, or evaluate reusable agent skills when a workflow needs packaging or an existing skill misroutes or produces poor results. Not for ordinary task execution or repository AGENTS.md rules.
---

# Skill design

Build a skill around an observable workflow need, not a collection of generic
advice. A narrower change, an existing skill, or no new skill may be sufficient.

## Scope the work

- Audit/evaluate means inspect and report; create/update permits the requested
  edits, not installation or publication. Preserve user constraints and existing
  invocation policy unless a change is requested.
- Inspect the destination's skill format and nearby conventions, the current
  skill and its callers, and relevant task examples. Do not search every skill
  or rewrite neighboring workflows without a concrete reason.
- Establish the intended result, when the skill should activate, a near-miss
  request it should not capture, and tools or inputs it actually needs. Infer
  these from available context; ask only about consequential missing decisions.

## Design the candidate

- Describe the capability and trigger in discoverable metadata. Avoid catchall
  language that competes with unrelated skills; distinguish likely overlaps.
- Keep the entrypoint focused on decisions that change behavior: outcome, scope,
  non-obvious constraints, and stopping conditions. Match detail to risk rather
  than prescribing a universal length or rigid sequence.
- Link conditional detail only where needed. Add scripts for repeatable mechanics
  when they improve reliability; do not add references or scaffolding without a
  use. Verify dependencies exist in the target environment and provide a safe
  fallback or explicit blocker when essential inputs or tools are unavailable.
- Keep examples separate from requirements. Do not turn one incident into a
  universal rule, copy a research summary into runtime instructions, or treat
  benchmark gains as a guarantee for this workflow.

## Evaluate and iterate

Use [EVALUATION.md](EVALUATION.md) when planning behavioral tests or making an
improvement claim. For a small edit, format validation, reference checks, and a
representative walkthrough may suffice; label those checks accurately.

Test new scripts on safe fixtures. Check metadata, references, discovery intent,
required constraints, and unauthorized side effects as well as task outcomes.
Revise only for observed failures or a clear requirement, then rerun affected
cases. Report the change, actual checks and outcomes, and untested boundaries.
