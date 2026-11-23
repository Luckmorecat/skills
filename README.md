# Striker skills

Fifteen workflow skills for shaping an idea, resolving design decisions, auditing usability, adopting a chosen prototype into the current system, planning implementation, implementing work, delivering one green slice at a time or several in parallel, handing settled work to subagents, reviewing and committing changes, and stripping comments from them, plus one for explaining a topic visually.

## Skills

| Skill | Purpose |
| --- | --- |
| `define` | Explore and grill an idea or feature; resolve consequential decisions. |
| `contract` | Write a work contract from settled conversation or documents. |
| `design` | Resolve a focused technical decision and summarize proposed contract updates. |
| `ux` | Audit an interface through its users' tasks and recommend usability improvements. |
| `adopt` | Adopt a chosen UI or logic prototype by reconciling it with current use cases. |
| `slice` | Break settled context into verifiable vertical slices and dependencies. |
| `wire` | Implement requested work directly with fit-for-purpose proof. |
| `land` | Implement requested work, review it, and commit it green. |
| `weave` | Deliver work settled in the current session through subagents. |
| `stitch` | Deliver work settled in the current session with one lean worker and Codex review. |
| `next-slice` | Implement one prepared slice and checkpoint progress. |
| `run-plan` | Orchestrate a slice plan through subagents, recovering blockers or escalating them. |
| `run-plan-parallel` | Run independent slices of a plan concurrently in isolated worktrees, integrating each onto the target branch. |
| `code-review` | Review a pinned change against repository standards and an optional approved plan. |
| `commit` | Group changes into semantic commits and create them. |
| `no-comments` | Delete comments from a change through an isolated subagent and report refactor targets. Manual invocation only. |
| `show-me` | Explain the current topic visually with diagrams, code-shape sketches, or an HTML artifact. Manual invocation only. |
| `sol-loop` | Review a change with GPT Sol through the Codex CLI, fixing findings in rounds until it approves. |

## Workflow

| Where you are | Run |
| --- | --- |
| An idea or feature needs exploration | `define` |
| Settled context needs a delivery contract | `contract` |
| A small change with a settled scope | `contract`, then `land` |
| Settled work, infra/setups, or quick fixes to run directly without TDD or review ceremony | `wire` |
| A small change settled in the current session, with context to preserve | `weave` |
| A settled change when you want low primary-agent quota and Codex review | `stitch` |
| A defined feature needing several increments | `slice` from settled context or a contract, then `next-slice` per eligible slice |
| A prepared plan should run through completion | `run-plan` for sequential execution through subagents |
| A prepared plan has independent slices worth running at once | `run-plan-parallel` for concurrent execution in worktrees |
| A technical decision needs deeper examination | Optional `design` during or after `define`, before dependent implementation |
| An interface is confusing or needs a usability pass | `ux`, then `land` or `contract` for the settled changes |
| A prototype settled the UI or logic | `adopt`, then `contract`; `adopt` again when implementation raises discrepancies |
| A breakdown needs revision or a slice needs preparation | `slice` with the existing plan and checkpoint |
| Work is in and you want it checked | `code-review` |
| A worktree of changes needs to land as commits | `commit` |
| Comments narrate a change or excuse workarounds | `no-comments`, then `design` or `land` for its open flags |
| A discussion needs a picture | `show-me` |
| A change needs a second model's review before a PR | `sol-loop` |

`land`, `next-slice`, and `weave` run `code-review` themselves or through a subagent. Run it directly to review a branch, a pull request, or anything since a commit.

`wire` is the direct, low-ceremony path for running settled work, infra/setups, or quick requests inline without TDD or review overhead: it verifies assumptions, guards against irreversible or external side effects, proves each scenario with the lightest concrete check, audits the diff, and leaves changes uncommitted. `land` carries the full test-first implementation steps, then runs `code-review` and hands the reviewed tree to `commit`. `weave` workers take those same test-first steps from its `WORKER.md`; each carries its own copy so it installs on its own—change those two together. `weave`'s `RECONCILER.md` likewise carries `adopt`'s mapping and precedence defaults, generalised from a prototype to any source of truth: `silent` stands for `adopt`'s `unshown`, and `added` covers behaviour a source requires that the system lacks. Change the two together.

`define` combines the former `shape` and `define` exploration flows. It works from a vague idea or a concrete feature, using question rounds, scenario checks, and targeted inline or subagent discovery to resolve consequential choices. It finishes with a conversational recap of purpose, scope, scenarios, settled decisions, and remaining uncertainties. The user chooses what happens next.

