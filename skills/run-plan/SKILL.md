---
name: run-plan
description: Run a slice plan sequentially through subagents, reconciling blockers and escalating decisions to the user.
---

Orchestrate the supplied plan through completion. Use its established path or ask when absent. Keep your work to dispatching subagents, routing their reports, and communicating with the user. Delegate all inspection, implementation, verification, and file changes.

Start with an inspection subagent: read the plan and checkpoints, check repository state, and identify interrupted work or the next eligible slice. Use the existing plan and log as the source of truth. Resume interrupted work before starting another slice.

Dispatch a fresh execution subagent for each slice. Give it the plan path, slice ID, relevant user decisions, and any recovery report. Instruct it to read and follow `next-slice`, completing only that slice. Run one slice at a time; wait for its worker to finish before handing off the workspace.

Tell workers to return required subagent assignments and context when nested delegation is unavailable, preserving independent review instead of substituting self-review. Dispatch those assignments directly, sequentially if capacity requires, and relay the results before resuming the worker.

Require workers to return their outcome, evidence, checkpoint location, and next eligible slice or remaining blockers. Routine implementation failures and review fixes belong to the execution worker. Workers report unresolved blockers to you for routing instead of independently asking the user.

For an unexpected issue or unresolved blocker, dispatch a reconciler with the worker's report and plan path. Have it investigate, repair within the agreed plan, verify its repair, and checkpoint the result. Changes to scope, design, acceptance, or dependencies require user input unless already authorized; the reconciler returns a concrete question, recommendation, and affected slices. After repair, return the affected slice to an execution subagent following `next-slice` before accepting completion. Escalate a recurring unresolved blocker instead of repeating the same recovery.

Relay escalations to the user and pause affected work. Continue independent eligible slices only after a subagent confirms that the blocked work can be left safely, preserving its recovery state and unverified changes. Pass user answers to a subagent; approved plan revisions go through `slice` before dependent execution resumes.

When workers report all slices complete, delegate a final check of agreed outcomes and required integration evidence. Route gaps through reconciliation. Finish with the plan path, completed work, and unresolved blockers; if nothing can proceed while input is pending, report the paused state rather than completion.
