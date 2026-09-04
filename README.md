# Striker skills

Seven workflow skills for shaping an idea, planning implementation, delivering one green slice at a time, and reviewing and committing changes.

## Skills

| Skill | Purpose |
| --- | --- |
| `shape-project` | Turn an open project idea into an approved intent brief. |
| `settle` | Resolve implementation decisions and write a sliced plan. |
| `brief` | Plan a small task that can land green in one session. |
| `land` | Implement an approved plan or brief and commit it green. |
| `next-slice` | Implement one slice from an approved `settle` plan. |
| `code-review` | Review a pinned change against repository standards and an optional approved plan. |
| `commit` | Group changes into semantic commits and create them. |

## Workflow

| Where you are | Run |
| --- | --- |
| The product intent is still open | `shape-project`, then pass its approved brief to `settle` |
| A feature spanning more than one session | `settle`, then `next-slice` once per slice |
| A small change that fits one session | `brief`, then `land` |
| Work is in and you want it checked | `code-review` |
| A worktree of changes needs to land as commits | `commit` |

`land` and `next-slice` both invoke `code-review` themselves. Run it directly to review a branch, a pull request, or anything since a commit.

Each planning skill hands the next one an approved document, so `settle` never re-asks what `shape-project` settled and the implementing session never re-asks what planning settled.

## Where plans live

Shapes, plans, and briefs are written outside the repository, which puts a commit of them out of reach rather than merely against the rules:

```
${STRIKER_ROOT:-${XDG_STATE_HOME:-$HOME/.local/state}/striker}/
  shapes/<repo>/<slug>-<date>/shape.md
  plans/<repo>/<slug>-<date>/{spine,map,NN-slug,log}.md
  briefs/<repo>/<slug>-<date>/brief.md
```

They are durable, not scratch: a plan outlives the session that wrote it. A skill that consumes one takes the path it was handed, so nothing hunts for the newest directory.

Export `STRIKER_ROOT` from your shell profile rather than per invocation. The planning session and the implementing session are different shells by design, and a root set in one and unset in the other sends the second somewhere else.

## Install with `npx skills`

Install directly from the public [Luckmorecat/skills](https://github.com/Luckmorecat/skills) repository—no local checkout is required.

List the available skills:

```bash
npx skills add Luckmorecat/skills --list
```

Install all seven globally for Codex:

```bash
npx skills add Luckmorecat/skills --global --agent codex --skill '*' --yes
```

Install selected skills by repeating `--skill`:

```bash
npx skills add Luckmorecat/skills --global --agent codex \
  --skill settle \
  --skill next-slice \
  --yes
```

## Install for Claude Code

Install all seven globally for Claude Code:

```bash
npx skills add Luckmorecat/skills --global --agent claude-code --skill '*' --yes
```

## Portability

One `SKILL.md` serves both runtimes. `disable-model-invocation: true` in its frontmatter keeps Claude Code from auto-loading a skill; `policy.allow_implicit_invocation: false` in `agents/openai.yaml` does the same for Codex. Each host ignores the other's, so there is no per-runtime fork to maintain.

Skill bodies name other skills in plain backticks rather than with a `$` or `/` prefix, because the two hosts spell invocation differently and a body that hardcodes one is wrong on the other.

## Repository layout

Each distributable skill lives under `skills/<name>/`. Supporting references and agent metadata stay in the same skill directory so `npx skills` installs the complete package.