`contract` turns settled context into a self-contained delivery contract when invoked. It derives acceptance examples from agreed behavior and surfaces missing decisions without repeating the exploration. `slice` alone owns sizing, splitting, ordering, and preparing future work. `next-slice` implements an eligible slice, records findings, and hands planning blockers back without replanning. Newly discovered consequential choices and changes to approved intent can be explored with `define`; agreed changes must be reflected in the plan and any supplied contract before dependent work proceeds.

`design` frames a named technical question, inspects evidence, compares alternatives against explicit criteria, and checks the recommendation against concrete scenarios. It finishes with a conversational summary of settled technical decisions, proposed contract additions or changes, and remaining uncertainties without editing files. Use it when you want deeper design work; `define` still resolves consequential decisions on its own. Missing evidence produces a bounded investigation, and affected slice plans return to `slice` for revision.

`ux` frames the users, their main tasks, and context of use, then checks the scope-relevant discovery tracks—inventorying the interface, walking through each task in the running UI, researching comparable patterns, and checking accessibility—inline when small or through subagents when broad. Findings are tied to a task step, a principle from its `PRINCIPLES.md`, and evidence, and rated by severity. It recommends changes without editing product code. Choices that need to be seen are handed to a separate `prototype` skill, and the returned variants are evaluated against the same tasks.

`adopt` makes a chosen prototype safe to implement as the source of truth for what it settles, whether an interface or logic such as a state model. It pins the reference, maps every use case the current system supports as kept, changed, unshown, dropped, or conflicting, and settles precedence so defaults resolve most gaps. It asks about the rest and records answers in the contract's prototype reference ledger. Per-kind checklists and default precedence live in its `KINDS.md`. Implementation treats the reference as approved behavior: `land`, `next-slice`, and `weave` raise discrepancies with it, and `adopt` settles them in a batch.

`slice` accepts settled conversation, a contract, or an existing plan. It prepares independently verifiable vertical slices with explicit dependencies, preserving the full agreed scope. Slice descriptions focus on outcomes, acceptance, and proof; execution discovers current paths and commands. The plan carries delegated discretion, precedence rules, and any prototype reference, so execution settles what they cover the same way with or without a contract. Missing decisions or evidence block affected slices while independent work continues. `next-slice` implements one eligible slice, verifies and reviews it, then commits and checkpoints progress. You can authorize bounded continuation across eligible slices.

`weave` delivers work whose intent the current session settled, orchestrating subagents while the main thread holds intent and avoids direct product-code edits. It writes a brief of goal, acceptance IDs, scope, settled decisions, and known starting points (amending a supplied contract only where conversation changed it), then routes workers following `WORKER.md` while answering or escalating questions. When sources of truth settle behaviour beyond acceptance, a reconciler following `RECONCILER.md` maps the scope before work starts (or starts read-only from a settled contract ledger), handles discrepancies in batches, and checks results pre-commit. It defaults to one chunk without a planner, splitting only when parallel tracks or scope warrant it; parallel workers leave temporary WIP commits in external worktrees that an integration worker cherry-picks uncommitted and cleans up once green. Direct parallel `code-review` axis reviewers run alongside any reconciler check with triaged delta re-reviews before local `commit`; under autonomy, orchestrator-made choices are tracked as run decisions. A final check verifies commits, status, per-ID evidence, and intent, or reports paused/blocked state when stopped.

`stitch` is the quota-friendly companion to `weave` for settled changes that do not need a planner, parallel worktrees, or source-of-truth reconciliation. The main thread keeps intent and writes a compact brief including already-known starting points (file paths, symbols, and check commands), then dispatches one lean worker following its `WORKER.md`. That worker implements, verifies green, runs an independent read-only review loop through `bin/review` (defaulting to `codex exec` with `gpt-6.2-sol` at `xhigh`, configurable separately via `${XDG_CONFIG_HOME:-$HOME/.config}/stitch/review.json`, `STITCH_REVIEW_*` env vars, or CLI flags, including custom CLI backends) checking both code quality and verbatim brief compliance, fixes accepted findings, and commits its owned paths directly without spawning a separate committer subagent. When `bin/review` reports `fallback_needed` or fallback-only review is requested, the worker reads `FALLBACK.md` and dispatches a single isolated review subagent itself where nested subagents are supported, or stops uncommitted for the orchestrator to run that fallback review and commit.

