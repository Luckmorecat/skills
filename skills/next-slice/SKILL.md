---
name: next-slice
description: Run one slice of an approved plan directory, then correct the plan with what the work revealed.
disable-model-invocation: true
---

You open a plan directory with no memory of the interview that produced it. `spine.md`, `map.md`, and the log are the whole inheritance. Run one slice, and leave the directory true for the session that follows.

Existing code is the only source of truth for claims about current behaviour. The plan carries approved intent and may also contain planned paths for a blank project. Treat those paths as work to create and verify, not as code already inspected.

## 1. Open

Take the path the user names: `spine.md`, or the directory holding it. That directory is the plan. When no path is named, ask.

Read `spine.md`, `map.md`, `log.md`, and the lowest-numbered slice file with no entry in the log. Read no other slice file: reading ahead tempts you into building work that is not yours yet.

Record this slice's fixed point with `git rev-parse HEAD 2>/dev/null || git hash-object -t tree /dev/null`, which yields the empty tree in a repository whose first commit has not landed. When the tree is already dirty, record `git status --porcelain` too and carry it to the review.

## 2. Build

- The slice's **Build** section is the work contract.
- `spine.md`'s **Out of scope** is the boundary, and it holds even when the code makes an excursion look cheap.
- The slice's **Verify** command is what proves the slice green. A verification marked `to create` does not exist yet, and creating it is part of this slice's Build.

Use the `tdd` skill at the slice's approved seams when it is available; otherwise follow the same test-first loop directly. Run typechecking and focused tests regularly, then run the full relevant suite once at the end.

When the implementation is green, invoke the `code-review` skill when it is available, passing the fixed point you recorded, the pre-existing snapshot when you took one, and the slice file plus `spine.md`'s **Out of scope** as the work contract. Otherwise inspect the diff against those same two axes directly. Fix every blocking finding and rerun the verification in full, so the tree you commit is the tree you verified.

## 3. Commit

Commit the work to the current branch.

A fact worth keeping past this work goes into the code, a test, or the commit message, so name it before committing. A test that fails when someone retries a dead end enforces where a note would only inform.

## 4. Reconcile

The work reveals what the interview could not know. Each finding goes one of two ways.

**The plan holds.** Record it in the log and carry on.

**The plan is wrong.** Edit `spine.md` now, while you still know why. Edit `map.md` too when this slice moved, renamed, or deleted something it points at: a stale path sends the next session to a file that is not there.

When this slice creates a planned traversal, replace that part of `map.md` with the paths the code now proves. When code invalidates a `D<n>` default, correct it without asking unless the correction changes approved behaviour, a public contract, persistent data, security, deployment, authentication, authorization, privacy, an external service, ongoing cost, or a later slice.

A ledger assumption the code disproved reports in the shape the interview used, and only when a later slice would do something different because of it:

```
⚠️ <the assumption>, from <spine.md ledger number>. The code <what it actually does> · <file:line>. Which holds?
```

A disproved assumption that changes nothing downstream needs no question. Correct the spine and log it.

## 5. Log

Append one entry to `log.md`: what landed, what deviated from the plan and why, and what the next slice needs to know.

A log, not a report. The next session pays context for every line, and it reads this to start work rather than to admire yours.

## 6. Hand off

Name the slice that comes next and stop. A second slice in the same session spends the context that slicing exists to protect.

When no slice remains, say so, and say which unmarked nodes of the use-case tree in `spine.md` are still unemitted. Reopening the plan is a `settle` session, not this one.
