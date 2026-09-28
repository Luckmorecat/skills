---
name: delegate
description: Land a work contract from the session that settled it, orchestrating subagents that implement, review, and commit it green.
disable-model-invocation: true
---

Land the supplied work contract from the session that settled it. Use the conversation only for intent; delegate the rest.

Before dispatch, amend the contract with conversation-settled decisions, constraints, and exclusions it omits or contradicts. Ask only about gaps whose answer changes the work. Record the fixed point with `git rev-parse HEAD 2>/dev/null || git hash-object -t tree /dev/null`, and `git status --porcelain` when the tree is already dirty.

Use one worker by default. Split into two to four chunks only when each owns disjoint files and its own acceptance IDs. Run dependent chunks in sequence in the current checkout, passing each worker the previous report. Run independent chunks in parallel in isolated worktrees, when available, from a clean tree; otherwise, in sequence. After parallel chunks, have an integration worker apply their changes to the current checkout uncommitted, resolve conflicts within the contract, and run the full relevant suite. When the work needs persisted slices or checkpoints, stop and recommend a slice plan.

Give each worker the contract path, the fixed point and any dirty snapshot, its chunk boundary and acceptance IDs when split, and the absolute path of `land/SKILL.md`, a sibling of this skill's directory. `land` is manual-only: instruct the worker to read that file and follow it, stopping before `code-review` and the commit. Where `land` says to ask, the worker reports the question to you and stops. Require changed paths, verification evidence, and blockers; changes stay uncommitted.

Answer questions the conversation or the contract's delegated discretion settles; escalate the rest to the user with options and a recommendation. Record in the contract every answer that changes approved behaviour. Continue independent chunks only after a worker confirms the paused work can be left safely.

When the user grants autonomy, treat choices the contract leaves open as delegated discretion; still escalate changes to approved behaviour. Keep these decisions out of the contract; pass each, with what raised it and why, to the committing worker for the commit message.

Dispatch a review subagent to read and follow `code-review/SKILL.md` by absolute path, passing the fixed point and any dirty snapshot, the amended contract, and verification evidence. When it cannot nest subagents, have it return its assignments and dispatch them yourself; never review yourself. Route blocking findings to the worker that last touched the code, or to the integration worker, and have it rerun affected verification.

Resume the last worker, or the integration worker, to finish `land` from its commit step.

Check the committed result against the contract's acceptance and the conversation's intent; route gaps through a worker and review again. Finish with the commits, acceptance evidence, contract amendments, autonomous decisions, and unresolved blockers.
