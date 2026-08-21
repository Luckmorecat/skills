# Striker skills

Four explicit workflow skills for shaping an idea, planning implementation, and delivering one green slice at a time.

## Skills

| Skill | Purpose |
| --- | --- |
| `shape-project` | Turn an open project idea into an approved intent brief. |
| `settle` | Resolve implementation decisions and write a sliced plan. |
| `brief` | Plan a small task that can land green in one session. |
| `next-slice` | Implement one slice from an approved `settle` plan. |

## Install with `npx skills`

List the skills from this local checkout:

```bash
npx skills add ~/development/striker-skills --list
```

Install all four globally for Codex:

```bash
npx skills add ~/development/striker-skills --global --agent codex --skill '*' --yes
```

Install selected skills by repeating `--skill`:

```bash
npx skills add ~/development/striker-skills --global --agent codex \
  --skill settle \
  --skill next-slice \
  --yes
```

After publishing the repository, replace the local path with its GitHub shorthand or Git URL:

```bash
npx skills add <owner>/striker-skills --global --agent codex --skill '*' --yes
```

## Workflow

Use `$shape-project` when the product intent is still open. Pass its approved brief to `$settle`. Use `$brief` instead for a small, single-session change. Run `$next-slice` against an approved `settle` plan directory.

## Repository layout

Each distributable skill lives under `skills/<name>/`. Supporting references and agent metadata stay in the same skill directory so `npx skills` installs the complete package.

To check discovery after an edit:

```bash
npx skills add . --list
```
