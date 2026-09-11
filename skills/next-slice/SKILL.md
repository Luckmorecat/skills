---
name: next-slice
description: Implement one prepared slice, verify and review it, then commit and checkpoint progress.
disable-model-invocation: true
---

Execute the prepared slice.

## 1. Open

Take the plan directory or `spine.md` path supplied; ask when absent. Read the compact spine, current log state, selected slice, and relevant map entries. Use the plan's execution order and completed dependencies. If no prepared slice is available, hand back to `slice`.

Check repository and branch/worktree identity. For interrupted work or older plans, read [RECOVERY.md](RECOVERY.md).

For a new slice, save `in-progress`, the fixed point from `git rev-parse HEAD 2>/dev/null || git hash-object -t tree /dev/null`, and any `git status --porcelain` snapshot before implementation. On resume, retain the original baseline. Run the cheapest relevant baseline check; distinguish existing failures from regressions.

## 2. Implement

Build against the slice's acceptance and the shared constraints. Choose local implementation details within that contract. Use `tdd` at approved seams when available, otherwise follow the same test-first loop. Run focused checks during development and the full relevant suite at completion.

Correct stale code pointers and record discoveries as they occur. If a missing prerequisite or necessary scope/acceptance change prevents execution, checkpoint the concrete blocker and hand back to `slice` before dependent work.

## 3. Verify and review

Run the prepared verification and demonstrate acceptance, exercising the API or UI when needed. A milestone's final slice also runs its specified integrated check.

Invoke `code-review` when available with the original fixed point, dirty snapshot, later unrelated changes to exclude, slice, shared product contract and exclusions, relevant decisions, and verification evidence. Otherwise review standards and contract compliance separately. Fix blocking findings and rerun affected checks. For an experiment without code changes, assess its findings against its question and criteria instead of invoking a diff review.

## 4. Commit and checkpoint

Record owned changes and verification/review evidence before committing. Commit only this slice's verified work. Mark `complete` after recording landed revisions and acceptance evidence with no blocking findings; a no-code experiment records its result and unchanged revision.

Update progress and factual navigation. Log deviations, downstream findings, and the next action concisely. On a blocker or interruption, preserve the original baseline and owned changes as `blocked` or `in-progress`.

Stop after one slice by default. User-authorized bounded continuation may execute further prepared slices through the same gates; stop at the bound, a blocker, or an unprepared slice. Hand unprepared work to `slice`. Declare completion only when every approved outcome has evidence.
