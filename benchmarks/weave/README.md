# Weave context-policy benchmark

This is a small behavioural pilot, not a measured token-efficiency claim. It uses
real delegated coding work where agents are available and provides process and
provider-usage instrumentation for subsequent runs. No model/API dependency is
required for fixture creation or instrument tests.

## Reproduce

From the repository root with Python 3 and Git:

```sh
python benchmarks/weave/bench.py prepare /tmp/weave-baseline-01 --arm baseline
python benchmarks/weave/bench.py prepare /tmp/weave-current-01 --arm current
python -m unittest discover -s benchmarks/weave -p test_bench.py -v
```

Each preparation refuses to overwrite an existing directory. It creates the
same starting source, tests, dirty user note, acceptance contract, and pinned
Weave/review/commit instructions. The baseline is
`a9c46d635e9af7fdc679a757901bc9cf0e071d4a`; current is
`df3ac191f6cbb5f5eb389f6885283b5a956194d3`. This requires both commits in the clone.
The fixture commit has fixed identity and dates. Manifests record the source
fixture hash and leave unavailable token measurements null.

Start two fresh orchestrators with their respective SKILL.md and BRIEF.md paths.
Give them only their own arm. Ask each to use the fixed two-chunk dependency
split, isolated Standards and Plan compliance reviewers, repair when needed,
commit, and verify at the final commit. Use inherited dispatch in the baseline
and fresh dispatch in current. Baseline allowed inheritance; it did not require
it. Therefore this compares two concrete runtime configurations, not all valid
interpretations of the old instructions. Keep both reviews after implementation:
the old policy did not require premature review. This does not isolate the new
review barrier's effect.

Keep model/version, settings, source, acceptance, tools, and budgets fixed.
Record the actual model identifier when the provider exposes it. Run paired
trials with randomized arm order, ideally at least five pairs, before drawing
efficiency conclusions. Never share solutions/reports across arms. Keep the
oracle out of worker prompts. A shared filesystem does not enforce this blind;
use separate containers for stronger isolation.

For every verification process:

```sh
python benchmarks/weave/bench.py run --cwd /tmp/weave-current-01/work \
  --events /tmp/weave-current-01/events.jsonl \
  --log /tmp/weave-current-01/logs/unique-name.log \
  -- python -m unittest discover -s tests -v
```

The wrapper preserves complete combined output externally, records command,
working directory, exit code, duration, byte count and SHA-256, and returns the
process status (signals use shell convention 128 + signal; the event preserves
the raw negative subprocess status). Launch failures record a null process
status and an error, and the wrapper returns 127. Log paths must be unique;
existing logs cannot be overwritten.
Baseline agents may read full logs; current agents follow WORKER.md. Byte counts
are output size, **not** bytes read into model context or token counts.
Use ordinary targeted source/log reads for inspection. The process wrapper is
for verification; it does not restrict inspection tools or excerpt retrieval.
Invoke `python legacy_smoke.py` once through the wrapper. Its intentional status
69 models an unavailable internal verification dependency. The contract permits
equivalent CLI/subprocess tests; agents must distinguish recovery from a pass.

After the orchestrator finishes, independently audit each final worktree:

```sh
python benchmarks/weave/audit.py /tmp/weave-current-01/work -v
```

The oracle covers nested deletion and replacement, aliasing, validation inside
discarded branches and lists, invalid roots, CLI success/error cases, and dirty
snapshot preservation. It is additional acceptance evidence, not a substitute
for independent review. Record natural findings and repairs separately from
any deliberately injected defects. Do not count a clean review as demonstrated
defect-detection sensitivity.

Optional probes operate only on copies of completed arms:

```sh
python benchmarks/weave/bench.py review-probe /tmp/weave-current-01 /tmp/weave-review-01
python benchmarks/weave/bench.py recovery-probe /tmp/weave-current-01 /tmp/weave-recovery-01
```

For review, dispatch an isolated Plan compliance reviewer against the copied
worktree, its BRIEF.md, evidence.md, original fixture fixed point, and existing
dirty-note exclusion. Ask for findings and minimal verification without naming
the seeded defect. The mutation changes the CLI input-error status from 2 to 0
and refuses unsupported implementation shapes. Preserve this as a separate
probe; never change or relabel the accepted main trial.

For recovery, dispatch a fresh core worker with the copied worktree, BRIEF.md,
handoff.md, and original WORKER.md. Keep orchestrator-update.txt out of its
handoff. When it returns its question, deliver that update and resume it. This
deliberately omits a required decision and tests safe pause/resume; it violates
Weave's required complete handoff and is **not** a naturally observed regression.
Record clarification turns, verification calls, changes and unresolved blockers.
Do not attribute all re-verification cost to the omission without a matched
complete-handoff recovery control.

## Measurement contract

Persist `outcome.json` and `report.md` per arm with acceptance-ID evidence,
completion/commit status, blockers, review findings, repeated work, missing-context
incidents, and per-agent tool-call counts. Separate wrapper-observed process
calls from agent-reported tool calls and functions.exec envelopes; do not add
envelopes to nested tool counts. Include orchestration, workers, reviewers,
repairs and committers in provider usage, even failed or abandoned agents.

Normalize provider traces to one JSONL row **per completed request**:

```json
{"run_id":"current-01","agent_id":"worker-core","request_id":"provider-id","input_tokens":1234,"cached_input_tokens":1000,"output_tokens":120}
```

Here input_tokens includes cached input, and cached_input_tokens is a subset.
Normalize providers whose counters separate cache reads/writes before import;
do not sum cumulative snapshots or both parent totals and child request totals.
Keep cache-write tokens and costs separately in the raw trace when exposed.
The numbers above are an illustrative schema, not measurements.

```sh
python benchmarks/weave/bench.py usage /path/to/one-run-normalized-usage.jsonl
```

The importer rejects mixed runs, duplicate (run, agent, request) IDs and invalid counts.
Use one input file per run. Empty input reports unknown tokens, never zero.
Keep provider originals, normalization code/version, model ID, settings, and
tool traces externally. Only provider counters establish actual input/output
usage. Tool counts, context window size, characters, source-file length, and
tokenizer estimates do not establish billed usage or savings.

## Interpretation

Check acceptance, review findings, repair success, dirty-file safety and recovery
before comparing paired token totals, cache behaviour, calls and time. Treat
omitted handoff facts, unavailable evidence, rediscovery and repeated checks as
costs, not just smaller prompts. State when a probe is seeded or deterministic.
Do not generalize this small standard-library fixture to UI, migrations,
parallel integration, large repositories, or long-running agent recovery.
