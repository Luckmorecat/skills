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

Read [REVIEW.md](REVIEW.md) and run review against `base` and your exact `owned paths` (every file you modified, added, or deleted), passing the orchestrator's brief **verbatim** in Round 1:

- **Default**: run the **Codex review loop** in [REVIEW.md](REVIEW.md).
- **Fallback** (when the orchestrator requested fallback-only review, or Codex fails/is unavailable per [REVIEW.md](REVIEW.md)): if this runtime allows you to dispatch a fresh subagent, run **Worker fallback** in [REVIEW.md](REVIEW.md) yourself. Otherwise stop uncommitted and return `Review status: fallback needed (<exact reason>)` with your `owned paths`, verification evidence, and proposed commit message so the orchestrator can run isolated fallback review.

Keep a ledger (`id`, `severity`, `outcome`) and verify every finding in the code yourself:

- **Agree (`blocker` / `should`)**: apply the smallest fix (prefer deleting or narrowing over adding abstractions, caches, or options), add one focused test if intent needs it, and rerun affected checks (plus the full relevant suite if fixes touched shared code).
- **Disagree (factual)**: prepare evidence (`file:line`, test output, or brief quote) for the next round.
- **Conflicts with the brief or expands scope**: push back once citing the brief; if the reviewer still insists on a later round, or if a finding exposes a genuine gap in the brief, stop uncommitted and escalate to the orchestrator with both sides in 2–3 lines.
- **Out of scope or `nit`**: decline in one line and list as a follow-up.

If review hits the round budget with a `blocker` or `should` still open, stop uncommitted and escalate both sides to the orchestrator; budget end is not approval.

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
- Review receipt: backend (`codex`, `worker fallback subagent`, or `fallback needed: <reason>`), model and effort (when Codex), rounds, final verdict, fixed and declined findings, usage if exposed (else say not exposed), and `<scratch>/r*.md` paths (when Codex)
- Proposed commit message/rationale (when returning uncommitted for fallback review)
- Any open questions, review disputes, follow-ups, or blockers
