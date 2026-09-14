---
name: slice
description: Decompose an approved contract into bounded, verifiable slices, or prepare and revise slices in an existing plan.
disable-model-invocation: true
---

Own decomposition: create, split, order, and prepare slices. Preserve the approved outcome.

## 1. Open

Take the approved contract or existing plan path the user supplies; ask when absent. Read its constraints, acceptance, relevant code, and any implementation findings. For an existing plan, reconcile the log with Git before replanning; preserve completed work, evidence, and unfinished owned changes.

Accept older briefs and plans without repeating settled decisions. Recover missing acceptance from approved intent; unresolved intent or consequential choices return to `define`.

## 2. Outline

Map every approved acceptance example to an outcome and its dependencies. Outline the whole scope. Assign deferred decisions to the point before dependent implementation begins. If evidence is missing, schedule a bounded experiment whose result unblocks that decision.

Prefer thin demonstrable use cases. Compatibility adapters, additive migrations, and disabled functionality are valid increments when independently verified and preserving existing behaviour. Include integration and cleanup in the outline. Place mechanical changes where dependencies require them.

For blank projects, read [BOOTSTRAP.md](BOOTSTRAP.md).

## 3. Prepare bounded slices

Prepare every outlined slice whose Build, Paths, and Verify can be written from evidence available now. Defer a slice only when an unresolved `U<n>` must be resolved before its content can be written; record the unknown and the experiment or slice whose result unblocks it. Dependence on earlier slices orders execution and never defers preparation. Each prepared slice must pass these checks:

- **Outcome** — one primary result with concrete acceptance examples.
- **Context** — shared constraints, this slice, and targeted source reads suffice; several independent flows or investigations signal a split.
- **Readiness** — blocking decisions are resolved; remaining prerequisites are earlier slices in the recorded order.
- **Verification** — checks demonstrate completion without implementing a later slice.
- **Review** — the change forms one coherent, reviewable unit.

File count and elapsed time are warning signals, not size limits. Reduce the knowledge needed for the slice rather than merely shortening its description. An experiment has one question, an explicit time or effort limit, and required evidence; it does not claim a delivered feature.

Record the outcome, acceptance, dependencies, relevant constraints, code entry points, exclusions, and verification with expected results. Cite commands from the environment; mark missing commands `to create` and include their creation. The final slice of a milestone includes an integrated acceptance check.

Keep one implementation owner by default. Parallel work requires independent dependencies, explicit write ownership, and an integration owner.

## 4. Write and hand off

Use [PLAN-FORMAT.md](PLAN-FORMAT.md). Keep identifiers stable when revising; update affected unstarted slices and record reasons. If unfinished work must be split, preserve its baseline and checkpoint, assigning remaining work explicitly instead of resetting progress.

Decomposition within approved scope needs no fresh approval. A change to approved behaviour, public contracts, persistent data, security/privacy, deployment, services, cost, or an expensive-to-reverse choice requires a decision through `define` before dependent work.

Return the plan path, brief outline, the next ready slice for `next-slice`, how many slices are prepared, and each deferred slice with the evidence that unblocks it and the exact `slice` invocation that prepares it. Later invocations prepare deferred slices from recorded evidence or revise unstarted slices from implementation findings. Keep planning and implementation in separate sessions by default.
