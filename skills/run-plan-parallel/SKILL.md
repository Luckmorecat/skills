---
name: run-plan-parallel
description: Run a slice plan through parallel subagents in isolated worktrees, integrating each verified slice and reconciling blockers.
disable-model-invocation: true
---

Orchestrate the plan to completion, asking for its path if none is given, and run independent slices concurrently in isolated worktrees. Your work is scheduling, dispatching subagents, routing their reports, and talking to the user; subagents do every inspection, implementation, verification, integration, and file change. The plan directory is the source of truth for the run's state, over anything this conversation remembers.

Dispatch plan-directory writers, integrators included, one at a time; a worker or reconciler writing only its slice's worktree and `checkpoints/<ID>.md` may run alongside them. When a subagent returns assignments because it cannot delegate further, dispatch them, sequentially if capacity requires, and return the results to that subagent.

## Inspect

Dispatch an inspection subagent to read the plan, `log.md`, and `checkpoints/`, check repository state, and report the eligible slices and each interrupted slice or integration, with its existing worktree and state, as the **recovery report**. Target the branch `plan.md` records unless the user names another, having the subagent record why in `log.md`. Require a clean tree on the target branch, ignoring the plan directory, since worktrees do not carry uncommitted changes; otherwise ask the user to commit or set changes aside, or to use `run-plan`.

Have it also flag eligible slices likely to conflict (overlapping files, migration sequences, lockfiles, generated artifacts, or registries), note the resources their verification needs, such as ports, databases, or caches, and record each flagged pair, and each pair needing a resource that cannot be duplicated, in the run state as a **scheduling constraint**: two slices that never run at once, kept apart from `plan.md`'s dependencies.

The **run state** lives in the log's current checkpoint: target branch and tip, any autonomy grant, scheduling constraints, and, for each slice with a worktree, its worktree, branch, base revision, and resources.

## Schedule

Run up to three slices at a time unless the user sets another limit. A slice is eligible when it is `ready`, its dependencies are `complete`, and it shares no scheduling constraint with an unfinished slice that has a worktree. Resume interrupted work first; then, whenever a running slice integrates or pauses, start the next eligible slice, until every slice is complete or none can proceed.

Before a worker starts, have a subagent:

- mark the slice `in-progress`;
- create its worktree from the current target tip, on a branch named for the plan and slice ID, at `worktrees/<ID>` in the plan directory, or at `${STRIKER_ROOT:-${XDG_STATE_HOME:-$HOME/.local/state}/striker}/worktrees/<repo>/<plan>/<ID>` when the plan directory is inside the repository;
- assign the slice its own instances of the resources its verification needs;
- record all of this in the run state.

## Execute

Dispatch a fresh **worker** per slice into its worktree with the plan path, slice ID, worktree path, branch, base revision, assigned resources, relevant user decisions, any recovery report, and the absolute paths of [WORKER.md](WORKER.md) and of `../next-slice/SKILL.md`, relative to this skill's directory. Instruct it to read and follow `WORKER.md`.

Each worker returns its outcome, evidence, slice-branch commits, checkpoint file, and any questions, blockers, or findings for `slice`. Integrate a committed slice; route the rest to a reconciler.

## Integrate

When a worker reports a committed slice, or the recovery report shows an interrupted integration, dispatch an integrator with the plan path, slice ID, the worker's report or the recovery report, and the absolute path of [INTEGRATOR.md](INTEGRATOR.md), instructing it to read and follow that file. Running slices stay on their base revision; each is rebased onto the newer tip only at its own integration.

## Blockers

The user may grant autonomy for the run. Have a subagent record the grant in the run state so it survives a restart; it lasts until the run finishes or the user revokes it.

A **reconciler** investigates an issue against the plan, repairs within the plan when it can, decides plan changes under an autonomy grant, and otherwise returns an **escalation**: a concrete question, options, a recommendation, and the affected slices. Workers and integrators fix routine failures and review findings themselves; for an unexpected issue, an unresolved blocker, a worker's question or findings for `slice`, or an integration the integrator stopped, dispatch a reconciler with the report, the plan path, the affected worktree, the running slices, whether autonomy is granted, and the absolute path of [RECONCILER.md](RECONCILER.md), instructing it to read and follow that file. When a reconciler decision lists two or more unfinished dependent slices, tell the user at once and keep running. Escalate a recurring unresolved blocker instead of repeating the same repair.

After the reconciler returns:

- send a repaired or revised slice back to a worker in its worktree before integrating it;
- let a running slice that a decision revises run until its worker reports, then return it to a worker with the revision;
- re-dispatch the integrator once the reconciler records a new target tip.

Relay escalations to the user and pause the slices each lists as affected; their worktrees hold the recovery state, so other slices keep running. Have a subagent mark each paused slice `blocked` with what resolves it and record its next action in `checkpoints/<ID>.md`; once resolved, have a subagent mark it `in-progress` again and return it to a worker in its worktree. Pass the user's answer to a reconciler to apply. For an approved plan revision, once every running slice whose files it changes has reported, dispatch a subagent to read and follow `../slice/SKILL.md` directly, as workers read `next-slice`, before dependent slices continue.

## Finish

When every slice is integrated, dispatch a subagent to check the agreed outcomes and required integration evidence on the target branch, and route its gaps to a reconciler. Have a subagent add each new slice the reconciler returns by following `../slice/SKILL.md`, then run it like any other. Finish once the check finds no gaps, reporting the plan path, completed work, landed revisions, unresolved blockers, and worktrees left for paused slices. When nothing can proceed while input is pending, stop and report the paused state instead of completion.

After an autonomous run, list the `pending-review` decisions from `log.md`, costliest to undo first, then the escalations that still await input.
