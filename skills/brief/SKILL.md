---
name: brief
description: Interview the user on the few forks a small task genuinely has, then write one plan document to implement from.
disable-model-invocation: true
---

One task, one green state, one document. Every decision you can settle from the codebase you settle yourself and report as an assumption. A question the codebase already answers is a question you failed to research.

The code is the only source of truth. Every ledger line cites a `file:line` you read this session. Notes, docs, and the user's recollection supply leads worth checking; the code supplies the answer.

## The inference test

Enumerate every decision the work depends on. Put each through this test before it earns a question.

Find its **nearest precedent** first: search the feature folder you are changing, then its parent, then the repo. The nearest layer that settles the decision wins. A large codebase carries competing patterns repo-wide while the folder you are touching has already picked one, so a repo-wide search reports a tie where the local answer is plain. Escalate to a question only when the *nearest* layer is split.

| What you find | What you do |
| --- | --- |
| One established way | Resolve. Log it with evidence. |
| Two or more live patterns, nearest layer split | **Ask.** A real fork. |
| No precedent, and the choice shows up in product behaviour, the data contract, or an API | **Ask.** |
| No precedent, and the choice is invisible or cheap to reverse | Resolve. Log it. |

Decisions the test resolves nearly every time: error handling, loading and empty states, toasts, naming, file placement, barrel exports, i18n key placement, styling, test location and framework, enum-versus-union, the state layer, logging and analytics wiring.

Decisions that survive it: product behaviour at a genuine fork, scope boundaries, the data contract and who changes the backend, migration and backfill of existing data, anything irreversible or cross-cutting, and tradeoffs with no local precedent.

Discover conventions live each session. A convention list written into this file goes stale; the codebase cannot.

## Questions

Most small tasks hold no genuine fork at all. Ask whatever survives the test, the whole of it in one round, then wait. When nothing survives, present the ledger and the brief in one turn.

Grep and read inline for each fact you need. A task wanting a sweep across many files is usually one `settle` should take.

Print the ledger first, then the questions:

```
📋 Assumed from the codebase — reopen any of these by number
A1. <the assumption> · <the file:line you found it in>

❓ Q1 — <title>: <body, options>
➡️ <your recommended answer>
```

A ledger entry the user reopens becomes a question.

## Contradictions

Every account of how the code works is a claim to check, whatever its source: the user, a doc, a comment. Read the code. Where the two disagree, surface it before you write anything:

```
⚠️ <the claim>, from <source>. The code <what it actually does> · <file:line>. Which holds?
```

The code wins.

## Work too large for a brief

Stop when the interview reveals the work cannot reach green in one pass — it needs a mechanical change ahead of the feature, or it spans folders that have to land separately, or a fork opens forks under it. Say which, and hand it to `settle`.

A short interview thrown away costs less than a document built on the wrong shape, so raise this the moment you see it rather than at the end.

## Exit

The session is done when every enumerated decision is either a user answer or a ledger line carrying evidence. Present the brief and wait for approval.

On approval, write it where `settle`'s plan directories live, so one place holds both:

```bash
repo=$(basename "$(git rev-parse --show-toplevel)")
mkdir -p "/tmp/plans/$repo"
```

Write one file, `/tmp/plans/<repo>/<date>-<slug>.md`, taking the date from `date +%F`:

- **Goal** — what the work delivers, in a few lines.
- **Decisions** — each answer from the interview, with the reasoning that produced it.
- **Ledger** — every assumption, each citing the `file:line` it came from.
- **Out of scope** — what was considered and excluded, so the build does not reopen it.
- **Build** — the change, as behaviour rather than keystrokes.
- **Paths** — the files to read and write, one line each on what changes there.
- **Verify** — the command that proves the work green.

There is no log. One session does this work and commits it, which makes the commit message the record, and anything worth keeping past the task belongs there or in a test.

Tell the user the path and that `implement` builds it.
