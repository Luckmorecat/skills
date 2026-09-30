---
name: weave
description: Land work whose intent the current session settled, orchestrating subagents that implement, review, and commit it green.
disable-model-invocation: true
---

Land the work whose intent this session settled by orchestrating subagents. This thread holds the conversation's intent and decisions: it briefs, unblocks, routes, and checks until acceptance holds. Subagents implement, review, and commit.

Before dispatch, write a brief from the supplied work and the conversation: the goal, observable acceptance examples with IDs, scope and exclusions, settled decisions, and delegated discretion. Derive acceptance where absent. Amend a supplied contract only where the conversation contradicts or extends it. Ask only about gaps whose answer changes the work. Record the fixed point with `git rev-parse HEAD 2>/dev/null || git hash-object -t tree /dev/null`, and `git status --porcelain` when the tree is already dirty.

Decide the chunks before dispatch. Split where parts can proceed independently or where one worker would carry too much context; keep a coherent change whole, since each split adds handoffs and integration. Give each chunk its own acceptance IDs. Run independent chunks that own disjoint files in parallel in isolated worktrees, when available, from a clean tree; run the rest in sequence in the current checkout, passing each worker the previous report. After parallel chunks, have an integration worker apply their changes to the current checkout uncommitted, resolve conflicts within the brief, and run the full relevant suite. When the work needs more than four chunks, or persisted slices or checkpoints, stop and recommend a slice plan.

Give each worker the brief, the paths of any supplied documents, any dirty snapshot, its chunk boundary and acceptance IDs when split, and the absolute path of [WORKER.md](WORKER.md), instructing it to read and follow that file.

Answer questions the conversation or the brief's delegated discretion settles; escalate the rest to the user with options and a recommendation. Add every answer that changes approved behaviour to the brief, and to a supplied contract. Continue independent chunks only after a worker confirms the paused work can be left safely.

When the user grants autonomy, decide choices the brief leaves open yourself. Still escalate changes to approved behaviour and any choice that would:

- lose data or require an irreversible migration;
- loosen security, privacy, or permissions;
- break a public API or external contract;
- change deployment, add an external service, or add ongoing cost;
- leave the result unverifiable against the brief's acceptance.

Decide by the brief's delegated discretion, then these defaults in order: never drop an existing capability; stay closest to the approved intent; prefer the option cheapest to undo; prefer the smallest change that satisfies acceptance. Keep these decisions out of the brief and any supplied contract; pass each, with what raised it, the alternatives, the reason, and its undo cost, to the commit worker for the message.

Dispatch a review subagent to read and follow `code-review/SKILL.md` by absolute path, passing the fixed point and any dirty snapshot, the brief, and verification evidence. When it cannot nest subagents, have it return its assignments and dispatch them yourself; never review yourself. Route blocking findings to the worker that last touched the code, or to the integration worker, and have it rerun affected verification.

Once no blocking findings remain, dispatch a commit worker to read and follow `commit/SKILL.md` by absolute path, passing the fixed point, any dirty snapshot, the autonomous decisions, and the commit-message notes workers reported.

Check the committed result against the brief's acceptance and the conversation's intent; route gaps through a worker and review again. Finish with the commits, acceptance evidence, answers that changed approved behaviour, autonomous decisions, costliest to undo first, and unresolved blockers.
