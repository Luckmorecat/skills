# Plan format

Write a new plan outside the repository using `STRIKER_ROOT`. When revising a supplied plan, update its existing directory and preserve recovery state.

```bash
striker_root="${STRIKER_ROOT:-${XDG_STATE_HOME:-$HOME/.local/state}/striker}"
if repo_root=$(git rev-parse --show-toplevel 2>/dev/null); then
  repo=$(basename "$repo_root")
else
  repo=$(basename "$PWD")
fi
slug="oauth-device-flow"   # replace with a short kebab-case summary
mkdir -p "$striker_root/plans/$repo"
mkdir "$striker_root/plans/$repo/$slug-$(date +%F)"
```

Create the leaf without `-p`; if it exists, choose a more specific slug. Always create a directory, including for single-slice work:

```text
<plan>/
  contract.md
  spine.md
  map.md
  01-<slug>.md
  log.md
```

## contract.md

Keep a complete snapshot of the approved input, including its source path. Refresh it only from an approved amendment. The slicer uses it for coverage; executors load it only when the slice and shared constraints leave a specific requirement unclear.

## spine.md

Every session reads this. Keep active shared constraints here, slice-local details in their slice, and history in the log.

- **Goal** — outcome and source contract path, written out so the plan stands alone.
- **Identity** — repository root and remote when available, branch/worktree, and planning revision (or `unborn`). Record deliberate checkout changes when work moves.
- **Evidence state** — established, sparse, or blank, with inspected scope.
- **Shared contract** — actor or caller, global constraints/exclusions, and shared approved decisions. Keep the full acceptance catalogue in `contract.md`; carry relevant examples into each slice without changing their meaning.
- **Implementation assumptions** — active shared `A<n>` facts with `file:line` and inspected revision; `D<n>` defaults with reason and reversal cost. Keep these distinct from approved intent.
- **Out of scope** — considered exclusions.
- **Milestones** — ordered outcomes covering every acceptance ID, dependencies, integrated acceptance checks, and stable slice IDs with `outline`, `ready`, `in-progress`, `blocked`, or `complete` status. Outline later work without speculative paths or commands; `slice` alone marks work ready.
- **Deferred decisions** — `U<n>`, unknown, dependent work, resolver, and evidence or milestone due before that work starts.
- **Execution** — selected/next ready slice and dependency order; one slice per invocation by default, with any user-authorized continuation bound. Continuation ends when no prepared slice remains.

## map.md

Navigation saves search, not reading. Verify paths before relying on them.

- **Existing traversal** — inspected flow and revision; `None` for blank projects.
- **Planned traversal** — intended paths, explicitly unverified until created and checked.
- **Shared paths** — files several slices touch and why.
- **Ruled out** — eliminated paths and reasons.

## NN-\<slug\>.md

Create files only for ready slices. Keep IDs stable; milestone order and dependencies determine execution, not filename order.

- **Build** — behaviour to deliver.
- **Acceptance** — applicable contract IDs and their success/boundary examples, relevant constraints and decisions. Include enough detail to execute without loading the full catalogue. Enabling changes prove compatibility; experiments name the question, limit, and required evidence.
- **Prerequisites** — dependencies and resolved unknowns; discoveries requiring a new decision.
- **Exclusions** — adjacent work reserved for later slices.
- **Paths** — `Read`, `Create`, or `Modify`, with purpose; include slice-local assumptions/defaults here.
- **Verify** — commands with sources and observable results proving acceptance. Missing commands are `to create` work in Build. Include integrated acceptance when this slice completes a milestone.

## log.md

Initialize current state; executors update it before work and after checkpoints, keeping milestone status in sync. Load historical entries only when relevant. Preserve existing baselines and evidence when replanning unfinished work.

```markdown
# Log

## Current

- Slice: <next ID>
- Status: ready
- Starting revision and pre-existing dirty snapshot: not started
- Owned changes, landed revisions, verification/review evidence: none
- Blocker or next action: <first action>

## History

Append per slice: ID, status, landed revisions, evidence, deviations and reasons, next dependencies.
```

Statuses are `ready`, `in-progress`, `blocked`, and `complete`. A log entry alone never proves completion: record acceptance/check results, resolved review findings, and landed revisions. For an experiment with no code changes, record its result and unchanged revision.

Record plan revisions and approved contract amendments with the previous decision, replacement, reason, and authorization where needed. Keep completed evidence intact. If history grows large, move older entries to `archive.md`; read it only for needed decision or recovery evidence.
