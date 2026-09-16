---
name: next-slice
description: Implement one prepared slice, verify and review it, then commit and checkpoint progress.
disable-model-invocation: true
---

Execute the prepared slice.

## 1. Open

Use the plan directory or `plan.md` path supplied or established in context; ask when absent. Read the shared context, dependency table, current log checkpoint, and selected slice. Choose a ready slice whose dependencies are complete, honoring a user-selected slice when eligible. If the selected slice is blocked, identify its missing prerequisite. If no eligible slice exists, report the blockers; incomplete descriptions return to `slice`.

Check repository and branch/worktree identity. For interrupted work or an older plan using `spine.md`, read [RECOVERY.md](RECOVERY.md).

For a new slice, mark its status and checkpoint `in-progress`. Before implementation, record the fixed point from `git rev-parse HEAD 2>/dev/null || git hash-object -t tree /dev/null` and any `git status --porcelain` snapshot. On resume, retain the original baseline. Run the cheapest relevant baseline check; distinguish existing failures from regressions.

## 2. Implement

Build against the slice's acceptance and the shared constraints. Inspect the relevant implementation and discover current verification commands before editing; create missing checks needed to prove acceptance. Resolve consequential choices that change agreed behavior, interfaces, data, security/privacy, deployment, dependencies, cost, or ownership with the user before dependent work, unless already approved or delegated. Use `tdd` at approved seams when available, otherwise follow the same test-first loop. Run focused checks during development and the full relevant suite at completion.

Correct stale code pointers and record discoveries as they occur. If a missing prerequisite or necessary scope/acceptance change prevents execution, checkpoint the concrete blocker and hand back to `slice` before dependent work.

## 3. Verify and review

Demonstrate the slice's acceptance using the specified verification and current repository checks, exercising the API or UI when needed. Run any assigned integration checks across completed slices.

Invoke `code-review` when available with the original fixed point, dirty snapshot, later unrelated changes to exclude, slice, shared agreed outcomes, constraints and exclusions, relevant decisions, and verification evidence. Otherwise review standards and contract compliance separately. Fix blocking findings and rerun affected checks. For an experiment without code changes, assess its findings against its question and criteria instead of invoking a diff review.

## 4. Commit and checkpoint

Record owned changes and verification/review evidence before committing. Commit only this slice's verified work. Mark the slice `complete` in the plan after recording landed revisions and acceptance evidence with no blocking findings; a no-code experiment records its result and unchanged revision.

Update the log checkpoint and correct stale factual pointers. Log deviations, downstream findings, and the next action concisely. On a blocker or interruption, preserve the original baseline and owned changes as `blocked` or `in-progress`.

Stop after one slice by default. User-authorized bounded continuation may execute further eligible slices through the same gates. Stop at the bound or when no eligible slice remains; report unresolved blockers with the plan path. Declare completion only when every agreed outcome, including required integration checks, has evidence.
