---
name: commit
description: Group changes into semantic commits and create them. Use when the user asks to commit, with or without a ticket ID, or when a skill hands over a verified tree.
---

Every commit carries one piece of work, named for the work rather than the files.

## Scope

With a caller, the scope is the diff since the fixed point they supplied, excluding the paths in the dirty snapshot they handed over. That tree arrived green and reviewed, so skip verification. Without a caller, the scope is the whole worktree. Treat existing staging as a hint about intent, not as a commit boundary.

## Hazards

Whatever the scope, set aside anything the user would want to see before it lands: secrets, build output, unexpected binaries, mass deletions, a file whose purpose you cannot establish. Name each one in the report. A hazard comes back in only when the user names its path specifically; plan approval covers the plan and never a hazard.

## Grouping

Group implementation with the tests, docs, schema, and config that complete it. Put unrelated features, fixes, refactors, docs, and tooling in separate commits. Assign whole files. Split a file by hunks only where it holds independent concerns and the hunks stage cleanly. Where a split fails either test, keep the file whole or leave it uncommitted, and say which.

## Message

Write a subject line only, in the imperative, under 72 characters, formatted `type(scope): subject`. Types are `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `style`, `chore`. When a task ID is given, use it as the scope on the commits that genuinely belong to it, and leave the rest without a scope: `feat(UP-12170): wire validation config to scene usages`. Where a hook or repository convention requires a trailer, show the finished message with the trailer in the plan.

## Plan and approval

A caller-supplied scope arrived approved; go straight to execution. A worktree scope needs one plan first. List every commit in order with its message, purpose, exact files, the hunks where a file splits, the hazards set aside, and anything still ambiguous. Where a change could belong to more than one group, ask before writing the plan rather than guessing inside it. Ask once for the whole plan. A revision means a fresh plan and a fresh approval.

## Execution

For each commit, stage exact paths with `git add -- <paths>`, read `git diff --cached`, and correct the index when anything outside the group is in it. Stage a hunk split through the index with `git add -p` or `git apply --cached`, leaving working files untouched. Commit the approved message verbatim, then continue straight to the next commit, since the approval covered all of them. A git or hook failure stops the run.

## Report

On success, list the commits made, the hazards set aside, and anything left uncommitted with the reason. On failure, report the error, the commits already in, and what remains.
