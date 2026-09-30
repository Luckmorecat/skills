---
name: no-comments
description: Delete comments from a scoped change through an isolated subagent, fix trivial refactor flags, and report the rest.
disable-model-invocation: true
---

Delete comments from the scope the user names through a fresh subagent, then audit its work. The subagent did not write the code, so it judges each comment without the author's attachment to it.

Use the files or diff the user names. Otherwise use the changes since the merge base with the default branch, including staged, unstaged, and untracked files. Resolve the scope to concrete paths and copy those files to a scratch directory, so the sweep's own changes can be diffed with `git diff --no-index`.

Dispatch a fresh subagent with the scope and the absolute path of [SICKO.md](SICKO.md), instructing it to read and follow that file. Do not restate its rules. Without subagents, sweep in a separate pass and state that the sweep ran without isolation.

Audit the sweep's diff against its report. Reject edits to code, edits outside the scope, deletions that meet an exception in [SICKO.md](SICKO.md), and flags that misname a symbol or misstate the reason. Restore a deleted comment only when you can show which exception it meets; a kept comment that fails its exception is deleted. Check the scope for suppressions the sweep missed. On a rejected report, restore the files, dispatch once more naming the failure, and stop with the scope restored and the failure reported if the second report fails too.

Fix trivial `MUST KILL` flags directly: deleting a dead path, dropping an unused parameter, calling the real API, or renaming a local symbol. A trivial fix stays inside the scope, keeps public contracts and behavior, and is proven by existing checks. Leave every other flag for the report. When a deleted suppression's fix is not trivial, restore the suppression so checks keep passing and report the flag.

Run the repository's relevant checks on the scope; a deleted directive or suppression can break the build even though no code changed. Leave the changes uncommitted for `commit`.

Report files touched, the deletion count, restored comments with their exceptions, reruns, and trivial fixes. List each open `MUST KILL` flag in one line with its next step: `design` when the reshape is a decision, `land` when it is settled. List deleted constraint claims so the user can encode any that still matter in a type, test, or lint rule.