`run-plan` delegates all substantive work, running one `next-slice` subagent at a time. A reconciler subagent repairs blockers within the agreed plan and escalates plan changes to the user. Independent slices may continue while affected work waits for an answer. When you ask it to run autonomously, the reconciler decides those changes itself except for hard stops such as data loss, security, public contracts, or cost. It records each decision for review, alerts you at once when two or more slices build on one, and ends with a report of decisions made on your behalf.

`run-plan-parallel` follows `run-plan` but runs up to three eligible slices at once, each in its own worktree and branch from the current tip, with its own instances of the resources its verification needs. It requires a clean tree and serializes slices likely to touch the same files or to share a resource that cannot be duplicated. Workers follow `next-slice` but keep their checkpoints in per-slice files, leaving the rest of the plan directory to one subagent at a time. An integrator rebases and re-verifies each committed slice, then fast-forwards the target branch; a slice is complete only once integrated, and an interrupted integration resumes where it stopped. Blockers go through its own reconciler under the same autonomy rules as `run-plan`; gaps no slice owns become new slices.

`no-comments` sends a fresh subagent to delete comments from the named files or the current diff, keeping only license headers, tool directives, public API docs, constraints imposed by code we cannot change, and a few suppressions. A comment excusing a surprise in our own code dies, and its symbol is flagged `MUST KILL` with the reshape that would make it obvious. The skill audits the sweep, restores deletions that meet an exception, fixes trivial flags, and reports the rest for `design` or `land` without refactoring further. Adapted from Comment Sicko in [pstack](https://github.com/cursor/plugins/tree/main/pstack) (MIT, © 2026 Lauren Tan).

`sol-loop` sends the change to GPT Sol through `codex exec` in a read-only sandbox and resumes the same Codex thread for later rounds, keeping a ledger of findings, outcomes, and usage. It answers each finding with the smallest fix or evidence-backed pushback, stops at approval or after three rounds (five for security or data-loss risks), and never pushes unless asked. Adapted from sol-loop in [tstack](https://github.com/t3dotgg/tstack/tree/main/skills/sol-loop) (MIT, © 2026 Theo Browne), with the T3 orchestrator route replaced by the Codex CLI.

## Where plans live

Contracts and slice plans live outside the repository. `define` presents its recap in the conversation. Saved contracts and plans use this storage root:

```
${STRIKER_ROOT:-${XDG_STATE_HOME:-$HOME/.local/state}/striker}/
  contracts/<repo>/<slug>-<date>/contract.md
  plans/<repo>/<slug>-<date>/{plan,NN-slug,log}.md
```

`plan.md` holds shared context and the dependency/status table. Each slice has its own outcome, acceptance, and verification; `log.md` holds recovery state and evidence. `run-plan-parallel` adds `checkpoints/<ID>.md` and `worktrees/<ID>/` beside them while slices are in flight; worktrees move under the storage root when the plan directory is inside the repository. Plans remain self-contained whether their source is conversation or a contract. Existing plans retain their layout and checkpoint history; `next-slice` can still execute prepared slices from the older spine/map format.

Export `STRIKER_ROOT` from your shell profile rather than per invocation. The planning session and the implementing session are different shells by design, and a root set in one and unset in the other sends the second somewhere else.

## Install with `npx skills`

Install directly from the public [Luckmorecat/skills](https://github.com/Luckmorecat/skills) repository—no local checkout is required.

List the available skills:

```bash
npx skills add Luckmorecat/skills --list
```

Install all eighteen globally for Codex:

```bash
npx skills add Luckmorecat/skills --global --agent codex --skill '*' --yes
```

Install selected skills by repeating `--skill`:

```bash
npx skills add Luckmorecat/skills --global --agent codex \
  --skill define \
  --skill contract \
  --skill slice \
  --skill next-slice \
  --yes
```

## Install for Claude Code

Install all eighteen globally for Claude Code:

```bash
npx skills add Luckmorecat/skills --global --agent claude-code --skill '*' --yes
```

## Portability

One `SKILL.md` serves both runtimes. For manually invoked skills, `disable-model-invocation: true` in the frontmatter keeps Claude Code from auto-loading the skill; `policy.allow_implicit_invocation: false` in `agents/openai.yaml` does the same for Codex. Each host ignores the other's, so there is no per-runtime fork to maintain.

Skill bodies name other skills in plain backticks rather than with a `$` or `/` prefix, because the two hosts spell invocation differently and a body that hardcodes one is wrong on the other.

## Repository layout

Each distributable skill lives under `skills/<name>/`. Supporting references and agent metadata stay in the same skill directory so `npx skills` installs the complete package.
