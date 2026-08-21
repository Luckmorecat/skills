---
name: next-slice
description: Run one slice of an approved plan directory, then correct the plan with what the work revealed.
disable-model-invocation: true
---

You open a plan directory with no memory of the interview that produced it. `spine.md`, `map.md`, and the log are the whole inheritance. Run one slice, and leave the directory true for the session that follows.

Existing code is the only source of truth for claims about current behaviour. The plan carries approved intent and may also contain planned paths for a blank project. Treat those paths as work to create and verify, not as code already inspected.

## 1. Open

Take the plan directory the user names. Otherwise take the most recent under `/tmp/plans/<repo>/`. Derive `<repo>` from the Git root when `git rev-parse --show-toplevel` succeeds, or from the current directory name when it does not. Stop and ask when neither resolves: an absent directory means the plan was reaped or never written, and reconstructing the work is a different job than running a slice of it.

Read `spine.md`, `map.md`, `log.md`, and the lowest-numbered slice file with no entry in the log. Read no other slice file. A slice is self-sufficient by design, so reading ahead spends context on work that is not yours and tempts you into building it early.

## 2. Build

Hand the slice to `$implement`, or to whatever build-and-commit workflow the project provides.

- The slice's **Build** section is the work contract.
- `spine.md`'s **Out of scope** is the boundary, and it holds even when the code makes an excursion look cheap.
- The slice's **Verify** command is what proves the slice green.

A fact worth keeping past this work goes into the code, a test, or the commit message, so name it before `$implement` commits. Nothing in the plan directory survives the plan, and a test that fails when someone retries a dead end enforces where a note would only inform.

## 3. Reconcile

The work reveals things the interview could not know. Each one goes to one of two places.

**The plan holds.** Record it in the log and carry on.

**The plan is wrong.** Edit `spine.md` now, while you still know why. A false ledger line or a stale decision misleads every slice after this one, and the cost compounds with each. Edit `map.md` too when this slice moved, renamed, or deleted something it points at: a stale path sends the next session to a file that is not there, which is the one failure a map cannot survive.

When this slice creates a planned traversal, replace that part of `map.md` with the paths the code now proves. When code invalidates a `D<n>` default, correct it without asking unless the correction changes approved behaviour, a public contract, persistent data, or a later slice.

A ledger assumption the code disproved reports in the shape the interview used, and only when a later slice would do something different because of it:

```
⚠️ <the assumption>, from <spine.md ledger number>. The code <what it actually does> · <file:line>. Which holds?
```

For claims about current behaviour, the code wins. A disproved assumption that changes nothing downstream needs no question. Correct the spine and log it.

## 4. Log

Append one entry to `log.md`: what landed, what deviated from the plan and why, and what the next slice needs to know.

A log, not a report. The next session pays context for every line, and it reads this to start work rather than to admire yours.

## 5. Hand off

Name the slice that comes next and stop. A second slice in the same session spends the context that slicing exists to protect.

When no slice remains, say so, and say which unmarked nodes of the use-case tree in `spine.md` are still unemitted. Reopening the plan is a `settle` session, not this one.
