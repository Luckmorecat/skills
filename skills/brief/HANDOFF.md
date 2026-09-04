# Handing off a brief

A brief that leaves this session has to survive it, so write it down. Put it outside the repository, which keeps a commit of it out of reach rather than merely against the rules. Override the root with `STRIKER_ROOT`:

```bash
striker_root="${STRIKER_ROOT:-${XDG_STATE_HOME:-$HOME/.local/state}/striker}"
if repo_root=$(git rev-parse --show-toplevel 2>/dev/null); then
  repo=$(basename "$repo_root")
else
  repo=$(basename "$PWD")
fi
slug="oauth-device-flow"   # replace with a short kebab-case summary
mkdir -p "$striker_root/briefs/$repo"
mkdir "$striker_root/briefs/$repo/$slug-$(date +%F)"
```

The leaf is created without `-p` so an existing directory stops you rather than being written over: choose a more specific slug and retry.

Write `brief.md` in that directory with every section from the exit, in the same order and unchanged. The receiving session opens this file with no memory of the interview, so a section it has to reconstruct is a section you did not hand off.

Tell the user the absolute path. Whatever runs the work takes that path as its argument.
