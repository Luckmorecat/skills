---
name: brief
description: Interview the user on the few forks a small task genuinely has, then present one implementation brief.
disable-model-invocation: true
---

One task, one green state, one brief. Every decision the codebase settles you settle yourself and report as an assumption. A question the codebase already answers is a question you failed to research.

Code is the only source of truth for current behaviour; user answers are the source of truth for desired behaviour. Every code-backed line cites a `file:line` read this session.

## The inference test

Enumerate every decision the work depends on, the small ones included: error handling, loading and empty states, naming, file placement, styling, test location, types, logging. Each decision passes this test before it earns a question.

Find its **nearest precedent**: the feature folder you are changing, then its parent, then the repo. The nearest layer that settles the decision wins, so a repo-wide tie is not a fork while the local folder has already picked. Escalate to a question only when the nearest layer is split.

| What you find | What you do |
| --- | --- |
| One established way | Resolve as `A<n>`. Cite the code. |
| Two or more live patterns at the nearest layer | **Ask.** A real fork. |
| No precedent, and the choice touches product behaviour, a public contract, persistent data, security, or deployment | **Ask.** |
| No precedent, and the choice is invisible outside the implementation and reversible within this session | Resolve as `D<n>`. Record the reason. |

Absence of code proves only that no precedent exists.

## Questions

Most small tasks hold no genuine fork. Ask whatever survives the test, the whole of it in one round, then wait. When nothing survives, present the brief in one turn.

Each round prints the `A<n>` and `D<n>` lines new to it, then the questions, as plain text in exactly this shape:

```
Assumed from the codebase; reopen any by number
A1. <the assumption> · <the file:line you read>

Defaults where no precedent exists; reopen any by number
D1. <the default> · no precedent; reversible within this session

Q1. <title>: <body, options>
Recommended: <your answer and why>
```

The labels are the interface. Number them once per session, never reuse one, and keep them in the round's text: a question-picker tool drops them. A reopened `A<n>` or `D<n>` becomes a question. When the user defers a question to you, your recommendation becomes the decision, recorded with its reason and the deferral.

## Contradictions

Every account of how the code works is a claim to check, whatever its source: the user, a doc, a comment. Read the code. Where the two disagree, surface it before you write anything:

```
⚠️ <the claim>, from <source>. The code <what it actually does> · <file:line>. Which holds?
```

The code wins.

## Work too large for a brief

Grep and read inline for each fact you need. Stop the moment the work shows it cannot reach green in one pass: it wants a sweep across many files, a mechanical change ahead of the feature, folders that have to land separately, or a fork that opens forks under it. Say which, and hand it to `settle`. A short interview thrown away costs less than a brief built on the wrong shape.

## Exit

The session is done when every enumerated decision is a user answer, a code-backed `A<n>`, or a reasoned `D<n>`. Present the complete brief with these sections and stop. Write it to disk only when the work will run in another session; [HANDOFF.md](HANDOFF.md) says how.

- **Goal** — what the work delivers, in a few lines.
- **Decisions** — each answer from the interview, with the reasoning that produced it.
- **Ledger** — every `A<n>`, citing its `file:line`, and every `D<n>`, with its reason.
- **Out of scope** — what was considered and excluded, so the build does not reopen it.
- **Build** — the change, as behaviour rather than keystrokes.
- **Paths** — the files to read and write, one line each on what changes there.
- **Verify** — the command that proves the work green, and where in the environment you found it: a `package.json` script, a Makefile target, a documented command. The implementing session runs it as the gate, so a command you did not find is a gate that will not hold.
