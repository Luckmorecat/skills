---
name: stitch
description: Deliver work settled in the current session with minimal primary-agent quota, delegating implementation, Codex review, and commit to one lean worker.
disable-model-invocation: true
---

Deliver work whose intent this session settled while keeping primary-agent quota low and the main thread clean. You hold the conversation's intent and decisions; a lean worker implements, verifies, runs independent review (through Codex by default), and commits green.

## 1. Scope and brief

Default to one worker. Split into two or three sequential chunks yourself only when the work is plainly too large for one worker and divides cleanly without a planner; pass each later chunk the earlier receipt and latest `HEAD` as `base`, and assign integration acceptance to the last chunk. When the work needs a planner, parallel worktrees, or reconciliation against a prototype or external spec, stop and recommend `weave` or `slice`.

Write a concise brief from the supplied work and this conversation:

- **Goal**: what changes and why.
- **Acceptance**: observable pass/fail bullets (derive them where absent).
- **Scope & exclusions**: what is in and what stays untouched.
- **Settled decisions**: choices already agreed in this session and any delegated discretion.
- **Starting points**: relevant file paths, key symbols, and test/check commands already known from this session, so the worker skips rediscovery.

Ask only about gaps whose answer changes the work. Amend a supplied work contract only where this session changed it.

Record `base` with `git rev-parse HEAD 2>/dev/null || git hash-object -t tree /dev/null`, and `dirty snapshot` with `git status --porcelain` when the tree is already dirty.

## 2. Dispatch worker

Dispatch a fresh worker without this conversation's history where the runtime allows. Pass:

- the verbatim brief;
- `base` and any `dirty snapshot`;
- any user-requested Codex model, reasoning effort, or fallback-only review preference;
- the absolute paths of [WORKER.md](WORKER.md) and [REVIEW.md](REVIEW.md), instructing the worker to read and follow them.

## 3. Handle returns

- **Completed**: the worker returned commit SHA(s), green verification evidence, and a review receipt with `VERDICT: APPROVE` (or `nit`-only findings) covering the final behavior diff. Confirm acceptance holds from the receipt and go to step 4.
- **Question or review dispute**: answer from this session's intent or delegated discretion. Escalate to the user any change to approved behavior or choice that risks data loss or irreversible migration, security/privacy/permissions, public API or external contracts, deployment/external services/ongoing cost, or unverifiable acceptance. When the user grants autonomy, decide open choices outside those hard stops using delegated discretion — preserving existing behavior and taking the smallest reversible option — and record each decision for the report. Resume the same worker with the answer and any brief amendment.
- **Fallback needed**: the worker stopped uncommitted after green checks because neither Codex nor a nested review subagent could run. Read [REVIEW.md](REVIEW.md) (**Orchestrator fallback**) and run it.

## 4. Report

Report: commits made, verification evidence (with log paths), review summary (reviewer backend, model and effort, rounds, fixed and declined findings, usage if exposed), any decisions made on the user's behalf, open follow-ups or blockers, and an explicit note whenever fallback review ran instead of Codex.
