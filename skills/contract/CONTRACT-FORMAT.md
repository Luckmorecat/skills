# Work contract

Use one contract for small and large work. Keep it self-contained and let coverage determine its length. Always include separate Problem Statement and Solution sections. For small changes, combine other sections when the same information is clear without them.

- **Problem Statement** — the problem the user is facing, from the user's perspective.
- **Solution** — the solution to the problem, from the user's perspective.
- **User stories** — every distinct user or caller need within the agreed scope, with stable IDs. State the actor, needed capability, and purpose; include alternate actors, recovery, and operational needs where relevant. Derive stories from settled context and surface newly discovered needs as proposals. For a small fix, the problem statement, solution, and acceptance may carry this information without a separate story list.
- **Acceptance** — observable success, failure, and boundary examples with stable IDs. Link examples to story IDs when stories are present; cover every agreed need. Stories explain why a capability matters; acceptance specifies the behavior that demonstrates it works.
- **Constraints and exclusions** — hard requirements and out-of-scope work.
- **Implementation decisions** — record every settled implementation choice and its rationale, preserving identifiers and approval or delegation status. Cover decisions about component responsibilities, interfaces and API contracts, data or schema changes, interactions and state transitions, failure behavior, and compatibility. These categories are prompts for coverage; include decisions outside them too. Leave undecided routine implementation details open. Include a small schema, type shape, or state model when it expresses a settled decision more precisely than prose.
- **Testing decisions and verification** — observable proof linked to every acceptance ID. Identify the behavior to exercise, the test boundary, relevant existing tests to follow, and new coverage to create. Prefer existing boundaries that prove the behavior reliably; exercise implementation details only through their observable effects. Include integration checks where isolated checks cannot prove the combined behavior. For directly executable work, include commands and their sources; missing commands are `to create` work. For larger scope, specify the verification approach without inventing later implementation details.
- **Repository context** — repository root, remote when available, branch/worktree, and inspected revision (or `unborn`). Add code entry points or source references when they materially help implementation; file paths and line citations are optional. Distinguish inspected code from proposed structure.
- **Open choices and delegated discretion** — separate unresolved proposals and unverified assumptions from settled decisions. For each consequential gap, state the affected work and what resolves it. Identify choices explicitly delegated to implementation and the constraints on that discretion.

Save the synthesized `contract.md` outside the repository and present its readiness and unresolved gaps. Preserve existing authorization; distinguish a draft from an approved contract without requiring another interview or approval round:

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

Create the leaf without `-p`; if it exists, choose a more specific slug. Return the absolute file path. For an amendment, update the supplied contract and record the old decision, replacement, reason, and existing approval or unresolved proposal status.
