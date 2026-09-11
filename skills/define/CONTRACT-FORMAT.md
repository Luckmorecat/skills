# Work contract

Use one contract for small and large work. Keep it concise and self-contained:

- **Goal / Build** — observable outcome, actor or caller, and scope.
- **Acceptance** — stable IDs for success and boundary examples.
- **Constraints and exclusions** — hard requirements and out-of-scope work.
- **Decisions** — user-approved choices and reasons, separate from `A<n>` assumptions and `D<n>` defaults.
- **Evidence / Paths** — repository root, remote when available, branch/worktree, inspected revision (or `unborn`), evidence state, and relevant code entry points. Cite facts with `file:line`; mark intended paths unverified.
- **Unknowns** — `U<n>`, dependent work, resolver, and required evidence; `None` when resolved.
- **Verify** — observable proof of acceptance. For directly executable work, include commands and their sources; missing commands are `to create` work. For larger scope, specify the verification approach without inventing later implementation details.

Present this for approval; preserve existing authorization. Write the approved `contract.md` outside the repository:

```bash
striker_root="${STRIKER_ROOT:-${XDG_STATE_HOME:-$HOME/.local/state}/striker}"
if repo_root=$(git rev-parse --show-toplevel 2>/dev/null); then
  repo=$(basename "$repo_root")
else
  repo=$(basename "$PWD")
fi
slug="oauth-device-flow"   # replace with a short kebab-case summary
mkdir -p "$striker_root/contracts/$repo"
mkdir "$striker_root/contracts/$repo/$slug-$(date +%F)"
```

Create the leaf without `-p`; if it exists, choose a more specific slug. Return the absolute file path. For an amendment, update the supplied contract and record the old decision, replacement, reason, and approval.
