# Plan format

The directory [`settle`](SKILL.md) writes on approval. The next session opens it with no memory of the interview, so the directory carries the whole result.

Create it outside the repository, which puts a commit of the plan out of reach rather than merely against the rules. Override the root with `STRIKER_ROOT`:

```bash
striker_root="${STRIKER_ROOT:-${XDG_STATE_HOME:-$HOME/.local/state}/striker}"
if repo_root=$(git rev-parse --show-toplevel 2>/dev/null); then
  repo=$(basename "$repo_root")
else
  repo=$(basename "$PWD")
fi
slug="oauth-device-flow"   # replace with a short kebab-case summary
mkdir -p "$striker_root/plans/$repo"
mkdir "$striker_root/plans/$repo/$slug-$(date +%F)"
```

The leaf is created without `-p` so an existing directory stops you rather than being written over: choose a more specific slug and retry.

Take the date from `date +%F`. Write a directory every time, including for single-slice work: `log.md` needs a home either way, and one shape means the implementing session never branches on the layout it finds.

```
<striker-root>/plans/<repo>/<slug>-2026-08-21/
  spine.md
  map.md
  01-<slug>.md
  02-<slug>.md
  log.md
```

## spine.md

Every session reads this. Keep it short enough that this stays true.

- **Goal** — what the work delivers, in a few lines, and the request or approved shape it came from. Write the intent out here rather than citing a path: the directory carries the whole result.
- **Evidence state** — established, sparse, or blank, with the inspected scope.
- **Product contract** — the actor or caller, the acceptance examples, and the hard constraints an approved shape settled. Write `None` when no shape exists.
- **User decisions** — each answer from the interview, with the reasoning that produced it.
- **Code-backed ledger** — every `A<n>` assumption, each citing the `file:line` it came from. Write `None` when the project is blank.
- **Defaults** — every `D<n>` no-precedent choice, with its reason and reversal cost. Write `None` when unused.
- **Out of scope** — what was considered and excluded, so no session reopens it.
- **Use-case tree** — the full depth, with the emitted slices marked. A later session emits an unmarked node's children from this, with no second analysis.

## map.md

Orientation for the whole task, so each session skips the search the interview already did.

- **Existing traversal** — how the inspected flow connects, in order: route, hook, service, api. Write `None` for a blank project.
- **Planned traversal** — paths a blank or sparse project intends to create. Mark these as unverified until an implementing slice creates and checks them.
- **Shared paths** — the files more than one slice touches, one line each on why they matter.
- **Ruled out** — the paths the interview eliminated, and what sent it there. Nothing in the code says "the answer is not here", which makes this the most valuable section.

`map.md` saves **search, not reading**. Existing paths say where to look, and planned paths say what must be created and verified. Never report a planned path as existing code.

## NN-\<slug\>.md

One slice. A session opens this file and needs no other slice file to start.

- **Build** — the change, as behaviour rather than keystrokes.
- **Paths** — the files this slice reads, creates, and modifies, each prefixed with `Read`, `Create`, or `Modify`. They live here rather than in `map.md` so that a slice stays self-sufficient.
- **Verify** — the command that proves this slice green, and where it was found. A command marked `to create` does not exist yet: creating it is part of this slice's Build.

## log.md

Write the header only. The implementing sessions fill it.

```markdown
# Log

Append per slice: what landed, what deviated from the plan, and what the next slice needs to know.
```
