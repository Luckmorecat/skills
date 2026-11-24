# Stitch Fallback Review

Isolated fallback review ladder used only when fallback-only review was requested or `bin/review` returned `fallback_needed` (or could not run).

## Fallback reviewer

Instructions for the single fresh isolated review subagent (2 rounds max: Round 1 full, Round 2 delta on open IDs and changes since Round 1; solo reviewer with no nested subagents):

1. Review only. Do not edit, commit, push, or start subagents.
2. Inspect:
   - `git diff <base> -- <tracked owned paths>`
   - any untracked owned paths directly
   - surrounding callers/code and the listed repo rules (`AGENTS.md`, `CLAUDE.md`, or repo rule files)
3. Check both code quality and verbatim brief compliance in one pass:
   - Bugs, broken callers, regressions, and edge cases within intent.
   - Mismatch with the brief's acceptance, exclusions, or settled decisions; flag missing proof where passing commands alone do not demonstrate acceptance.
   - Breaches of documented repo rules; skip style unless it hides a bug.
   - Smallest-change discipline: flag dead code, tests, or guards the brief does not need.
4. Severity:
   - `blocker` = acceptance unmet, intended case wrong, security/data-loss defect, or mandatory repo rule breach.
   - `should` = real bug callers will hit in intent, or missing proof for an acceptance item.
   - `nit` = rare edge case, small perf, extra compat, style, or out-of-scope suggestion.
5. Reply concisely (findings only, under 400 words; omit praise):
   - Round 1:
     ```text
     VERDICT: APPROVE or CHANGES
     R1 [blocker|should|nit] <file>:<line> <claim>. Fix: <smallest suggestion>
     ```
   - Round 2 (delta pass): inspect open IDs and changes since Round 1 only; mark each old ID `resolved`, `deferred: <reason>` (accepted decline, nit, or non-blocking follow-up), or `still open: <reason>` (blocking item), report any new defect introduced by the fixes, and end with `VERDICT: APPROVE` (only when zero `blocker`, `should`, or `still open` items remain) or `VERDICT: CHANGES`.

## Worker fallback (when nested subagents are available)

1. Dispatch one fresh isolated review subagent (without your conversation history), passing the absolute path of this file (**Fallback reviewer**), the verbatim brief, `base`, any `dirty snapshot`, your `owned paths`, applicable repo rule paths, and verification evidence.
2. Handle findings using the triage rules in [WORKER.md](WORKER.md). If a `blocker` or `should` stays open or fixes change behavior code, dispatch one delta pass (Round 2) with the updated ledger, modified paths, and check results.
3. Stop once approved (`VERDICT: APPROVE` covering the current behavior diff, or only declined `nit`s remain) and proceed to commit in [WORKER.md](WORKER.md). If a `blocker` or `should` stays open after Round 2, stop uncommitted and escalate both sides to the orchestrator.

## Orchestrator fallback (when the worker cannot spawn subagents)

1. Dispatch one fresh isolated review subagent (without this conversation's history), passing the absolute path of this file (**Fallback reviewer**), the verbatim brief, `base`, any `dirty snapshot`, the worker's `owned paths`, applicable repo rule paths, and verification evidence.
2. **Approved (`VERDICT: APPROVE` or `nit`-only)**: commit the worker's `owned paths` directly yourself (stage only owned paths outside `dirty snapshot`, inspect `git diff --cached --stat`, exclude secrets/build artifacts/unrelated hunks, use semantic `type(scope): subject` with the worker's rationale).
3. **Changes needed (`blocker` or `should`)**: triage findings against session intent, decline out-of-scope items directly, and resume the same worker with accepted findings to fix, re-verify, and return uncommitted for one delta pass (Round 2). Once approved, commit the worker's `owned paths` directly yourself, resuming the worker only if hunk-level staging is needed.
4. **No subagents available anywhere**: review the diff yourself as a separate pass following **Fallback reviewer**, state explicitly that the review ran without isolation, fix accepted findings, and commit.
