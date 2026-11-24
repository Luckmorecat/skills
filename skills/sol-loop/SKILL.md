---
name: sol-loop
description: Use when the user says "sol loop" (or "sol-loop").
---

Review a change in a read-only loop with GPT Sol through `bin/review` (defaulting to `gpt-6.2-sol` at `xhigh`). Fix confirmed defects with the smallest change, hold scope tight, and push back with evidence on unsound claims.

## 1. Scope and checks

Inspect `git status --short`; leave unrelated changes untouched. Pass `--path` to limit review to the change's paths when they separate cleanly from unrelated dirty files; stop and ask if hunks overlap.

Resolve `base`:

- **PR**: run `gh pr view <n> --json baseRefName,headRefOid`. Fetch the remote when available. Check out the PR branch only when clean; if dirty on another branch, stop and ask. Confirm `HEAD` is the PR head (or ahead only by this change), then use `git merge-base HEAD origin/<baseRefName>` (or local `<baseRefName>` if offline).
- **Local**: fetch the remote when available and use `git merge-base HEAD origin/<default-branch>` (falling back to the local default branch, a user-named base, `HEAD` for uncommitted changes, or `git hash-object -t tree /dev/null` before the first commit).

Confirm the change is non-empty. State **intent** and **out-of-scope** in 1–2 sentences. Run covering checks and fix regressions this change introduces before review; record missing or pre-failing checks.

## 2. Run Sol

Below, `<review-cli>` is the absolute path of `bin/review` in this skill's directory (`python3 <review-cli> <command> --help` documents every flag). `bin/review` owns prompt assembly, `gpt-6.2-sol`/`xhigh` defaults, read-only `codex exec` and `resume` execution, single transient retry, fresh-thread fallback with prior findings, verdict validation, diff stats, and cumulative-usage JSONL extraction.

Start Round 1 (one solo reviewer; run in the background or with a generous timeout such as 15 minutes for `xhigh` and wait for exit; leave scoped files untouched while review runs):

```bash
python3 <review-cli> start \
  --repo <repo abs path> \
  --base <base> \
  --intent "<intent>" \
  --out-of-scope "<out-of-scope>" \
  [--path <path>...] \
  --checks "<commands and pass/fail results>"
```

Use `--intent-file`, `--out-of-scope-file`, or `--checks-file` for multi-line text. Pass `--model`, `--effort`, `--thread-mode`, or `--max-rounds` only when the user overrides them; pass `--rule <path>...` only for extra repo rules beyond auto-discovered `AGENTS.md`, `CLAUDE.md`, and `.github/copilot-instructions.md`.

Branch on the stdout JSON `status` (exit 2 with stderr is a caller/input error — fix arguments):

- **`blocked`**: stop and report `blocker_reason` to the user. Never substitute another model.
- **`budget_exhausted`**: go to Step 4 (**Stuck**); budget end is not approval.
- **`ok`**: read `verdict`, `nit_only`, and `findings` from stdout JSON (never read raw `*.jsonl` logs).

## 3. Answer findings

Verify every finding and severity in the code yourself; other paths, rare edge cases, and small perf costs stay `nit` regardless of label.

- **Agree (`blocker` / `should`)**: apply the smallest fix (prefer deleting or narrowing over new helpers, caches, locks, or options), add one focused regression test if intent needs it, trim unnecessary added code, and rerun checks.
- **Disagree**: gather factual evidence (`file:line`, test, or command output).
- **Out of scope or `nit`**: decline in one line and track as a follow-up.

Update your ledger (`fixed:` / `disagree:` / `declined:` + evidence).

Stop the loop once `verdict` is `APPROVE` (or `nit_only` is true, confirmed in code) covering the current behavior diff — declined nits and comment, doc, or format-only edits need no new round. Stop as **Stuck** if a finding stays disputed with no new evidence after an evidence-backed rebuttal (or after two replies on an extended budget).

Otherwise run the next round:

```bash
python3 <review-cli> reply \
  --session <session> \
  --ledger-file <ledger file> \
  [--changed-path <path>...] \
  --checks "<updated pass/fail results>"
```

Default budget is 3 rounds. Pass `--max-rounds 5 --extend-reason "<reason>"` only for security, permissions, auth, data loss, or state/concurrency while a `blocker` or `should` stays open with evidence, or when the user asks. Pass `--fresh` to start a new Sol thread after a major rewrite.

## 4. Stop and ship

Run `python3 <review-cli> receipt --session <session>` to collect exact rounds, model, effort, before/after diff stats, and usage without guessing.

- **Agreed**: `APPROVE` or `nit`-only on the current behavior diff, no open `blocker` or `should`, and no remaining concern of your own.
- **Stuck**: unresolved dispute or budget exhausted — show both sides in 2–3 lines each and let the user decide.

Leave changes local during the loop. Push or update a PR after agreement only when the user asked; if updating a PR description, append:

`Reviewed with sol-loop: <N> rounds with <model> (<effort>). Sol verdict: <approved | nits only>.`

Report: rounds, model and effort, what Sol changed, diff size before/after, fixed and declined findings with reasons, usage if exposed (else say not exposed), and pushed/PR status.
