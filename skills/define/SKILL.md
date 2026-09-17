---
name: define
description: Explore and grill an idea or feature until its purpose, experience, scope, and consequential decisions are clear.
disable-model-invocation: true
---

Explore the requested feature until its purpose, experience, scope, and consequential decisions are clear. Start from the user's existing context. When the direction is uncertain, contribute concrete possibilities and help choose one. A repository or commitment to build is optional.

Grill assumptions and use concrete scenarios to uncover missing behavior, contradictions, failure cases, and tradeoffs. Recommend answers with reasons.

Treat decisions as a tree. Ask independent questions whose prerequisites are settled together; defer questions that depend on unanswered choices. Wait for answers before treating recommendations as decisions. When the user delegates a choice, make it and explain why.

Use numbered questions with explicit lettered choices (`A`, `B`, `C`) on separate lines so the user can answer briefly. Keep question numbers unique across rounds; restart choice letters at `A` for each question. Give each a recommendation that names its choice letter and explains its main tradeoff. When a question needs an open-ended answer, ask it directly instead of inventing choices.

```markdown
❓ **Q1 — Who can invite members?**

- **A.** Any member
- **B.** Only the owner

➡️ **Recommended: A** — The group can grow without waiting on
its owner, at the cost of less control over who gets invited.

---

❓ **Q2 — When do invitations expire?**

- **A.** After seven days
- **B.** Only when revoked

➡️ **Recommended: A** — Seven days limits how long an
unused invitation grants access, at the cost of resending expired ones.
```

The user can reply: `Q1 B; Q2 A`. Accept custom answers and modifications to choices in plain text. Record those answers before moving to dependent questions.

Investigate facts yourself. Use subagents for independent exploration of relevant code, existing behavior, technical feasibility, and external evidence. Give each a bounded question and ask for findings with supporting evidence. Continue independent questions while they investigate; revisit dependent decisions when findings arrive.

Resolve choices within the requested scope that affect user-visible behavior, public interfaces, persistent data, security or privacy, deployment, external dependencies, ongoing cost, ownership between components, or the cost of changing direction. Surface these consequences even when the choice appears to be an implementation detail.

Distinguish settled decisions, proposals, and claims that still need evidence. User agreement settles intent; it does not prove feasibility or demand. When evidence is unavailable, identify what remains uncertain and what would resolve it.

Continue until concrete scenarios explain the main experience and meaningful boundaries, and every known consequential choice is resolved or explicitly left open with its implications understood. Clearly identify any open choice that prevents the feature from being fully defined.

Finish with a brief recap of settled decisions and remaining uncertainties.
