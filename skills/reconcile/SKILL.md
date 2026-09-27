---
name: reconcile
description: Reconcile a chosen UI prototype with the use cases the current interface supports, and settle the gaps before or during implementation.
disable-model-invocation: true
---

Make a chosen prototype safe to implement as the UI source of truth. A prototype settles what it shows; the current interface supports more than any prototype shows. Find where the two disagree or where the prototype is silent, and settle what should happen there. Start from the chosen prototype or artifact, the conversation that chose it, and any supplied contract, plan, or reported discrepancies. Diagnose and recommend; do not change product code.

Pin the reference before comparing. Commit the prototype's code or an artifact's HTML, and screenshots of every state and viewport it shows, to a branch off main; record the branch, commit SHA, path, and variant key. Do not push the branch unless asked. Outside a Git repository, save them under `${STRIKER_ROOT:-${XDG_STATE_HOME:-$HOME/.local/state}/striker}/references/<slug>-<date>/` instead. When the choice combines parts of several variants, ask for one converged variant or describe the combination precisely.

Dispatch subagents for independent discovery. Give each a bounded question and request concise findings with evidence: file references, screenshots, or source URLs.

- **Inventory**: list the use cases the current interface supports, from code and the running interface: actors and permissions, feature flags, entry points, actions, empty, loading, error, and first-run states, data extremes such as long, missing, or many values, and narrow viewports.
- **Reference**: from both its code and rendered output, list the states, viewports, interactions, components, tokens, copy, and data assumptions of the prototype. Report states its code handles that no screenshot shows.

Map every inventoried use case against the reference as `kept`, `changed`, `unshown`, `dropped`, or `conflicting` (with a constraint, the design system, or accessibility). Treat `unshown` and `dropped` with most suspicion. Deliberate changes already settled in conversation need no question.

Settle precedence first, so defaults resolve most gaps without a question. Recommend, unless the user has decided otherwise: the prototype wins on layout, hierarchy, components, copy, and interactions for what it shows; current behavior wins on what it does not show; unshown states follow existing project patterns; where its code and the approved rendering disagree, the rendering wins; the design system and WCAG win on conflict unless the prototype changes them deliberately; and which choices to delegate to implementation, with constraints.

Ask about the remaining consequential gaps with options and a recommendation. Group independent questions and defer dependent ones until their prerequisites settle. Wait for answers before treating recommendations as decisions.

Use numbered questions with explicit lettered choices (`A`, `B`, `C`) on separate lines. Keep question numbers unique across rounds; restart choice letters at `A` for each question. Give each a recommendation that names its choice letter, ties it to the mapping or a precedence rule, and explains its main tradeoff.

```markdown
❓ **Q1 — Where does per-row edit go in the new table?**

- **A.** An action revealed on row hover
- **B.** An overflow menu on each row
- **C.** Edit only from the detail page

➡️ **Recommended: A** — Current behavior lets editors act on
permitted rows directly; a hover action keeps that capability while
preserving the prototype's clean rows, at the cost of discoverability on touch.
```

Accept brief replies such as `Q1 A`, custom answers, and modifications to choices. Record answers before moving to dependent questions.

During implementation, settle reported discrepancies and decisions awaiting review the same way; an overturned decision names its replacement and the work it affects.

Record each settled gap as a `D<n>` ledger entry: what came up, decision, reason, and status `settled` or `overturned`. With a supplied contract, amend its UI reference section, preserving approval and identifiers, and name the planned work the change affects. Without one, finish with a recap for the contract: the pinned reference, mapping, precedence, delegated discretion, ledger entries, and open gaps.
