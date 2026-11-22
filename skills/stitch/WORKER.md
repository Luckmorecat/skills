# Stitch Worker

Implement the orchestrator's brief, verify it green, run independent review, and commit cleanly in one continuous run.

## 1. Implement and verify

Start from the brief's **Starting points** before searching the repo. Keep context lean: use targeted searches and line ranges, redirect verbose test/build/browser output to temp log files outside the repository, and read back only exit status and failure lines (cite the log paths as evidence).

Honour the brief's scope, exclusions, and settled decisions. Leave every path in any `dirty snapshot` untouched; if the work must edit a path already in `dirty snapshot`, stop and report it rather than mixing hunks silently.

Write or update focused tests at the boundaries the brief changes. Run focused checks while iterating, then run the relevant check suite once before review; exercise the API or UI only where needed to prove acceptance, stopping once demonstrated. Skip a pre-edit baseline check when the starting state is clean and known.

Stop uncommitted and return to the orchestrator when:

- ambiguity changes the outcome, or a required choice would change approved behavior, public contracts, persistent data, security/privacy, deployment, external services, ongoing cost, or anything expensive to reverse;
- a failing tool or missing prerequisite leaves acceptance unproven.

## 2. Review

Below, `review <command>` means `python3 <review-cli> <command>`, where `<review-cli>` is the absolute path of this skill's `bin/review` passed by the orchestrator (`review <command> --help` documents every flag; `review config` shows effective defaults). `bin/review` owns prompt templates, model/effort/backend configuration, scratch session state, read-only execution, retries, resume fallback, and JSONL extraction.

- **Fallback-only requested**: skip `bin/review` and read [FALLBACK.md](FALLBACK.md).
- **Round 1**: write the orchestrator's brief **verbatim** (never summarized or trimmed) to a temp file outside the repo (or pipe via `--brief-file -`) and run:

```bash
python3 <review-cli> start \
  --repo <repo abs path> \
  --base <base> \
  --brief-file <brief file> \
  --owned-path <path>... \
  --evidence "<commands and pass/fail results>"
```

Pass `--backend`, `--model`, `--effort`, `--thread-mode`, or `--config` only when the orchestrator supplied overrides. Pass `--rule <path>...` only if applicable repo rule files exist beyond `AGENTS.md`, `CLAUDE.md`, or `.github/copilot-instructions.md` (which `bin/review` discovers automatically). Run in the background (or with a generous timeout) and wait for exit; leave owned paths untouched while review runs.

Branch on the stdout JSON `status` (non-zero exit with stderr is a caller/config error — fix your arguments, or move to [FALLBACK.md](FALLBACK.md) if `bin/review` itself cannot run):

- **`fallback_needed`**: read [FALLBACK.md](FALLBACK.md). Run **Worker fallback** if this runtime lets you dispatch a fresh subagent; otherwise stop uncommitted and return `Review status: fallback needed (<fallback_reason>)` with your `owned paths`, verification evidence, and proposed commit message so the orchestrator can run **Orchestrator fallback**.
- **`budget_exhausted`**: stop uncommitted and escalate both sides to the orchestrator; budget end is not approval.
- **`ok`**: read `verdict`, `nit_only`, and `findings` from the JSON response (never read raw `*.jsonl` logs). Keep a ledger (`id`, `severity`, `outcome`) and verify every finding in the code yourself:
  - **Agree (`blocker` / `should`)**: apply the smallest fix (prefer deleting or narrowing over adding abstractions, caches, or options), add one focused test if intent needs it, and rerun affected checks (plus the full relevant suite if fixes touched shared code).
  - **Disagree (factual)**: prepare evidence (`file:line`, test output, or brief quote) for the next round.
  - **Conflicts with the brief or expands scope**: push back once citing the brief; if the reviewer still insists on a later round, or if a finding exposes a genuine gap in the brief, stop uncommitted and escalate to the orchestrator with both sides in 2–3 lines.
  - **Out of scope or `nit`**: decline in one line and list as a follow-up.

Stop early once `verdict` is `APPROVE` covering the current behavior diff, or only declined `nit`s remain (confirmed in code) and no behavior code changed (comment, doc, or format-only edits need no new round). Otherwise run the next round:

```bash
python3 <review-cli> reply \
  --session <session> \
  --ledger-file <ledger file> \
  [--changed-path <path>...] \
  --evidence "<updated pass/fail results>"
```

Pass `--max-rounds <N> --extend-reason "<reason>"` (up to the session's `extended_max_rounds`, default 5) only for security, permissions, auth, data loss, or state/concurrency while a `blocker` or `should` stays open with evidence, or when the orchestrator asked. Pass `--fresh` on `reply` to start a new reviewer thread after a major rewrite or long pause.

Before returning, run `python3 <review-cli> receipt --session <session>` to collect the exact review receipt fields without guessing usage.

## 3. Commit

Commit only once checks are green and review returned `VERDICT: APPROVE` (or only declined `nit`s remain) covering the current behavior diff.

- Inspect `git status --porcelain`; stage only your `owned paths`, keeping every `dirty snapshot` path and unrelated hunk untouched.
- Inspect `git diff --cached --stat`; exclude secrets, build output, stray binaries, and unintended edits.
- Use imperative semantic commits (`type(scope): subject`, under 72 chars) with a concise rationale body. Split into multiple commits only when concerns are clearly distinct; keep implementation with its tests.
- Leave changes local unless the brief explicitly asks to push. A git or hook failure stops the run and reports uncommitted state.

## 4. Return receipt

Return:

- Commit SHA(s) and subjects (or uncommitted status if paused, blocked, or handing off to fallback review)
- `owned paths`
- Verification evidence (commands, pass/fail, temp log paths)
- Review receipt: backend, model and effort, rounds, final verdict, fixed and declined findings, usage if exposed (else say not exposed), and response paths from `review receipt` (or fallback receipt / `fallback needed: <reason>`)
- Proposed commit message/rationale (when returning uncommitted for fallback review)
- Any open questions, review disputes, follow-ups, or blockers
