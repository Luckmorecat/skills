# Stitch Review

Shared review specification for the worker's **Codex review loop** and the **Fallback review** ladder.

## Review prompt (Round 1)

Use this prompt verbatim as the Round 1 review brief, filling in the bracketed fields with the orchestrator's **verbatim** brief (never summarized or trimmed):

```text
Review only. Do not edit, commit, push, or start subagents.
Repo: <repo abs path>
Base: <base sha>
Owned paths: <modified, added, and deleted paths>
Repo rules: <paths of applicable AGENTS.md, CLAUDE.md, or repo rule files, or "none found">
Verification evidence: <commands and pass/fail results>

Brief (verbatim):
<verbatim orchestrator brief>

Inspect:
- git diff <base> -- <tracked owned paths>
- read any untracked owned paths directly
- read surrounding callers/code and the listed repo rules

Check both code quality and brief compliance in one pass:
1. Bugs, broken callers, regressions, and edge cases within intent.
2. Mismatch with the brief's acceptance, exclusions, or settled decisions; flag missing proof where passing commands alone do not demonstrate acceptance.
3. Breaches of documented repo rules; skip style unless it hides a bug.
4. Smallest-change discipline: flag dead code, tests, or guards the brief does not need.

Severity:
- blocker = acceptance unmet, intended case wrong, security/data-loss defect, or mandatory repo rule breach.
- should = real bug callers will hit in intent, or missing proof for an acceptance item.
- nit = rare edge case, small perf, extra compat, style, or out-of-scope suggestion.

Reply concisely (findings only; omit praise):
VERDICT: APPROVE or CHANGES
R1 [blocker|should|nit] <file>:<line> <claim>. Fix: <smallest suggestion>
```

## Budget and stopping rules

- **Codex default**: 3 rounds total (Round 1 full; later rounds inspect only open IDs and code changed since the previous round). Extend to 5 rounds only for security, permissions, auth, data loss, or state/concurrency while a `blocker` or `should` stays open with evidence, or when the user asks.
- **Isolated subagent fallback**: 2 rounds max (Round 1 full; Round 2 delta on open IDs and changed code).
- **Early stop**: stop once a round returns `VERDICT: APPROVE` covering the current behavior diff, or returns only `nit`s. Declined nits and comment/doc/format-only edits need no new round.
- **One reviewer only**: the reviewer runs solo without spawning nested reviewers or subagents.

## Codex review loop

Defaults: model `gpt-6.2-sol`, reasoning effort `xhigh` (override with whatever model or effort the user named). Record both explicitly.

Create one scratch directory outside the repo (`mktemp -d`) and keep every prompt, output, and JSONL log there. Write each prompt via a single-quoted heredoc (`cat <<'EOF' > <scratch>/r<N>-prompt.txt`) so backticks and `$` in the brief never expand.

### Round 1

```bash
codex exec -C <repo abs path> -m <model> -c model_reasoning_effort=<effort> \
  -s read-only --json -o <scratch>/r1.md "$(cat <scratch>/r1-prompt.txt)" \
  < /dev/null > <scratch>/r1.jsonl
```

Run in the background (or with a generous timeout) and wait for exit; leave owned files untouched while review runs. Read findings from `r1.md`, `thread_id` from the `thread.started` JSONL event, and `usage` from `turn.completed` (record usage only when exposed; never guess).

### Failures

- Non-zero exit, empty output file, or missing `VERDICT:` line is a failure, not approval.
- If `codex` is missing, not logged in, blocked by sandbox/network, or rejects the model, move to **Fallback review** immediately without substituting a model.
- On a transient failure (truncated output or missing `VERDICT:` line), retry the round once cleanly; if it fails again, move to **Fallback review**.

### Round N (resume)

Start a new round only when budget remains and a `blocker` or `should` is open, behavior code changed, or approval does not cover the current behavior diff.

Write `<scratch>/r<N>-prompt.txt` containing: the updated ledger (`fixed:` / `disagree:` / `declined:` with `file:line` and check evidence), the paths modified or added since the previous round, the same `git diff <base> -- <owned paths>` reference, updated verification results, and the instruction:

> Review open IDs and changed code only. Mark each open ID `resolved` or `still open: <reason>`, report any new defect introduced by the fixes, and end with `VERDICT: APPROVE` or `VERDICT: CHANGES`.

Resume the saved thread:

```bash
codex exec resume <thread_id> -m <model> -c model_reasoning_effort=<effort> \
  -c sandbox_mode='"read-only"' --json -o <scratch>/r<N>.md "$(cat <scratch>/r<N>-prompt.txt)" \
  < /dev/null > <scratch>/r<N>.jsonl
```

If `resume` fails, start a fresh `codex exec` thread using the Round 1 command with the Round 1 prompt plus the Round N message appended, and keep the new `thread_id`.

## Fallback review

Use when fallback-only review was requested or Codex is unavailable.

### Fallback reviewer

Instructions for the single fresh isolated review subagent:

1. Follow the **Review prompt (Round 1)** rules above in a single read-only pass (do not edit files or spawn subagents).
2. Inspect `git diff <base> -- <tracked owned paths>`, read untracked owned paths, check surrounding callers and applicable repo rule files, and compare implementation and verification evidence against every acceptance bullet in the brief.
3. Return `VERDICT: APPROVE` or `VERDICT: CHANGES` followed by `R1...` findings only (under 400 words). On Round 2 (delta pass), review only open IDs and changes since Round 1, marking each old ID `resolved` or `still open: <reason>`.

### Worker fallback (when nested subagents are available)

1. Dispatch one fresh isolated review subagent (without your conversation history), passing the absolute path of this file (**Fallback reviewer**), the verbatim brief, `base`, any `dirty snapshot`, your `owned paths`, applicable repo rule paths, and verification evidence.
2. Handle findings using the rules in [WORKER.md](WORKER.md). If a `blocker` or `should` stays open or fixes change behavior code, dispatch one delta pass (Round 2) with the updated ledger, modified paths, and check results.
3. Once approved (`APPROVE` or `nit`-only), proceed to commit in [WORKER.md](WORKER.md).

### Orchestrator fallback (when the worker cannot spawn subagents)

1. Dispatch one fresh isolated review subagent (without this conversation's history), passing the absolute path of this file (**Fallback reviewer**), the verbatim brief, `base`, any `dirty snapshot`, the worker's `owned paths`, applicable repo rule paths, and verification evidence.
2. **Approved (`APPROVE` or `nit`-only)**: commit the worker's `owned paths` directly yourself (stage only owned paths outside `dirty snapshot`, inspect `git diff --cached --stat`, exclude secrets/build artifacts/unrelated hunks, use semantic `type(scope): subject` with the worker's rationale).
3. **Changes needed (`blocker` or `should`)**: triage findings against session intent, decline out-of-scope items directly, and resume the same worker with accepted findings to fix, re-verify, and return uncommitted for one delta pass (Round 2). Once approved, commit the worker's `owned paths` directly yourself, resuming the worker only if hunk-level staging is needed.
4. **No subagents available anywhere**: review the diff yourself as a separate pass following **Fallback reviewer**, state explicitly that the review ran without isolation, fix accepted findings, and commit.
