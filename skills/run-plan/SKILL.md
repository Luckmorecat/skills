---
name: run-plan
description: Run a slice plan sequentially through subagents, reconciling blockers and escalating decisions to the user.
---

Orchestrate the supplied plan through completion. Use its established path or ask when absent. Keep your work to dispatching subagents, routing their reports, and communicating with the user. Delegate all inspection, implementation, verification, and file changes.

Start with an inspection subagent: read the plan and checkpoints, check repository state, and identify interrupted work or the next eligible slice. Use the existing plan and log as the source of truth. Resume interrupted work before starting another slice.

Dispatch a fresh execution subagent for each slice. Give it the plan path, slice ID, relevant user decisions, any recovery report, and the absolute path of `next-slice/SKILL.md`, a sibling of this skill's directory. `next-slice` is manual-only, so instruct the worker to read that file directly instead of invoking it as a skill, resolve its relative links from its directory, and follow it, completing only that slice. Run one slice at a time; wait for its worker to finish before handing off the workspace.

Tell workers to return required subagent assignments and context when nested delegation is unavailable, preserving independent review instead of substituting self-review. Dispatch those assignments directly, sequentially if capacity requires, and relay the results before resuming the worker.

Require workers to return their outcome, evidence, checkpoint location, and next eligible slice or remaining blockers. Routine implementation failures and review fixes belong to the execution worker. Workers report unresolved blockers to you for routing instead of independently asking the user.

The user may grant autonomy for a run, for example by asking to run the plan autonomously. Record the grant in `log.md` so it survives interruption and resume; it lasts until the run finishes or the user revokes it.

For an unexpected issue or unresolved blocker, dispatch a reconciler with the worker's report, the plan path, whether autonomy is granted, and the absolute path of [RECONCILER.md](RECONCILER.md), instructing it to read and follow that file. Tell the user about a decision that two or more unfinished slices build on as soon as it is made, without pausing. After repair, return the affected slice to an execution subagent following `next-slice` before accepting completion. Escalate a recurring unresolved blocker instead of repeating the same recovery.

Relay escalations to the user and pause affected work. Continue independent eligible slices only after a subagent confirms that the blocked work can be left safely, preserving its recovery state and unverified changes. Pass user answers to a subagent; approved plan revisions go through `slice` before dependent execution resumes.

When workers report all slices complete, delegate a final check of agreed outcomes and required integration evidence. Route gaps through reconciliation. Finish with the plan path, completed work, and unresolved blockers; if nothing can proceed while input is pending, report the paused state rather than completion. After an autonomous run, list the `pending-review` decisions from `log.md`, costliest to undo first, then decisions the reconciler escalated that still await input.
