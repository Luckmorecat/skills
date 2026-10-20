# Baseline Weave result

Complete and accepted at `4da728d411cb37ed548c6520b6bc75735fb17c4c` (`feat(configkit): support validated layered configuration`). Fixed point: `a1554a97a974af7fad86abf160a5dc391c8382fe`.

A1–A2: recursive detached merges, deletion, full-input reserved-key validation and root validation are implemented and covered by eight core regressions. A3: seven CLI subprocess regressions cover layered/base-only success and specified failures with status 2, stderr, empty stdout and no traceback. Source was inspected by orchestrator and isolated reviewers.

A4: final committed suite passes all 15 tests (`logs/final-suite.log`); real success/error demonstrations pass (`logs/cli-demonstration.log`). `LOCAL_NOTES.txt` is the sole remaining dirty path, preserving original SHA256 `3cc1f3ffdd22f0f42c6449b2be0fea9b2660da6c2ddc99d705ddb562029d4e26`. Legacy smoke was attempted exactly once, exited 69 because its optional internal driver is unavailable (`logs/legacy-smoke.log`); this is not a successful check. The brief permits unittest/subprocess substitution.

Nine instrumented verification processes: six successful, two expected test-first red runs, one unavailable legacy run. Evidence: `events.jsonl` and `logs/`. Standards: 0 blocking, 0 advisory; Plan compliance: 0 blocking, 0 advisory. No repairs needed.

No answers changed approved behaviour. Settled run decisions: standard library only, preserve dirty notes, substitute unittest/subprocess proof for unavailable legacy runner. No additional run decisions, missing-context incidents, repeated work, unresolved blockers, or kept worktrees. Two dependent workers, isolated reviewers, and committer followed supplied role files.

Self-reported invocation counts (nested tools / functions.exec wrappers / collaboration calls / verification processes):

| Agent | Nested | Exec | Collaboration | Verification |
|---|---:|---:|---:|---:|
| orchestrator | 12 | 9 | 12 | 2 |
| core | 8 | 5 | 0 | 3 |
| cli | 7 | 4 | 0 | 4 |
| standards | 2 | 2 | 0 | 0 |
| compliance | 2 | 2 | 0 | 0 |
| committer | 3 | 3 | 0 | 0 |

Tool invocations count nested tools individually, with wrappers and collaboration separate. Token counts are unavailable. Orchestrator counts include writing these reports.
