---
name: design
description: Resolve a focused technical design question through evidence, alternatives, and scenario checks, then amend the work contract.
disable-model-invocation: true
---

Turn a named technical uncertainty into a decision precise enough for implementation. Work within the supplied intent and constraints. `define` owns the delivery contract; `design` deepens selected technical decisions; `slice` owns decomposition. This session produces decisions and contract amendments, not implementation.

## 1. Frame

Read the supplied contract or plan and relevant conversation. Reuse settled intent and decisions. If no contract exists, work from the stated outcome and constraints; return missing product intent to `define` when it prevents evaluating the design.

State the **decision**, **fixed constraints**, **comparison criteria in priority order**, and **excluded questions**. Ask only for missing information that changes this frame. A broad request becomes a bounded set of related decisions with their dependencies.

Proceed when the decision and criteria distinguish what an acceptable answer must accomplish. Explicit user priorities govern; otherwise propose priorities and identify any tradeoff that needs the user's judgment.

## 2. Inspect evidence

Trace the relevant behavior, interfaces, state ownership, and dependency boundaries in code. Cite current facts with `file:line` read this session; label proposed structures separately. Find the nearest applicable precedent. Treat internals being replaced as current behavior, not a constraint on their replacement.

List only evidence gaps that could change the choice. For each, name the question, affected decision, and evidence needed. Distinguish facts, assumptions, and approved constraints; agreement does not verify an assumption.

Proceed when there is enough evidence to compare approaches. If a decisive fact requires an experiment, specify its scope, effort limit, observable result, and how that result selects an approach. Mark the decision pending evidence; continue independent decisions only.

## 3. Compare

Compare the simplest viable approach with materially different credible alternatives, usually two or three approaches in total. Include the existing approach when viable. If only one survives the constraints, explain why; avoid manufacturing alternatives.

Use a compact table against the same criteria. Reject hard-constraint violations first, then compare surviving options using the stated priorities. Include consequences, operating burden, and reversal cost where they distinguish options. Recommend one approach and state what evidence or priority change would overturn it.

Proceed when the recommendation and its tradeoffs follow from the evidence and criteria. Leave unsupported claims explicit.

## 4. Stress-test and resolve

Trace the recommendation through concrete success, failure, and boundary scenarios relevant to the decision. Include concurrency, retries, cancellation, or migration when they can change the choice. State the expected behavior and responsible component at each consequential boundary. Revise the recommendation if a scenario exposes a contradiction.

Show the proposed design at the smallest useful level: responsibilities, interfaces, state transitions, invariants, and failure behavior that implementers must preserve. Keep cheaply reversible implementation details open.

Ask unresolved tradeoffs together when independent; ask dependent questions after their prerequisites settle. Give each question a stable `Q<n>` label, options, a recommendation, and its consequence. Preserve existing identifiers and allocate unused numbers. Record choices and reasons, including delegated choices. Existing approval or delegation suffices; otherwise wait for the user's decision before treating a recommendation as settled.

Proceed when each in-scope decision is resolved or explicitly pending evidence or user choice, and scenario checks reveal no unaddressed contradiction.

## 5. Record and hand off

Present a concise decision record:

- **Question and status** — resolved, pending evidence, or pending user choice.
- **Decision and rationale** — chosen approach, relevant evidence, alternatives, and accepted tradeoffs.
- **Design obligations** — boundaries, interfaces, invariants, and scenario expectations needed for implementation and verification.
- **Contract changes** — affected acceptance, constraints, decisions, and unknowns; distinguish agreed changes from proposals.
- **Remaining uncertainty** — affected work, resolver, evidence required, and resolution point; `None` when resolved.

Amend the supplied contract with agreed changes, preserving identifiers and unrelated content. For replaced decisions record the prior choice, replacement, reason, and approval or delegation. Keep the contract authoritative; use a linked design note only when the detail would overwhelm it. Without a supplied file, return the record in conversation for `define` to incorporate. An ADR is optional for a durable, costly-to-reverse tradeoff whose rationale future maintainers need.

If a supplied plan is affected, identify the affected unstarted slices and hand it to `slice` for revision. Otherwise return to `define` for unresolved delivery intent, recommend the bounded investigation for missing evidence, or recommend `land` or `slice` according to the existing contract's readiness. Pending decisions block their dependent work. Return amended paths and the next action, then stop.
