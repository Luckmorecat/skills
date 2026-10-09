# Plan format

Honor a supplied destination. Otherwise create an unused directory under `${STRIKER_ROOT:-${XDG_STATE_HOME:-$HOME/.local/state}/striker}/plans/<repo>/<slug>-<date>/`, using the repository name, a short feature slug, and an ISO date.

```text
<plan>/
  plan.md              shared context and the generated status block
  01-<slug>.md         one file per slice
  02-<slug>.md
  state.json           run state
  log.md               history
  checkpoints/<ID>.md  a started slice's checkpoint
  worktrees/<ID>/      a slice's worktree from `plan start --worktree` (see `plan start --help`)
```

Agents write the prose: `plan.md` outside its status block, the slice files, and the checkpoints. The `plan` CLI in this skill's `bin/` writes `state.json`, the status block, and `log.md`, and creates and removes worktrees. Run state (repository and target branch, slice status, dependencies, baselines, landed revisions, worktrees, scheduling constraints, the autonomy grant, and the decision index) changes only through `plan`; `plan --help` documents its commands and the `state.json` fields.

## plan.md

Keep the shared context self-contained: agreed outcomes, constraints, exclusions, and consequential decisions with their approval or delegation status, with source references when available, including the absolute path of a source contract. Record delegated discretion with its constraints and any precedence rules, so execution settles the choices they cover without asking. When a prototype reference settles the interface or logic, carry its pinned reference and kind, what it settles and leaves open, and its `D<n>` ledger with IDs and status. Record the remote when available and any branch or worktree convention; `plan init` records the repository root, target branch, and planning revision. Separate verified facts from assumptions.

The generated status block lists every slice with its file, outcome, dependencies, and status between its `plan:status` markers. Leave the block and its markers to `plan`. IDs remain stable; dependencies determine execution order. Name the behavior or evidence each dependency supplies. `plan` refuses missing dependencies and cycles, and `plan validate` checks the whole plan; check that every agreed outcome is covered.

Statuses are `ready`, `in-progress`, `blocked`, and `complete`. A ready slice is fully described; it can start only after its dependencies complete. Mark a slice blocked when a missing decision or evidence prevents describing or executing it, with a reason naming what resolves that blocker. An unfinished dependency alone does not make a slice blocked.

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

Include slice-specific constraints and exclusions where needed. A `## Notes` section holds findings earlier slices recorded for this one; keep it when revising. Carry forward acceptance identifiers when the input has them. Add code pointers or snippets only when they preserve a decision or materially help navigation; distinguish inspected code from proposed structure. Verification describes observable proof; include commands when known and recheck them during execution.

## checkpoints/<ID>.md

The checkpoint of a started slice, kept by the skill executing it. `plan start` creates it when missing; a reconciler or the record of a paused slice's next action may write it earlier. `plan complete` and `plan land` fold it into `log.md` with the slice's evidence and delete it.

## log.md

History only, appended by `plan`: a dated entry for each lifecycle transition (start, block, resume, complete, land), import, decision, grant, constraint, target-tip change, forced override, and slice change given `--note`, holding the prose passed to it, such as a slice's evidence and folded checkpoint, a decision's body, or the note. `plan init` and a `plan slice add|edit` without `--note` log nothing.

## Plans in the previous format

A plan directory without `state.json`, whose `plan.md` holds the slice table `| ID | File | Outcome | Blocked by | Status |`, is in the previous format. Run `plan import <dir>` before reading or changing its state; it converts the table into `state.json` and the status block, and moves `log.md`'s checkpoint section into `checkpoints/<ID>.md`. See `plan import --help` for what it reads and refuses.
