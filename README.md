# Striker skills

Nine workflow skills for shaping an idea, resolving design decisions, planning implementation, delivering one green slice at a time, and reviewing and committing changes, plus one for explaining a topic visually.

## Skills

| Skill | Purpose |
| --- | --- |
| `define` | Explore and grill an idea or feature; resolve consequential decisions. |
| `contract` | Write a work contract from settled conversation or documents. |
| `design` | Resolve a focused technical decision and amend the work contract. |
| `slice` | Break settled context into verifiable vertical slices and dependencies. |
| `land` | Implement requested work and commit it green. |
| `next-slice` | Implement one prepared slice and checkpoint progress. |
| `run-plan` | Orchestrate a slice plan through subagents, recovering blockers or escalating them. |
| `code-review` | Review a pinned change against repository standards and an optional approved plan. |
| `commit` | Group changes into semantic commits and create them. |
| `show-me` | Explain the current topic visually with diagrams, code-shape sketches, or an HTML artifact. Manual invocation only. |

## Workflow

| Where you are | Run |
| --- | --- |
| An idea or feature needs exploration | `define` |
| Settled context needs a delivery contract | `contract` |
| A small change with a settled scope | `contract`, then `land` |
| A defined feature needing several increments | `slice` from settled context or a contract, then `next-slice` per eligible slice |
| A prepared plan should run through completion | `run-plan` for sequential execution through subagents |
| A technical decision needs deeper examination | Optional `design` during or after `define`, before dependent implementation |
| A breakdown needs revision or a slice needs preparation | `slice` with the existing plan and checkpoint |
| Work is in and you want it checked | `code-review` |
| A worktree of changes needs to land as commits | `commit` |
| A discussion needs a picture | `show-me` |

`land` and `next-slice` both invoke `code-review` themselves. Run it directly to review a branch, a pull request, or anything since a commit.

`define` combines the former `shape` and `define` exploration flows. It works from a vague idea or a concrete feature, using question rounds, scenario checks, and subagent discovery to resolve consequential choices. It finishes with a brief conversational recap of settled decisions and remaining uncertainties. The user chooses what happens next.

`contract` turns settled context into a self-contained delivery contract when invoked. It derives acceptance examples from agreed behavior and surfaces missing decisions without repeating the exploration. `slice` alone owns sizing, splitting, ordering, and preparing future work. `next-slice` implements an eligible slice, records findings, and hands planning blockers back without replanning. Newly discovered consequential choices and changes to approved intent can be explored with `define`; agreed changes must be reflected in the plan and any supplied contract before dependent work proceeds.

`design` frames a named technical question, inspects evidence, compares alternatives against explicit criteria, and checks the recommendation against concrete scenarios. It folds agreed decisions into the existing contract. Use it when you want deeper design work; `define` still resolves consequential decisions on its own. Missing evidence produces a bounded investigation, and affected slice plans return to `slice` for revision.

`slice` accepts settled conversation, a contract, or an existing plan. It prepares independently verifiable vertical slices with explicit dependencies, preserving the full agreed scope. Slice descriptions focus on outcomes, acceptance, and proof; execution discovers current paths and commands. Missing decisions or evidence block affected slices while independent work continues. `next-slice` implements one eligible slice, verifies and reviews it, then commits and checkpoints progress. You can authorize bounded continuation across eligible slices.

`run-plan` delegates all substantive work, running one `next-slice` subagent at a time. A reconciler subagent repairs blockers within the agreed plan and escalates plan changes to the user. Independent slices may continue while affected work waits for an answer.

## Where plans live

Contracts and slice plans live outside the repository. `define` presents its recap in the conversation. Saved contracts and plans use this storage root:

```
${STRIKER_ROOT:-${XDG_STATE_HOME:-$HOME/.local/state}/striker}/
  contracts/<repo>/<slug>-<date>/contract.md
  plans/<repo>/<slug>-<date>/{plan,NN-slug,log}.md
```

`plan.md` holds shared context and the dependency/status table. Each slice has its own outcome, acceptance, and verification; `log.md` holds recovery state and evidence. Plans remain self-contained whether their source is conversation or a contract. Existing plans retain their layout and checkpoint history; `next-slice` can still execute prepared slices from the older spine/map format.

Export `STRIKER_ROOT` from your shell profile rather than per invocation. The planning session and the implementing session are different shells by design, and a root set in one and unset in the other sends the second somewhere else.

## Install with `npx skills`

Install directly from the public [Luckmorecat/skills](https://github.com/Luckmorecat/skills) repository—no local checkout is required.

List the available skills:

```bash
npx skills add Luckmorecat/skills --list
```

Install all ten globally for Codex:

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

Install all ten globally for Claude Code:

```bash
npx skills add Luckmorecat/skills --global --agent claude-code --skill '*' --yes
```

## Portability

One `SKILL.md` serves both runtimes. For manually invoked skills, `disable-model-invocation: true` in the frontmatter keeps Claude Code from auto-loading the skill; `policy.allow_implicit_invocation: false` in `agents/openai.yaml` does the same for Codex. Each host ignores the other's, so there is no per-runtime fork to maintain.

Skill bodies name other skills in plain backticks rather than with a `$` or `/` prefix, because the two hosts spell invocation differently and a body that hardcodes one is wrong on the other.

## Repository layout

Each distributable skill lives under `skills/<name>/`. Supporting references and agent metadata stay in the same skill directory so `npx skills` installs the complete package.
