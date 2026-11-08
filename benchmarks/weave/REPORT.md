# Weave context-policy evaluation — 21 October 2026

**Recommendation: retain the revised instructions provisionally.** The pilot
found no completion regression, both policies detected a seeded review defect,
and a fresh worker recovered safely from a missing decision. It did **not**
establish reduced context consumption. Actual provider token usage and request
counts are unavailable in this runtime. The current arm used more tool calls in
this one pair; no efficiency improvement is claimed.

## Compared instructions and work

The baseline is [a9c46d6](https://github.com/Luckmorecat/skills/commit/a9c46d635e9af7fdc679a757901bc9cf0e071d4a),
the exact parent of [df3ac191](https://github.com/Luckmorecat/skills/commit/df3ac191f6cbb5f5eb389f6885283b5a956194d3).
The latter adds fresh dispatch without inherited history where supported,
review after final worker reports, and targeted worker reads with full output
stored in external logs. Acceptance, run decisions and role handoffs remain.
The commit's approximately 5.4 million input tokens across 47 calls describes
one earlier run; it supplies neither a paired baseline nor a measured saving.

Two fresh orchestrators ran concurrently in ChatGPT Work. Each used the pinned
Weave and sibling review/commit instructions, two dependent implementation
workers, two isolated review axes, a committer, and a final check. Baseline
children inherited their orchestrator context; current children used
`fork_turns=none`. Children inherited the runtime's default model. Its concrete
provider identifier, settings, per-request usage and full agent traces were not
exposed. No standalone Codex/Claude CLI was installed.

Both arms began at fixture commit `a1554a97a974af7fad86abf160a5dc391c8382fe`,
with identical code and contract, plus the same protected dirty user note.
The work implements a small Python configuration library and CLI:

- A1: recursive merge, replacement, null deletion, detached results, no mutation.
- A2: complete-input reserved-key validation, including discarded branches/lists.
- A3: JSON CLI success and controlled status-2 errors, retaining base-only use.
- A4: tests, real subprocess demonstrations, correct failure reporting and note preservation.

The fixed split and equal acceptance avoid different planning scope. Authors
wrote their own tests; a separate shared oracle independently checks the same
six test methods and their subcases on both final trees. This is representative
of bounded library/CLI maintenance, not a large application benchmark.

## Normal-run measurements

Numbers below exclude setup, infrastructure development/review, independent
oracle runs, and the separately labeled seeded probes.

| Measure | Baseline | Current |
|---|---:|---:|
| Actual input/output tokens | unavailable | unavailable |
| Provider request count | unavailable | unavailable |
| Nested tool calls, agent-reported | 34 | 46 |
| Collaboration calls, agent-reported | 12 | 21 |
| `functions.exec` envelopes, separately reported | 25 | 33 |
| Instrumented processes, observed | 9 | 13 |
| Verification processes | 9 | 11 |
| Inspection-only instrumented processes | 0 | 2 |
| Expected test-first failing processes | 2 | 2 |
| Unavailable legacy smoke attempts (status 69) | 1 | 1 |
| Final author-written suite | 15 passed | 16 passed |
| Shared independent audit | 6 passed | 6 passed |
| Natural review findings / repair rounds | 0 / 0 | 0 / 0 |
| Task completion and protected note preservation | passed | passed |

Fixture result commits are `4da728d411cb37ed548c6520b6bc75735fb17c4c`
and `dc586c7ebd1fd09946e26bd2ba4cb24697796a79`. These belong to the
temporary fixture repositories; their complete implementation/test patches are
archived, rather than advertised as commits in Luckmorecat/skills.

The wrapper recorded 31,275 output bytes for baseline and 58,238 for current.
Current's latter total includes 26,370 bytes from two source-inspection commands;
verification-only output was 31,868 bytes. Output bytes are **not** bytes read
into context, tokens or billed usage. Recorded subprocess durations sum to
1.8244 and 1.9714 seconds; these exclude agent reasoning and are **not** whole-run
latency. Tool counts are role reports, not independently captured provider
traces. Envelopes must not be added again to the nested tool counts.

The current Plan reviewer asked whether direct source/log inspection was allowed
after the wrapper returned summaries. Its orchestrator clarified that it was.
This was one real clarification round, not missing product requirements or a
code defect. Instrumentation wording contributed, so it cannot establish a
policy regression. The reusable protocol now explicitly allows direct targeted
inspection. Current also ran an extra constraints check and a reviewer source
capture. Neither arm reported natural task-context loss or implementation rework.

## Review and recovery probes

**Seeded review sensitivity, one per arm.** Copies of the completed trees had
the same defect inserted: CLI input errors returned status 0 rather than 2.
Reviewers received the contract and an explicit warning that prior verification
predated the working tree, without being told the defect. Both isolated Plan
reviewers reported the blocking defect. Baseline used one targeted subprocess
test with two failing subcases; current reran its complete suite, with thirteen
failing subcases. Each used one verification process. This demonstrates detection
of one concrete defect, not broad review-quality equivalence. No seeded change
was applied to the accepted main trials.

**Seeded fresh-worker recovery, current instructions.** A copied core-worker
handoff referenced reserved-key decision D1 but omitted its contents and had no
recoverable prior verification evidence. The worker inspected the code, refused
to treat implementation as approval, and returned a focused question. After the
orchestrator supplied D1, it updated its brief, passed six independent baseline
tests and all nine core tests, and changed no implementation. One clarification
round and two verification processes were recorded; the worker reported seven
nested tool calls, seven envelopes, and one collaboration call. A3/A4 were
correctly left to their owner.

The missing decision deliberately violated Weave's required complete handoff.
It demonstrates safe pause/resume and a concrete additional clarification cost,
not an observed regression caused by fresh dispatch. With no complete-handoff
recovery control, the cost of rerunning verification cannot be attributed solely
to D1's omission. Source and report reconstruction were real work; no token cost
can be attached to them here.

## Improvements and validation

The PR adds reusable fixtures, paired-run instructions, independent acceptance
checks, safe seeded-probe generators, exit-preserving external logs, and a
provider-usage importer. Missing token counters stay null. The importer rejects
duplicate requests, mixed runs and invalid counts, and separates cached input
as a subset rather than double-counting it.

Independent infrastructure review found an incomplete replacement oracle,
mixed-run token aggregation, signal-status handling, and an overly broad probe
mutation. These were fixed with targeted tests. All eight infrastructure tests
pass, including a deliberately faulty merge rejected by the oracle, command
launch failure, signal handling, and supported/unsupported mutation shapes.
The original buggy fixture also failed the audit as expected. These deterministic
checks validate instrumentation and test sensitivity; they are not model
efficiency measurements.

Weave's operational instructions are unchanged: this pilot does not justify
relaxing acceptance or adding speculative restrictions. The generic skill
validator rejects the existing `disable-model-invocation` portability field in
Weave's frontmatter; that pre-existing field is unchanged and unrelated to this
benchmark. `git diff --check` passes.

## Limits and retention decision

This is one paired run on one small fixture. Concurrent execution, nondeterminism,
different generated tests and unpinned model settings prevent causal attribution
of call-count differences. Both reviews began after worker reports, so the
review barrier's independent effect was not measured. Baseline inheritance is
one allowed old-policy configuration, not a requirement of the old text. The
shared filesystem was guarded by instructions, not sandbox isolation; complete
agent traces were unavailable to independently audit every read.

No UI, migration, parallel integration, large dependency graph, long history or
real runtime crash was exercised. The optional smoke dependency was intentionally
unavailable. Seeded faults are explicitly distinct from natural outcomes. No
statistical confidence interval, savings percentage, or billed-cost comparison
is warranted.

Retain the revised policy as a reasonable default because bounded acceptance,
review and recovery held here; do not describe it as proven cheaper. The next
decision-quality experiment needs token-enabled traces across all roles,
at least five randomized pairs with a pinned model, larger multi-module/UI work,
and matched complete/missing-handoff recovery trials. Revert or adjust specific
measures if such runs show acceptance loss or rediscovery costs exceeding their
context savings.

See [reproduction and measurement protocol](README.md) and
[archived pilot evidence](results/2026-10-21/summary.json).
Within the evidence archive, `/tmp/weave-ab-<arm>/logs/NAME` references map to
`<arm>/logs/NAME`; probe paths similarly map to their named probe directories.
Absolute paths are retained in raw records for fidelity, not as live links.
