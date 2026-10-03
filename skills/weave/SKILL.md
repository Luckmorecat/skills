---
name: weave
description: Land work whose intent the current session settled, orchestrating subagents that implement, review, and commit it green.
disable-model-invocation: true
---

Land the work whose intent this session settled by orchestrating subagents. You are the orchestrator: this thread holds the conversation's intent and decisions; it briefs, unblocks, routes, and checks until acceptance holds. Subagents implement, review, and commit.

Resolve `code-review/SKILL.md` and `commit/SKILL.md` as siblings of this skill's directory. When either is missing, report it as a missing prerequisite before dispatching anything.

## Brief

Write a brief from the supplied work and the conversation: the goal, observable acceptance examples with IDs, scope and exclusions, settled decisions, delegated discretion, and any sources of truth for approved behaviour, such as a contract, spec, design, or prototype, each with the version to hold it to, what it settles, and its precedence. Derive acceptance where absent. Amend a supplied contract only where the conversation contradicts or extends it. Ask only about gaps whose answer changes the work. The brief is done when every behaviour the conversation settled has an acceptance ID and every source of truth has a version, what it settles, and its precedence.

Keep **run decisions**, the choices made during the run that the brief leaves open, in a list apart from the brief and any supplied contract, each with what raised it, the alternatives, the reason, and its undo cost.

When the brief names sources of truth, read [SOURCES.md](SOURCES.md) before deciding chunks and follow it through the run.

## Handoff

Every subagent gets the brief, the run decisions affecting its work, and the absolute path of its role file, instructed to read and follow it: [WORKER.md](WORKER.md) for workers, [RECONCILER.md](RECONCILER.md) for reconcilers, and the sibling `code-review/SKILL.md` or `commit/SKILL.md` for review and commit. Each dispatch names only what it adds.

## Fixed point

Record the fixed point before dispatch with `git rev-parse HEAD 2>/dev/null || git hash-object -t tree /dev/null`, and `git status --porcelain` as the dirty snapshot when the tree is already dirty. A **round** is one pass of implementation, review, and commit. The first round's fixed point is the recorded one; each repair round's is the last commit. Give review the recorded fixed point instead when a repair changes code earlier work depends on.

## Dispatch

Decide the chunks before dispatch. Split where parts can proceed independently or where one worker would carry too much context; keep a coherent change whole, since each split adds handoffs and integration. Give each chunk its own acceptance IDs. When the work needs more than four chunks, or persisted slices or checkpoints, stop and recommend a slice plan.

Run chunks in sequence in the current checkout, passing each worker the previous report. To run independent chunks in parallel, read [PARALLEL.md](PARALLEL.md).

Give each worker the paths of any supplied documents, any dirty snapshot, and, when split, its chunk boundary and acceptance IDs.

## Questions and updates

A worker that raises a question or a discrepancy stops and returns; its chunk is **paused** until you deliver the update it needs. Resume a paused worker by continuing it with its context, or, when that is unavailable, dispatch a fresh worker with its report. Continue independent chunks only after a worker confirms the paused work can be left safely.

Answer questions the conversation or the brief's delegated discretion settles; escalate the rest to the user with options and a recommendation. Add every answer that changes approved behaviour to the brief, and to a supplied contract; record any other answer as a run decision. Revise any run decision an answer overturns.

Deliver every update, whether an answer or a run decision, to each worker whose acceptance IDs it affects before that worker's dependent work resumes. When the work it affects is already done, dispatch a worker to rework it.

## Autonomy

When the user grants autonomy, decide choices the brief leaves open yourself. Still escalate changes to approved behaviour and any choice that would:

- lose data or require an irreversible migration;
- loosen security, privacy, or permissions;
- break a public API or external contract;
- change deployment, add an external service, or add ongoing cost;
- leave the result unverifiable against the brief's acceptance.

Decide by the brief's delegated discretion, then these defaults in order: keep every existing capability; stay closest to the approved intent; prefer the option cheapest to undo; prefer the smallest change that satisfies acceptance. Record each as a run decision.

## Review and commit

Dispatch a review subagent with the round's fixed point, any dirty snapshot, and verification evidence. Where subagents cannot dispatch their own, dispatch `code-review`'s Standards and Plan compliance axes as two subagents yourself, each following `code-review/SKILL.md` for its axis alone, and combine their findings; never review yourself. Route blocking findings to the worker that last touched the code, and have it rerun affected verification.

Once no blocking findings remain, dispatch a commit worker with the round's fixed point, any dirty snapshot, the commit-message notes workers reported, and the round's run decisions for the message.

## Check

Check the committed result against the brief's acceptance and the conversation's intent, and, when the brief names sources of truth, through the reconciler check in [SOURCES.md](SOURCES.md). Repair each gap through a worker that verifies it, then review, commit, and check the new result the same way. Escalate a gap that recurs after repair instead of repeating the same repair.

Finish once acceptance holds at the final commit, any reconciler check returns no gaps, and no owned changes remain uncommitted. Report the commits, acceptance evidence, answers that changed approved behaviour, run decisions, costliest to undo first, unresolved blockers, and any worktrees kept for paused chunks.
