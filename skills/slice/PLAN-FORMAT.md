# Plan format

Honor a supplied destination. Otherwise create an unused directory under `${STRIKER_ROOT:-${XDG_STATE_HOME:-$HOME/.local/state}/striker}/plans/<repo>/<slug>-<date>/`, using the repository name, a short feature slug, and an ISO date.

```text
<plan>/
  plan.md
  01-<slug>.md
  02-<slug>.md
  log.md
```

## plan.md

Keep the shared context self-contained: agreed outcomes, constraints, exclusions, and consequential decisions, with source references when available. Record the repository root, remote when available, branch/worktree, and planning revision (or `unborn`). Separate verified facts from assumptions.

List every slice in a compact table:

| ID | File | Outcome | Blocked by | Status |
| --- | --- | --- | --- | --- |
| 01 | 01-<slug>.md | Observable result | None | ready |
| 02 | 02-<slug>.md | Observable result | 01 | ready |

This table owns dependencies and status. IDs remain stable; dependencies determine execution order. Name the behavior or evidence each dependency supplies. Check that every dependency exists, the graph has no cycles, and every agreed outcome is covered.

Use `ready`, `in-progress`, `blocked`, or `complete`. A ready slice is fully described; it can start only after its dependencies complete. Mark a slice blocked when a missing decision or evidence prevents describing or executing it, and record what resolves that blocker. An unfinished dependency alone does not make a slice blocked.

## Slice files

Create one file per slice. A blocked slice records what is known and its unresolved gap; keep speculative requirements visibly unresolved.

```markdown
# 01 — <Title>

## Outcome
<The behavior this slice delivers.>

## Acceptance
- [ ] <Observable success example.>
- [ ] <Relevant boundary or failure example.>

## Verification
<How to demonstrate acceptance, including any required integration check.>
```

Include slice-specific constraints and exclusions where needed. Carry forward acceptance identifiers when the input has them. Add code pointers or snippets only when they preserve a decision or materially help navigation; distinguish inspected code from proposed structure. Verification describes observable proof; include commands when known and recheck them during execution.

## log.md

Keep a current checkpoint with the active slice, original starting revision, pre-existing dirty snapshot, owned changes, verification/review evidence, landed revisions, and blocker or next action. Initialize it as not started. Append concise history at checkpoints; completed claims require evidence.

When revising a plan, retain completed work, IDs, and recovery state; record the reason for changed unfinished work. Existing plans using `contract.md`, `spine.md`, and `map.md` can retain their layout. Update their equivalent fields in place rather than forcing a migration.
