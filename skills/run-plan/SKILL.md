---
name: run-plan
description: Run a slice plan sequentially through subagents, reconciling blockers and escalating decisions it cannot make.
---

Orchestrate the plan to completion, asking for its path if none is given. Your work is dispatching subagents, routing their reports, talking to the user, and recording run state. Run state (status, baselines, landed revisions, the autonomy grant, and the decision index, kept in `state.json`) changes only through `plan`. You call `plan` directly for your own writes and reads, and dispatch subagents for every other change and for every inspection of repository state, implementation, verification, and reconciliation. `plan status` is the source of truth for the run's state, over anything this conversation remembers.

Below, `plan <command>` means `python3 <cli> --plan <dir> <command>`, where `<dir>` is the plan directory and `<cli>` is `../slice/bin/plan` resolved from this skill's directory to an absolute path. When that file is missing or lacks a command used here, stop and report that `slice` must be installed or updated beside this skill. `plan <command> --help` documents each command.

## Inspect

When the plan directory has no `state.json`, run `plan import <dir>` before anything else; if the import fails, stop and report its error.

Read `plan status --json`. Its `eligible` slices can start. An **interrupted** slice is one without a worktree that is in progress, or blocked with a recorded fixed point; a slice with a worktree is not this skill's to run, so report it. Continue an in-progress slice before starting another; a blocked one continues once what its reason names is resolved. Before a fresh worker continues an interrupted slice, dispatch an inspection subagent to check the repository state against `checkpoints/<ID>.md` and report the slice's recovery state as the **recovery report**.

## Run each slice

Dispatch a fresh **worker** per slice with the plan path, slice ID, relevant user decisions, any recovery report or existing `checkpoints/<ID>.md`, and the absolute path of `../next-slice/SKILL.md`, relative to this skill's directory. `next-slice` is manual-only, so instruct the worker to read that file directly instead of invoking it as a skill, resolve its relative links from its directory, and follow it for that slice alone. Tell it to return to you, instead of asking the user or handing back to `slice`, every unresolved blocker and every consequential choice `next-slice` would settle with the user.

If a worker cannot delegate further, it returns each subagent assignment it needs, such as `code-review`'s reviewers, with its context, so review stays independent. Dispatch those, sequentially if capacity requires, and return the results to the worker.

Each worker returns its outcome, evidence, landed revision, and the next eligible slice or remaining blockers; a slice is complete once `plan status` shows it complete. Run slices sequentially: hand the workspace to another subagent only after the current worker returns. Then inspect again and dispatch a worker for the interrupted slice or the next slice `plan next` lists, until every slice is complete or none can proceed.

## Blockers

The user may grant autonomy for the run. Record it with `plan grant --note <its terms>`. A grant that `plan status` already shows is the run's grant after a restart; record new terms with `plan revoke`, then `plan grant`. The grant lasts until the run completes, when you end it with `plan revoke`, or until the user revokes it, which you record the same way; every other stop leaves it recorded for the restart.

A **reconciler** investigates an issue against the plan, repairs within the plan when it can, decides plan changes under an autonomy grant, and otherwise returns an **escalation**: a concrete question, options, a recommendation, and the affected slices. Workers fix routine failures and review findings themselves; for an unexpected issue or unresolved blocker, dispatch a reconciler with the report, the plan directory, the absolute path of `<cli>`, whether autonomy is granted, and the absolute path of [RECONCILER.md](RECONCILER.md), instructing it to read and follow that file. For each `R<n>` a reconciler decides, read its row in `plan decisions --json`; when `unfinished` names two or more slices, tell the user at once and keep running. After a repair or decision, a worker runs or reruns each unfinished slice it unblocks before you accept that slice as complete; the next final check verifies a repair outside any slice. Escalate a recurring unresolved blocker instead of repeating the same repair.

Relay escalations to the user and pause the slices each lists as affected, running `plan block <ID> --reason <the input it awaits>` for each that is ready or in progress. Before continuing other eligible slices, have a subagent record each paused slice's next action in `checkpoints/<ID>.md` (`plan start` keeps that file for a slice not yet started) and, for one that has started, preserve its recovery state and unverified changes and confirm it can be left safely. Pass the user's answer to a reconciler to apply. For an approved plan revision, dispatch a subagent to read and follow `../slice/SKILL.md` directly, as workers read `next-slice`, before dependent slices continue. Then return each paused slice that never started to ready with `plan resume <ID>`; a started one is interrupted work, which its worker resumes.

## Finish

When `plan status` shows every slice complete, dispatch a subagent to check the agreed outcomes and required integration evidence, and route its gaps to a reconciler. Finish once the check finds no gaps, reporting the plan path, completed work, repairs that reconcilers reported outside any slice, and unresolved blockers. When nothing can proceed while input is pending, stop and report the paused state instead of completion.

After an autonomous run, list the `pending-review` decisions, costliest to undo first. `plan decisions --pending` gives the indexed ones in that order. Have a subagent report the `pending-review` decisions `log.md` records before an ``imported by `plan import` `` entry, which the index lacks, leaving out those a later `approved` decision names as the one it approves, and merge them in by their recorded undo cost. Then list the escalations that still await input. Once a completed run is reported, end a recorded grant.
