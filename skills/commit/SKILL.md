---
name: commit
description: Group changes into semantic commits and create them. Use when the user asks to commit, with or without a ticket ID, or when a skill hands over a verified tree.
---

Every commit carries one piece of work, named for the work rather than the files.

The scope is the change since the fixed point a caller supplied, less the paths in the dirty snapshot handed over with it: that tree arrived green and reviewed, so commit it as it stands and reverify nothing. Without a caller, the scope is the whole worktree, where existing staging is a hint about intent rather than a commit boundary.

Set aside whatever the user would want to see before it lands — secrets, build output, unexpected binaries, mass deletions, a file whose purpose you cannot establish — and name it in the report. Only a path the user names specifically comes back in, because `approve` covers the plan and never a hazard.

Implementation travels with the tests, docs, schema, and config that complete it, and unrelated features, fixes, refactors, docs, and tooling travel separately. Assign whole files; split one by hunks only where it holds independent concerns and stages cleanly, and where it does not, keep it together or leave it uncommitted and say so.

Subject only, imperative, under 72 characters, from `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `style`, `chore`. A task ID scopes the commits that genuinely belong to it — `feat(UP-12170): wire validation config to scene usages` — and leaves the rest unlabelled. Where a runtime mandates a footer, the plan shows the finished message before anyone approves it.

A caller-supplied scope arrived approved, so commit it. A worktree scope earns one plan first: every commit in order, with message, purpose, exact files, the hunks where a file splits, the hazards you set aside, and anything still ambiguous. Ask once, for the whole plan; a revision means a fresh plan and a fresh approval. Ambiguity about which group a change belongs to is a question before the plan rather than a guess inside it.

Stage exact paths with `git add -- <paths>`, read `git diff --cached` back, and correct the index when anything outside the group is in it. Commit the approved message to the character, then continue straight to the next one, because the approval covered all of them. Stage an approved hunk split through the index; the working file is not a scratch pad for making boundaries. A git or hook failure stops the run: report the error, the commits already in, and what remains.
