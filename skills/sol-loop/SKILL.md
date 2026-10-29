---
name: sol-loop
description: Use when the user says "sol loop".
---

# sol-loop

This is a workflow for making your code changes more correct before (or
sometimes after) filing a pull request. tl;dr - use OpenAI's GPT Sol to review
your code in a loop.

Make the most minimal possible changes to appease the Sol reviewers. Be careful
of scope creep and don't be scared to push back.

## Budget

- Default: 3 rounds total. Round 1 is full. Later rounds check only
  changed code and open findings.
- Extend to 5 only for security, permissions, auth, data loss, or
  state/concurrency, while a blocker or should stays open with evidence. Or when
  the user asks.
- Stop early if a round returns only nits. Declined nits and comment,
  doc, or format-only fixes need no new round.
- One reviewer only. Sol must not start subagents or reviewers.
- Keep a ledger: id, severity, outcome, usage if returned. Never guess it.

## 1. Scope

Run `git status --short`. Do not stash, discard, or include unrelated
changes. Limit review to the change paths if they separate cleanly.
Otherwise stop and ask.

Find the base after `git fetch origin`:

- PR: `gh pr view <n> --json baseRefName,headRefOid`. Check out the branch
  only if clean. Confirm `HEAD` is the PR head, or ahead only by this
  change. Base: `git merge-base HEAD origin/<baseRefName>`.
- Local: `git merge-base HEAD origin/<default-branch>`. No remote: a base
  the user names, or `HEAD` for uncommitted changes only.

The change is base to working tree in those paths, with untracked files.
Use one diff command all rounds. State intent and out-of-scope in 1-2
sentences. Run covering checks. Do not send code this change breaks. Note
missing or pre-failing checks in the brief.

## 2. Start Sol

Sol runs through the Codex CLI. Model: `gpt-6.1-sol`, or the version the
user names. Effort: `high`, or the one the user names. Both are passed
explicitly, so record them. Make one scratch directory outside the repo
(`mktemp -d`) and keep every round's output there.

Round 1 starts a read-only thread:

```bash
codex exec -C <repo abs path> -m <model> -c model_reasoning_effort=<effort> \
  -s read-only --json -o <scratch>/r1.md "<round 1 brief>" \
  < /dev/null > <scratch>/r1.jsonl
```

Read the findings from `r1.md`, the thread ID from the `thread.started`
event's `thread_id`, and usage from the `turn.completed` event's `usage`.
Keep the thread ID for later rounds. If `codex` is missing, not logged in,
or does not list the model, report the blocker. Do not substitute a model.

Run each round in the background and wait for it to exit. Do not edit
scoped files while review runs. Do not poll or start a second reviewer. A
non-zero exit, an empty output file, or a reply without a `VERDICT:` line
is a failure, not approval. On failure, restart the round with the ledger.

Round 1 brief (Sol gets no history):

```
Review only. Do not edit, commit, push, comment on PRs, or start subagents.
Repo: <abs path> Base: <sha> Intent: <intent> Out of scope: <scope> Checks: <results>
See: git diff <base> [-- <paths>]; git status --short (read untracked).
Read surrounding code. Find bugs, broken callers, mismatch with intent.
Skip style unless it hides a bug. Hold to the smallest change. Flag code,
tests, or guards the intent does not need. Other paths, rare cases, small
perf, extra compat: nits.
blocker = intended case wrong. should = real bug callers will hit, in intent. nit = rest.
Reply:
VERDICT: APPROVE or CHANGES
S1 [blocker|should|nit] <file>:<line> <claim>. Fix: <suggestion> (stable ids)
```

## 3. Answer findings

Check each finding and severity yourself. Another path, rare case, or
small cost is a nit, whatever label it came with.

- Agree: smallest fix. Prefer delete or narrow over new lock, cache,
  helper, or option. Fix the case that happened. Add one focused test
  that fails without the fix, if intent needs it.
- Disagree: say why, with evidence (file:line, test, output).
- Out of scope or nit: decline in one line. List as follow-up.

Update the ledger. Re-run checks and `git diff --shortstat <base>`. If
review grew the diff, cut first. Do not agree just to end the loop.

## 4. Next round

Start one only if budget remains and a blocker or should is open, behavior code
changed, or approval does not cover the current behavior diff. Resume the
saved thread, which already holds the round 1 brief:

```bash
codex exec resume <thread_id> -m <model> -c model_reasoning_effort=<effort> \
  -c sandbox_mode='"read-only"' --json -o <scratch>/r<N>.md "<round N message>" \
  < /dev/null > <scratch>/r<N>.jsonl
```

Send the ledger (`fixed:` / `disagree:` / `declined:` + evidence), the same
base diff, and the change since last round. Tell Sol: open ids and changed
code only. Mark each old id `resolved` or `still open: <reason>`.

If resume fails, start a fresh thread with the round 1 command, sending the
round 1 brief with this message appended. Keep the new thread ID.

## 5. Stop and ship

Agreed: APPROVE on the current behavior diff, no blocker or should open,
no concern of your own. Stuck: an item stays disputed after two replies,
or budget ends. Show both sides in 2-3 lines each. The user decides.
Budget end is not approval.

Do not push during the loop. Push after agreement only if the user asked
to push, ship, or update the PR. If you push to a PR, add above the model
blurb:

`Reviewed with sol-loop: <N> rounds with <model>. Sol verdict: approved`.

Add `on <effort>` only if verified.

Report: rounds, model, what Sol changed, diff size before/after, fixed and
declined findings with reasons, usage if exposed (else say not), pushed or not.
