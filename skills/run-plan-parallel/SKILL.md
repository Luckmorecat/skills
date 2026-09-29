---
name: run-plan-parallel
description: Run a slice plan through parallel subagents in isolated worktrees, integrating each verified slice and reconciling blockers.
disable-model-invocation: true
---

Orchestrate the supplied plan through completion, running independent slices concurrently in isolated worktrees. Use its established path or ask when absent. Keep your work to scheduling, dispatching subagents, routing their reports, and communicating with the user; delegate all inspection, implementation, verification, integration, and file changes.

Only one subagent at a time writes the plan directory, apart from each worker's worktree and `checkpoints/<ID>.md`; serialize those dispatches while workers run alongside. When a subagent returns assignments because nested delegation is unavailable, dispatch them, sequentially if capacity requires, and relay the results before resuming it.

## Inspect

Start with an inspection subagent: read the plan and checkpoints, check repository state, and identify interrupted work, including integrations, existing slice worktrees, and eligible slices. Use the existing plan and log as the source of truth. Target the branch `plan.md` records unless the user names another, recording why in `log.md`. Require a clean tree on the target branch, ignoring the plan directory, since worktrees do not carry uncommitted changes; otherwise ask the user to commit or set changes aside, or to use `run-plan`.

Have it flag eligible slices likely to touch the same files, migrations, lockfiles, generated artifacts, or registries, and note the resources their verification needs, such as ports, databases, or caches. Record each flagged pair, and each pair needing a resource that cannot be duplicated, in `log.md` as a scheduling constraint, not a plan dependency.

Keep the run state in the log's current checkpoint: target branch and tip, any autonomy grant, scheduling constraints, and, for each slice with a worktree, its worktree, branch, base revision, resources, and phase.

## Schedule

Run up to three slices at a time unless the user sets another limit. A slice is eligible when it is `ready`, its dependencies are `complete`, and it shares no scheduling constraint with a running slice. Resume interrupted work first; then start the next eligible slice whenever one integrates or pauses.

Before a worker starts, have a subagent mark the slice `in-progress`, create a worktree on a branch named for the plan and slice ID from the current target tip, at `worktrees/<ID>` in the plan directory or, when that directory is inside the repository, at `${STRIKER_ROOT:-${XDG_STATE_HOME:-$HOME/.local/state}/striker}/worktrees/<repo>/<plan>/<ID>`, assign it its own instances of the resources its verification needs, and record it in the run state.

## Execute

Dispatch a fresh worker per slice into its worktree with the plan path, slice ID, worktree path, branch, base revision, assigned resources, relevant user decisions, any recovery report, and the absolute paths of [WORKER.md](WORKER.md) and of `next-slice/SKILL.md`, a sibling of this skill's directory. Instruct it to read and follow `WORKER.md`.

## Integrate

When a worker reports a committed slice, or inspection finds an interrupted integration, dispatch an integrator with the plan path, slice ID, the worker's or inspection's report, and the absolute path of [INTEGRATOR.md](INTEGRATOR.md), instructing it to read and follow that file. Running slices keep their base; integration brings them onto newer work.

## Blockers

The user may grant autonomy for a run, for example by asking to run the plan autonomously. Record the grant in `log.md` so it survives interruption and resume; it lasts until the run finishes or the user revokes it.

For an unexpected issue, an unresolved blocker, or a conflict the integrator could not resolve within the plan, dispatch a reconciler with the report, the plan path, the affected worktree, the running slices, whether autonomy is granted, and the absolute path of [RECONCILER.md](RECONCILER.md), instructing it to read and follow that file. Tell the user at once, without pausing, about a decision that two or more unfinished slices build on. Return a repaired or revised slice to a worker in its worktree before integrating it, and re-dispatch the integrator after the reconciler records a new target tip; a running slice takes the revision when its worker reports. Escalate a recurring unresolved blocker instead of repeating the same recovery.

Relay escalations to the user and pause affected work; its worktree holds the recovery state, so other slices keep running. Have a subagent mark the paused slice `blocked` with what resolves it and record its next action in `log.md`; once resolved, have a subagent mark it `in-progress` again and return it to a worker in its worktree. Pass user answers to a subagent; approved plan revisions go through `slice` before dependent execution resumes, after any running slice whose files the revision changes has reported.

## Finish

When every slice is integrated, delegate a final check on the target branch of agreed outcomes and required integration checks and their evidence. Route gaps through reconciliation; new slices it returns go through `slice` and then run like any other. Finish with the plan path, completed work, landed revisions, unresolved blockers, and worktrees left for paused slices; if nothing can proceed while input is pending, report the paused state rather than completion. After an autonomous run, list the `pending-review` decisions from `log.md`, costliest to undo first, then decisions the reconciler escalated that still await input.
