---
name: next-slice
description: Implement one prepared slice, verify and review it, then commit and checkpoint progress.
disable-model-invocation: true
---

Execute the prepared slice.

Run state (repository and target, status, baseline, and landed revisions, kept in `state.json`, with status mirrored in `plan.md`'s status block) changes only through `plan`. Below, `plan <command>` means `python3 <cli> --plan <dir> <command>`, where `<dir>` is the plan directory and `<cli>` is `../slice/bin/plan` resolved from this skill's directory to an absolute path. When that file is missing or lacks a command used here, stop and report that `slice` must be installed or updated beside this skill. `plan <command> --help` documents each command.

When your caller has already started the slice and limits your writes in the plan directory, that slice is the chosen one and its baseline is the one the caller supplies; leave every `plan` command that writes, `import` included, to the caller. Read the run state from `plan status`, or, when the plan has no `state.json`, from `plan.md` and `checkpoints/<ID>.md`.

## 1. Open

Use the plan directory or `plan.md` path supplied or established in context; ask when absent. When the directory has no `state.json`, run `plan import <dir>` before anything else; if the import fails, stop and report its error.

Read the run state with `plan status` and the shared context in `plan.md`. Interrupted work is a slice without a worktree that is in progress, or blocked with a recorded fixed point. Continue interrupted work through [RECOVERY.md](RECOVERY.md); a blocked slice continues once its blocker is resolved. When the user selects another slice, first block the in-progress one (step 4). Otherwise choose a slice that `plan next` lists, honoring a user-selected slice when listed. For a selected slice that can neither continue nor start, report what `plan status` gives for it: its blocked reason, unfinished dependencies, or scheduling constraint. If nothing is eligible, report the blockers; incomplete descriptions return to `slice`. Then read the chosen slice file.

Check that the checkout is the run state's repository on its target branch, or the worktree branch your caller supplied; resolve an unexplained mismatch before editing.

Start a new slice in the repository checkout with `plan start <ID>`; it records the fixed point and dirty snapshot and creates the checkpoint `checkpoints/<ID>.md`. Run the cheapest relevant baseline check; distinguish existing failures from regressions.

## 2. Implement

Build against the slice's acceptance and the shared constraints. Inspect the relevant implementation and discover current verification commands before editing; create missing checks needed to prove acceptance. Resolve consequential choices that change agreed behavior, including the plan's prototype reference, interfaces, data, security/privacy, deployment, dependencies, cost, or ownership with the user before dependent work, unless already approved or delegated. Use `tdd` at approved seams when available, otherwise follow the same test-first loop. Run focused checks during development and the full relevant suite at completion.

Correct stale code pointers and record discoveries in the checkpoint as they occur. If a missing prerequisite or necessary scope/acceptance change prevents execution, checkpoint the concrete blocker, block the slice (step 4), and hand back to `slice` before dependent work.

## 3. Verify and review

Demonstrate the slice's acceptance using the specified verification and current repository checks, exercising the API or UI when needed. Run any assigned integration checks across completed slices.

Invoke `code-review` when available with the original fixed point, dirty snapshot (`plan status --json`), later unrelated changes to exclude, slice, shared agreed outcomes, constraints and exclusions, relevant decisions, and verification evidence. Otherwise review standards and contract compliance separately. Fix blocking findings and rerun affected checks. For an experiment without code changes, assess its findings against its question and criteria instead of invoking a diff review.

## 4. Commit and checkpoint

Keep `checkpoints/<ID>.md` current: owned changes, verification/review evidence, deviations, stale-pointer corrections, and the next action, recorded before committing. Correct stale factual pointers in the plan's prose and slice files. Add each downstream finding to the file of the slice it affects under `## Notes`, naming this slice; hand one that would change that slice's scope or acceptance to `slice` instead.

Commit only this slice's verified work. With no blocking findings, run `plan complete <ID> --rev <sha> --evidence <text|@file>`, repeating `--rev` for every commit the slice landed and summarizing the acceptance evidence and review outcome; it folds the checkpoint into `log.md`. A no-code experiment passes its unchanged fixed point as `--rev` and its result as evidence.

On a blocker or interruption, run `plan block <ID> --reason <what resolves it>`, leaving the checkpoint and owned changes in place.

Stop after one slice by default. User-authorized bounded continuation may execute further eligible slices through the same gates. Stop at the bound or when no eligible slice remains; report unresolved blockers with the plan path. Declare completion only when every agreed outcome, including required integration checks, has evidence.
