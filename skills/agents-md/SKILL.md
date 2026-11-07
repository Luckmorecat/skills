---
name: agents-md
description: Create, audit, or simplify AGENTS.md when repository instructions need writing, review, or a fix for recurring agent mistakes.
---

# AGENTS.md

Make repository instructions useful for the requested work. No change is a valid
outcome; neither brevity nor a particular file layout proves effectiveness.

## Establish scope

- Audit/review means inspect and propose, without editing. Create/update means
  edit the requested files. Ask only when intent or a consequential choice is
  unresolved; publishing is a separate action.
- Start with the relevant instruction chain, linked procedures, and configuration
  for the task or reported failure. Expand inspection only to resolve a specific
  gap; do not inventory the whole repository by default.
- Identify the target agent's discovery and inheritance rules before placing
  instructions in nested files. Separate user requirements from recommendations.

## Write or assess

- Preserve required constraints, including unusual ones. Verify suspected stale
  rules against their source; ask about unresolved conflicts instead of silently
  discarding either requirement.
- Give each instruction a concrete trigger and action. Keep shared rules at the
  root and local rules in their applicable scope, without duplicating them.
- Link existing procedures with a clear trigger rather than copying their body.
  Check that links, commands, and required tools are valid in this repository.
- Include non-obvious decisions and demonstrated failure prevention, not a tour
  of discoverable code. Keep research, task history, and temporary plans outside
  always-loaded instructions. Do not fill a template or impose a line limit.
- Make the smallest useful change; leave unrelated skills and configuration alone.

## Verify and report

Check the diff against required constraints, applicable scopes, reference targets,
and authoritative commands. For changed behavior, walk through a representative
request and an important boundary case. Do not execute destructive or external
actions just to test their instructions.

Report edits or proposals, checks actually performed, and remaining uncertainty.
A static review or smoke test is not proof of improved agent performance. When
that claim matters, compare baseline and candidate on fixed representative tasks
in fresh sessions with the same model, tools, permissions, and budget; score task
correctness, adherence, and cost separately. Preserve safeguards in both arms.
