---
name: settle
description: Settle implementation decisions, question the user only on real forks, then write a sliced plan for the next session.
disable-model-invocation: true
---

A grilling that spends the user's attention only on decisions that are genuinely theirs. Settle the rest from the nearest code precedent or, where none exists, as an explicit reversible default.

Code is the only source of truth for current behaviour; user answers are the source of truth for desired behaviour. Every code-backed line cites a `file:line` read this session.

## Evidence state

Classify the project before enumerating decisions, and state the classification in the first round:

- **Established**: relevant implementation and conventions exist.
- **Sparse**: tooling or a skeleton exists, but the feature has no nearby precedent.
- **Blank**: no implementation, build configuration, or tests. Git metadata and prose documents are not implementation precedent.

Blank projects follow [BOOTSTRAP.md](BOOTSTRAP.md) as well as this file.

A concrete feature request stays in `settle` whatever the repository holds; an open runtime, framework, or storage fork is an implementation decision and belongs in the interview. Redirect only when the product itself is open: if the request cannot name an observable outcome, an actor or caller, one demonstrable use case, and a boundary for the first green slice, report the missing product decisions, point at the `shape-project` skill, and wait.

## The inference test

Enumerate every decision the work depends on, the small ones included: error handling, loading and empty states, naming, file placement, styling, test location, types, logging. Each decision passes this test before it earns a place in a round.

Find its **nearest precedent**: the feature folder you are changing, then its parent, then the repo. The nearest layer that settles the decision wins, so a repo-wide tie is not a fork while the local folder has already picked. Escalate to a question only when the nearest layer is split.

| What you find | What you do |
| --- | --- |
| One established way | Resolve as `A<n>`. Cite the code. |
| Two or more live patterns at the nearest layer | **Ask.** A real fork. |
| No precedent, and the choice touches product behaviour, a public contract, persistent data, security, deployment, or several slices | **Ask.** |
| No precedent, and the choice is invisible outside the implementation and reversible within one slice | Resolve as `D<n>`. Record the reason and reversal cost. |

Absence of code proves only that no precedent exists.

## Rounds

Work the decisions as a tree. The **frontier** is every decision whose prerequisites are settled. Ask the whole frontier in one round, then wait; a question whose answer depends on another question open this round belongs to the next. There is no question budget: if eight genuine forks survive the test, ask eight.

Each round prints the `A<n>` and `D<n>` lines new to it, then the questions, as plain text in exactly this shape:

```
Assumed from the codebase; reopen any by number
A1. Errors surface through useCommonErrorHandling · <the file:line you read>

Defaults where no precedent exists; reopen any by number
D1. Put feature tests beside their source files · no precedent; local and reversible within this slice

Q1. <title>: <body, options>
Recommended: <your answer and why>
```

The labels are the interface. Number them once per session, never reuse one, and keep them in the round's text: a question-picker tool drops them. A reopened `A<n>` or `D<n>` becomes a question on the current frontier. When the user defers a question to you, your recommendation becomes the decision, recorded with its reason and the deferral.

## Discovery

Find targeted facts inline. Delegate a bounded discovery task when it needs a broad sweep, several sources, or an independent line of investigation that can run in parallel. Give the subagent the exact question, scope, and evidence expected, and continue the frontier while it runs, holding only the decisions that depend on its result. External research is never code precedent.

## Contradictions

Every account of how the code works is a claim to check, whatever its source: the user, a note, a doc, a comment, a subagent's report. Read the code. Where the two disagree, surface it before the next round:

```
⚠️ <the claim>, from <source>. The code <what it actually does> · <file:line>. Which holds?
```

The code wins on current behaviour. When a note or doc loses, record that line as stale so it gets fixed. A deliberate request to change current behaviour is a decision, not a contradiction.

## Slices

The interview produces a tree of **use cases**: things a user can do and you can demonstrate. Record the tree at full depth and emit slices at depth one. One slice is one session's work.

Every slice ends **green**: the code compiles and its tests pass. Green states exist only at use-case boundaries, so the tree decides the seams and size never does. A slice that cannot end green merges into its neighbour, even when that makes it large. A slice reaching across many folders means the use case wants decomposing: ask the user whether to emit that node's children.

Slices run in order. A complete mechanical change (a rename, an enum migration, a signature change) is a legitimate slice and runs **first**; left until last, it rewrites the files the earlier slices just wrote.

Each slice names the cheapest verification that proves it green: an affected-only typecheck with the specs it touched, ahead of a full build whose output costs the next session's context. Source the command from the environment (a `package.json` script, a Makefile target, a documented command) and cite where you found it. A command you did not find is a command the next session cannot run. When it does not exist yet, mark it `to create` and name the slice that creates it.

## Exit

The session is done when the frontier is empty, every enumerated decision is a user answer, a code-backed `A<n>`, or a reasoned `D<n>`, and every slice has a command that will prove it green.

Present the goal, the ordered slices with their verifications, and the `D<n>` defaults. Wait for approval.

On approval, write the plan directory specified in [PLAN-FORMAT.md](PLAN-FORMAT.md). Tell the user the absolute directory path and that `next-slice` runs the first slice.
