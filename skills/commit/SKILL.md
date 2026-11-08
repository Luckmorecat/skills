---
name: commit
description: Use when committing changes.
---

Every commit carries one piece of work, named for the work rather than the files.

## Scope

Use the user's requested scope. With a caller, use the diff since their fixed point, excluding paths in their dirty snapshot. Reuse supplied verification and review evidence while it still matches the changes. For a direct request without a narrower scope, inspect the whole worktree. Treat existing staging as a hint about intent, not as a commit boundary.

## Hazards

Whatever the scope, set aside anything the user would want to see before it lands: secrets, build output, unexpected binaries, mass deletions, a file whose purpose you cannot establish. Name each one in the report. Include an excluded hazard only with explicit authorization for that path and risk, subject to applicable safety rules.

## Grouping

Group implementation with the tests, docs, schema, and config that complete it. Put unrelated features, fixes, refactors, docs, and tooling in separate commits. Assign whole files. Split a file by hunks only where it holds independent concerns and the hunks stage cleanly. Where a split fails either test, keep the file whole or leave it uncommitted, and say which.

## Message

Write a subject line in the imperative, under 72 characters, formatted `type(scope): subject`. Add a body only for content a caller supplies for the message, such as decisions or facts worth keeping: put it on the commits it concerns, after a blank line, wrapped at 72 characters. Types are `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `style`, `chore`. When a task ID is given, use it as the scope on the commits that genuinely belong to it, and leave the rest without a scope: `feat(UP-12170): wire validation config to scene usages`. Include trailers required by hooks or repository conventions.

## Execution

For each commit, take its paths from a fresh `git status --porcelain`, including both sides of renames and deletions, and stage them with `git add -A -- <paths>`. Read `git diff --cached` and correct the index when anything outside the group is in it. Stage a hunk split through the index with `git add -p` or `git apply --cached`, leaving working files untouched. Preserve unrelated working-tree changes and leave excluded staged changes available but out of these commits. Commit the chosen message, inspect the resulting commit, and continue to the next group. A git or hook failure stops the run: inspect whether a commit was created before retrying, and do not bypass hooks. Do not amend, rewrite history, or push unless requested.

## Report

On success, list the commits made, the hazards set aside, and anything left uncommitted with the reason. On failure, report the error, the commits already in, and what remains.
