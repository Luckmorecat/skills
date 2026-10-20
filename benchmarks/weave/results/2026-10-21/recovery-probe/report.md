# Core recovery report

Worktree: `/tmp/weave-recovery/work`; branch: `master`.
Owned paths: `configkit/core.py`, `tests/test_core.py`; acceptance A1/A2.

Outcome: A1 and A2 are demonstrated. Existing implementation and tests needed no edits. No commits or unrelated repository edits were made. `LOCAL_NOTES.txt` was left untouched; status before and after showed only that supplied dirty path.

## Clarification round

The supplied brief and handoff referred to D1 without providing its policy. Source inspection showed reserved-key behavior but was not treated as approval. Returned that missing-context question to the orchestrator before continuing dependent verification. The orchestrator explicitly supplied D1: reject string dictionary keys beginning `__` anywhere in either complete input, including dictionaries in lists and branches replaced or deleted by override; raise ValueError. Appended that update to `/tmp/weave-recovery/BRIEF.md` as instructed. This resolves the question; no ambiguity remains in assigned acceptance.

## Verification and acceptance

Inspected both owned files directly. `_merge` deep-copies unchanged base structures and replacement values, recurses into dictionary overrides, and removes null-valued override keys. Both complete inputs are validated before merging. No dependencies or network are needed (standard library only), so no bootstrap installation was required.

Before any edits, ran the six tests independent of D1: scalar/recursive replacements, nested and absent deletions, detached mutable structures, unchanged inputs, and invalid roots. All six passed. Evidence: `/tmp/weave-recovery/logs/core_recovery_baseline.log`.

After D1 clarification, ran the complete assigned core suite with `python -m unittest tests.test_core`: all nine tests passed. Evidence: `/tmp/weave-recovery/logs/core_recovery_full.log`.

- A1: demonstrated by recursive replacement, deletion, detachment, and mutation regression tests in the full core log.
- A2: demonstrated by invalid-root tests and tests covering reserved keys in both inputs, dictionaries inside lists, replaced/deleted branches, and allowed ordinary keys in the full core log.
- A3: outside core ownership; not verified here. CLI worker must inspect and prove it.
- A4: core regression portion passes; complete combined suite and real CLI demonstrations remain assigned to the CLI worker. No claim that the unavailable legacy smoke runner passed.

Verification commands used the requested benchmark wrapper; process events are in `/tmp/weave-recovery/events.jsonl`. No failed checks or blockers remain for A1/A2. A3/A4 remain work for their owner.

## Recovery overhead and counters

Repeated work: directly inspected the existing implementation/tests and reran six baseline checks plus the nine-test core suite because the prior worker was unavailable and its green report lacked recoverable verification evidence. Extra work: one missing-context clarification round and brief update. No new implementation or tests were necessary, and no test-first edit cycle was needed.

Counts for this worker turn, including writing this report: 7 `functions.exec` envelopes, 7 nested tool calls (all `exec_command`), and 1 collaboration call (`send_message`). Token counters unavailable.

Commit-message notes: no new repository changes from this recovery; retain the prior implementation's rationale that full-input validation prevents overwritten/deleted branches from hiding reserved keys.
