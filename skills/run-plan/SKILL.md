---
name: run-plan
description: Run a slice plan sequentially through subagents, reconciling blockers and escalating decisions it cannot make.
---

Orchestrate the plan to completion, asking for its path if none is given. Your work is dispatching subagents, routing their reports, and talking to the user; subagents do every inspection, implementation, verification, and file change. The plan and `log.md` are the source of truth for the run's state, over anything this conversation remembers.

## Inspect

Dispatch an inspection subagent to read the plan and `log.md`, check repository state, and report the next eligible slice, or the interrupted slice with its state as the **recovery report**. Resume an interrupted slice before starting another.

## Run each slice

Dispatch a fresh **worker** per slice with the plan path, slice ID, relevant user decisions, any recovery report, and the absolute path of `../next-slice/SKILL.md`, relative to this skill's directory. `next-slice` is manual-only, so instruct the worker to read that file directly instead of invoking it as a skill, resolve its relative links from its directory, and follow it for that slice alone. Tell it to return to you, instead of asking the user or handing back to `slice`, every unresolved blocker and every consequential choice `next-slice` would settle with the user.

If a worker cannot delegate further, it returns each subagent assignment it needs, such as `code-review`'s reviewers, with its context, so review stays independent. Dispatch those, sequentially if capacity requires, and return the results to the worker.

Each worker returns its outcome, evidence, landed revision, and the next eligible slice or remaining blockers. Run slices sequentially: hand the workspace to another subagent only after the current worker returns. Then dispatch a worker for the next eligible slice, until every slice is complete or none can proceed.

## Blockers

The user may grant autonomy for the run. Have a subagent record the grant in `log.md` so it survives a restart; it lasts until the run finishes or the user revokes it.

A **reconciler** investigates an issue against the plan, repairs within the plan when it can, decides plan changes under an autonomy grant, and otherwise returns an **escalation**: a concrete question, options, a recommendation, and the affected slices. Workers fix routine failures and review findings themselves; for an unexpected issue or unresolved blocker, dispatch a reconciler with the report, the plan path, whether autonomy is granted, and the absolute path of [RECONCILER.md](RECONCILER.md), instructing it to read and follow that file. When a reconciler decision lists two or more unfinished dependent slices, tell the user at once and keep running. After a repair, a worker reruns the affected slice before you accept it as complete. Escalate a recurring unresolved blocker instead of repeating the same repair.

Relay escalations to the user and pause the slices each lists as affected. Before continuing other eligible slices, have a subagent preserve the blocked slice's recovery state and unverified changes and confirm it can be left safely. Pass the user's answer to a reconciler to apply. For an approved plan revision, dispatch a subagent to read and follow `../slice/SKILL.md` directly, as workers read `next-slice`, before dependent slices continue.

## Finish

When workers report all slices complete, dispatch a subagent to check the agreed outcomes and required integration evidence, and route its gaps to a reconciler. Finish once the check finds no gaps, reporting the plan path, completed work, and unresolved blockers. When nothing can proceed while input is pending, stop and report the paused state instead of completion.

After an autonomous run, list the `pending-review` decisions from `log.md`, costliest to undo first, then the escalations that still await input.
