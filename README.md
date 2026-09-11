# Striker skills

Seven workflow skills for shaping an idea, planning implementation, delivering one green slice at a time, and reviewing and committing changes, plus one for explaining a topic visually.

## Skills

| Skill | Purpose |
| --- | --- |
| `shape-project` | Turn an open project idea into an approved shape. |
| `define` | Resolve intent and decisions; write an approved work contract. |
| `slice` | Decompose a contract and prepare bounded, verifiable slices. |
| `land` | Implement requested work and commit it green. |
| `next-slice` | Implement one prepared slice and checkpoint progress. |
| `code-review` | Review a pinned change against repository standards and an optional approved plan. |
| `commit` | Group changes into semantic commits and create them. |
| `show-me` | Explain the current topic visually with diagrams, code-shape sketches, or an HTML artifact. Manual invocation only. |

## Workflow

| Where you are | Run |
| --- | --- |
| The product intent is still open | `shape-project`, then pass its approved shape to `define` |
| A small change that fits one session | `define`, then `land` |
| A feature needing several increments | `define`, then `slice`, then `next-slice` per prepared slice |
| The next slice is unprepared or implementation exposes a contract blocker | `slice` with the existing plan and checkpoint |
| Work is in and you want it checked | `code-review` |
| A worktree of changes needs to land as commits | `commit` |
| A discussion needs a picture | `show-me` |

`land` and `next-slice` both invoke `code-review` themselves. Run it directly to review a branch, a pull request, or anything since a commit.

`define` replaces `brief` as the common entry point for small and large work. It defines the contract and recommends `land` or `slice`. `slice` alone owns sizing, splitting, ordering, and preparing future work. `next-slice` implements the prepared contract, records findings, and hands blockers back without replanning. Changes to approved intent return to `define`.

Keep planning and implementation in separate sessions by default. The slicer outlines all outcomes but details only ready work, keeping each slice's required knowledge bounded. Run `slice` again when more preparation is needed. Each slice gets acceptance checks, review, and a checkpoint; milestones finish with an integrated check. You can authorize bounded continuation across already-prepared slices.

## Where plans live

Shapes, contracts, and slice plans live outside the repository:

```
${STRIKER_ROOT:-${XDG_STATE_HOME:-$HOME/.local/state}/striker}/
  shapes/<repo>/<slug>-<date>/shape.md
  contracts/<repo>/<slug>-<date>/contract.md
  plans/<repo>/<slug>-<date>/{contract,spine,map,NN-slug,log}.md
```

The plan keeps the full contract separately; its compact spine carries shared constraints and the milestone outline. The map holds navigation, ready slices hold relevant acceptance and execution scope, and the log holds recovery state and evidence. Consumers take explicit paths and check repository identity. Existing briefs remain valid inputs to `land` or `slice`; older plans needing preparation go to `slice`, while executable slices can still run through `next-slice`.

Export `STRIKER_ROOT` from your shell profile rather than per invocation. The planning session and the implementing session are different shells by design, and a root set in one and unset in the other sends the second somewhere else.

## Install with `npx skills`

Install directly from the public [Luckmorecat/skills](https://github.com/Luckmorecat/skills) repository—no local checkout is required.

List the available skills:

```bash
npx skills add Luckmorecat/skills --list
```

Install all eight globally for Codex:

```bash
npx skills add Luckmorecat/skills --global --agent codex --skill '*' --yes
```

Install selected skills by repeating `--skill`:

```bash
npx skills add Luckmorecat/skills --global --agent codex \
  --skill define \
  --skill slice \
  --skill next-slice \
  --yes
```

## Install for Claude Code

Install all eight globally for Claude Code:

```bash
npx skills add Luckmorecat/skills --global --agent claude-code --skill '*' --yes
```

## Portability

One `SKILL.md` serves both runtimes. `disable-model-invocation: true` in its frontmatter keeps Claude Code from auto-loading a skill; `policy.allow_implicit_invocation: false` in `agents/openai.yaml` does the same for Codex. Each host ignores the other's, so there is no per-runtime fork to maintain.

Skill bodies name other skills in plain backticks rather than with a `$` or `/` prefix, because the two hosts spell invocation differently and a body that hardcodes one is wrong on the other.

## Repository layout

Each distributable skill lives under `skills/<name>/`. Supporting references and agent metadata stay in the same skill directory so `npx skills` installs the complete package.
