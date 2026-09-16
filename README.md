# Striker skills

Eight workflow skills for shaping an idea, resolving design decisions, planning implementation, delivering one green slice at a time, and reviewing and committing changes, plus one for explaining a topic visually.

## Skills

| Skill | Purpose |
| --- | --- |
| `define` | Explore and grill an idea or feature; resolve consequential decisions. |
| `contract` | Write a work contract from settled conversation or documents. |
| `design` | Resolve a focused technical decision and amend the work contract. |
| `slice` | Decompose a contract and prepare bounded, verifiable slices. |
| `land` | Implement requested work and commit it green. |
| `next-slice` | Implement one prepared slice and checkpoint progress. |
| `code-review` | Review a pinned change against repository standards and an optional approved plan. |
| `commit` | Group changes into semantic commits and create them. |
| `show-me` | Explain the current topic visually with diagrams, code-shape sketches, or an HTML artifact. Manual invocation only. |

## Workflow

| Where you are | Run |
| --- | --- |
| An idea or feature needs exploration | `define` |
| Settled context needs a delivery contract | `contract` |
| A small change with a settled scope | `contract`, then `land` |
| A defined feature needing several increments | `contract`, then `slice`, then `next-slice` per prepared slice |
| A technical decision needs deeper examination | Optional `design` during or after `define`, before dependent implementation |
| The next slice is deferred or implementation exposes a contract blocker | `slice` with the existing plan and checkpoint |
| Work is in and you want it checked | `code-review` |
| A worktree of changes needs to land as commits | `commit` |
| A discussion needs a picture | `show-me` |

`land` and `next-slice` both invoke `code-review` themselves. Run it directly to review a branch, a pull request, or anything since a commit.

`define` combines the former `shape` and `define` exploration flows. It works from a vague idea or a concrete feature, using question rounds, scenario checks, and subagent discovery to resolve consequential choices. It finishes with a brief conversational recap of settled decisions and remaining uncertainties. The user chooses what happens next.

`contract` turns settled context into a self-contained delivery contract when invoked. It derives acceptance examples from agreed behavior and surfaces missing decisions without repeating the exploration. `slice` alone owns sizing, splitting, ordering, and preparing future work. `next-slice` implements the prepared contract, records findings, and hands blockers back without replanning. Newly discovered consequential choices and changes to approved intent can be explored with `define`; agreed changes must be reflected in the contract before dependent work proceeds.

`design` frames a named technical question, inspects evidence, compares alternatives against explicit criteria, and checks the recommendation against concrete scenarios. It folds agreed decisions into the existing contract. Use it when you want deeper design work; `define` still resolves consequential decisions on its own. Missing evidence produces a bounded investigation, and affected slice plans return to `slice` for revision.

Keep planning and implementation in separate sessions by default. The slicer outlines all outcomes and prepares every slice it can write from current evidence; it defers only slices that wait on an unresolved unknown, naming the experiment that unblocks them. Run `slice` again once that evidence lands. Each slice gets acceptance checks, review, and a checkpoint; milestones finish with an integrated check. You can authorize bounded continuation across already-prepared slices.

## Where plans live

Contracts and slice plans live outside the repository. `define` presents its recap in the conversation. Saved contracts and plans use this storage root:

```
${STRIKER_ROOT:-${XDG_STATE_HOME:-$HOME/.local/state}/striker}/
  contracts/<repo>/<slug>-<date>/contract.md
  plans/<repo>/<slug>-<date>/{contract,spine,map,NN-slug,log}.md
```

The plan keeps the full contract separately; its compact spine carries shared constraints and the milestone outline. The map holds navigation, ready slices hold relevant acceptance and execution scope, and the log holds recovery state and evidence. Consumers take explicit paths and check repository identity where applicable. Existing briefs remain valid inputs to `land` or `slice`; older plans needing preparation go to `slice`, while executable slices can still run through `next-slice`.

Export `STRIKER_ROOT` from your shell profile rather than per invocation. The planning session and the implementing session are different shells by design, and a root set in one and unset in the other sends the second somewhere else.

## Install with `npx skills`

Install directly from the public [Luckmorecat/skills](https://github.com/Luckmorecat/skills) repository—no local checkout is required.

List the available skills:

```bash
npx skills add Luckmorecat/skills --list
```

Install all nine globally for Codex:

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

Install all nine globally for Claude Code:

```bash
npx skills add Luckmorecat/skills --global --agent claude-code --skill '*' --yes
```

## Portability

One `SKILL.md` serves both runtimes. For manually invoked skills, `disable-model-invocation: true` in the frontmatter keeps Claude Code from auto-loading the skill; `policy.allow_implicit_invocation: false` in `agents/openai.yaml` does the same for Codex. Each host ignores the other's, so there is no per-runtime fork to maintain.

Skill bodies name other skills in plain backticks rather than with a `$` or `/` prefix, because the two hosts spell invocation differently and a body that hardcodes one is wrong on the other.

## Repository layout

Each distributable skill lives under `skills/<name>/`. Supporting references and agent metadata stay in the same skill directory so `npx skills` installs the complete package.
