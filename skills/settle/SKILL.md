---
name: settle
description: Settle implementation decisions, question the user only on real forks, then write a sliced plan for the next session.
disable-model-invocation: true
---

A grilling that spends the user's attention only on decisions that are genuinely theirs. Settle the rest from the nearest code precedent or, where no precedent exists, as an explicit reversible default.

Existing code is the only source of truth for claims about existing behaviour. User answers are the source of truth for desired behaviour. Every code-backed ledger line cites a `file:line` read this session. Notes, docs, and recollection supply leads worth checking. Their implementation claims remain unverified until the code confirms them. Absence of code proves only that no precedent exists.

## Evidence state

Before enumerating decisions, classify the project:

- **Established**: relevant implementation and conventions exist.
- **Sparse**: tooling or a skeleton exists, but the feature has no nearby precedent.
- **Blank**: no implementation, build configuration, or tests exist. Git metadata and prose documents do not count as implementation precedent.

When the project is blank, read [BOOTSTRAP.md](BOOTSTRAP.md) before applying the inference test.

If the request is too open to name an observable outcome, a caller or actor, and one demonstrable use case, suggest the `shape-project` skill, name the missing product decisions, and wait. A blank repository alone is not a reason to redirect: keep a concrete feature request in `settle`.

## The inference test

Enumerate every decision the work depends on. Put each through this test before it earns a place in a round.

Find its **nearest precedent** first: search the feature folder you are changing, then its parent, then the repo. The nearest layer that settles the decision wins. A large codebase carries competing patterns repo-wide while the folder you are touching has already picked one, so a repo-wide search reports a tie where the local answer is plain. Escalate to a question only when the *nearest* layer is split.

| What you find | What you do |
| --- | --- |
| One established way | Resolve as `A<n>`. Cite the code. |
| Two or more live patterns, nearest layer split | **Ask.** A real fork. |
| No precedent, and the choice affects product behaviour, a public contract, persistent data, security, deployment, or several slices | **Ask.** |
| No precedent, and the choice is invisible outside implementation and reversible within one slice | Resolve as `D<n>`. Record the reason and reversal cost. |

With a local precedent, the test resolves error handling, loading and empty states, toasts, naming, file placement, exports, i18n key placement, styling, test location, types, state, logging, and analytics wiring. Without a precedent, apply the table rather than assuming these remain cheap.

Discover conventions live each session. A convention list written into this file goes stale; the codebase cannot.

## Rounds

Work the decisions as a tree. The **frontier** is every decision whose prerequisites are settled, so you can ask without guessing at an answer you have not heard. Ask the whole frontier in one round, then wait. A question whose answer depends on another question open in this round belongs to a later round.

There is no question budget. If eight genuine forks survive the inference test, ask eight.

Each round prints the code-backed assumptions and no-precedent defaults new to that round, then the questions:

```
Assumed from the codebase; reopen any by number
A1. Errors surface through useCommonErrorHandling · <the file:line you actually found it in>

Defaults where no precedent exists; reopen any by number
D1. Put feature tests beside their source files · no precedent; local and reversible within this slice

Q1. <title>: <body, options>
Recommended: <your answer and why>
```

When the user reopens an assumption or default, it becomes a question on the current frontier.

## Facts are yours to find

Find targeted facts inline. Delegate a bounded discovery task when it needs a broad sweep, several sources, or an independent line of investigation that can run in parallel. Give the subagent the exact question, scope, and evidence expected. Treat its report as a lead: verify plan-shaping claims against the code or primary sources, and never treat external research as code precedent. While it runs, continue the frontier except for decisions that depend on its result.

## Contradictions

Every account of how the code works is a claim to check, whatever its source: the user, a note, a doc, a comment, a subagent's report. Read the code. Where the two disagree, surface it before the next round:

```
⚠️ <the claim>, from <source>. The code <what it actually does> · <file:line>. Which holds?
```

For claims about current behaviour, the code wins. When a note or doc loses, record that line as stale so it gets fixed. A deliberate request to change current behaviour is a decision, not a contradiction.

The same reading feeds both directions: the inference test finds what the code already decides, and this finds where the code contradicts what you were told.

## Slices

The interview produces a tree of **use cases**: things a user can do and you can demonstrate. Record the tree at full depth and emit slices at depth one. One slice is one session's work.

Every slice ends **green**: the code compiles and its tests pass. A slice that cannot end green merges into its neighbour, even when that makes it large. Green states exist only at use-case boundaries, which is why the tree decides the seams and size never does.

In a blank project, prefer a thin demonstrable use case that initializes only the tooling it needs. When setup cannot share a green boundary with that use case, allow one bootstrap slice first. It must leave a runnable project with its build, typecheck where applicable, test command, and a smoke check passing. It may not add infrastructure for later un-emitted use cases.

Slices run in order, and each names the cheapest verification that proves it green — an affected-only typecheck with the specs it touched, ahead of a full build whose output costs the next session's context.

Source each verification from the environment — a `package.json` script, a Makefile target, a documented command — and cite where you found it. A command you did not find is a command the next session cannot run. When it does not exist yet, mark it `to create` and name the slice that creates it.

A complete mechanical change (a rename, an enum migration, a signature change) is a legitimate slice, and it runs **first**. Left until last, it has to rewrite the files the earlier slices just wrote.

Size is a smell, never a cut. A slice reaching across many folders means the use case wants decomposing: ask the user whether to emit that node's children. The recorded tree makes a deeper emit free, in this session or a later one that reopens the plan directory.

## Exit

The session is done when the frontier is empty, every enumerated decision is a user answer, a code-backed `A<n>` assumption, or a reasoned `D<n>` default, and every slice has a command that will prove it green.

Present the goal, the ordered slices with each one's verification, and the `D<n>` defaults. Then wait for approval.

On approval, write the plan directory specified in [PLAN-FORMAT.md](PLAN-FORMAT.md).

Tell the user the absolute directory path and that `next-slice` runs the first slice.
