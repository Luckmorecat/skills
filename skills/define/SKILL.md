---
name: define
description: Resolve the desired outcome, acceptance, constraints, and consequential decisions, then write a work contract.
disable-model-invocation: true
---

Define what should be delivered and its constraints. Spend the user's attention on decisions that are theirs.

Code is the source of truth for current behaviour; user answers govern desired behaviour. Cite code-backed claims with a `file:line` read this session.

## Evidence state

State the classification in the first round:

- **Established**: relevant implementation and conventions exist.
- **Sparse**: tooling exists, but the feature has no nearby precedent.
- **Blank**: no implementation, build configuration, or tests. Check hidden files; prose and Git metadata are not implementation precedent.

A concrete task stays here: resolve missing outcomes, actors, use cases, or scope boundaries through the question rounds. For a blank project, settle the runtime, tooling, storage, services, and cost choices needed by the requested outcome; mark missing verification commands `to create`. Hand off to `shape-project` when the user is exploring an open-ended product idea rather than defining a concrete task.

## Decisions

Resolve choices that constrain acceptance, shared architecture, or immediate implementation. Defer later details as `U<n>`: unknown, dependent work, resolver, and evidence required before that work starts.

Find the **nearest precedent**: feature folder, parent, then repository. The nearest layer that settles the choice wins.

| Evidence | Action |
| --- | --- |
| One established way | Resolve as `A<n>`; cite the code. |
| Split or absent precedent; choice changes behaviour, public contracts, persistent data, security/privacy, deployment, external services, ongoing cost, or is expensive to reverse | Ask before dependent implementation. |
| Split or absent precedent; internal and cheaply reversible within approved constraints | Resolve as `D<n>`; record reason and reversal cost. |

## Rounds and discovery

The **frontier** contains questions needed now whose prerequisites are settled. Ask them together, then wait; dependent questions belong to the next round.

Print new decisions with stable labels:

```text
Assumed from code; reopen by number
A1. <assumption> · <file:line>

Defaults; reopen by number
D1. <choice> · <reason and reversal cost>

Deferred
U1. <unknown> · <dependent work, resolver, required evidence>

Q1. <decision and options>
Recommended: <answer and reason>
```

Keep labels unique within the contract. When the user delegates a choice, record the chosen recommendation and delegation. Reuse approved intent from a supplied shape or contract.

Find targeted facts inline. Delegate independent broad discovery when useful, giving the exact question, scope, and expected evidence. External research is not code precedent. Correct stale factual notes; ask only when desired behaviour is unclear or an approved constraint must change.

## Contract and handoff

Finish when acceptance and constraints are concrete and remaining uncertainty has a resolution point. Use [CONTRACT-FORMAT.md](CONTRACT-FORMAT.md) to present the contract and persist it after approval, unless already approved.

Recommend `land` when the whole contract has bounded implementation and verification with no unresolved blocking decisions. Otherwise recommend `slice`. Return the contract's absolute path and the next skill.
