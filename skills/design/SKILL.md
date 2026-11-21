---
name: design
description: Explore technical approaches for a supplied contract or spec and summarize decisions that make implementation easier.
disable-model-invocation: true
---

Turn technical uncertainty into decisions precise enough for implementation. Build on the supplied contract or spec and what the conversation already settles. Preserve settled intent and constraints; focus on technical choices that simplify implementation or resolve ambiguity, leaving cheaply reversible implementation details open. Keep the session read-only and conversational, leaving any file edits or implementation for a later step.

## Research and exploration

Cover the tracks below that affect the choice. Do targeted reads and searches inline; dispatch subagents (without editing repository files) only when external primary-source research or broad, multi-file codebase exploration would bloat this conversation. Give each subagent a bounded question and request concise findings, implications, uncertainties, and supporting references.

- **External research**: when choosing a library, tool, design pattern, or technical mechanism, inspect currently available solutions using primary sources, including simpler approaches that avoid an additional dependency. Assess fit against the requirements, limitations, integration cost, and maintenance where relevant.
- **Codebase exploration**: when existing code affects the choice, inspect relevant behavior, interfaces, dependencies, ownership, and conventions. Treat internals being replaced as current behavior, not constraints on their replacement.

Finish relevant discovery before asking questions that depend on it, and follow up on consequential claims or gaps that could change the choice.

## Evaluation and questions

Compare credible alternatives against the contract's requirements and constraints. Favor the simplest approach that meets them. Explain why the recommendation fits and what costs or limitations it introduces; avoid manufacturing alternatives.

Test the approach against concrete success, failure, and boundary scenarios. Work out responsibilities, interfaces, data flow, and failure behavior where they matter to implementation. Revise choices that expose contradictions or unnecessary complexity.

Treat unresolved consequential tradeoffs as a decision tree: batch independent questions whose prerequisites are settled, and defer branches that depend on unanswered choices. Reuse existing decisions and delegation; otherwise wait for the user's reply before treating a recommendation as settled. When the user delegates a choice, make it and explain why.

Write every question directly in your chat reply as numbered markdown (`Q1`, `Q2`, unique across rounds): give choice questions lettered options restarting at `A` per question and a recommendation naming the letter, tying it to the requirements or research findings, and explaining its main tradeoff; ask open-ended questions directly when choices would be artificial.

```markdown
❓ **Q1 — How should we represent the approval workflow?**

- **A.** An explicit transition table in the existing module
- **B.** A state-machine library

➡️ **Recommended: A** — The specified workflow has four states and
simple transitions. A table makes allowed transitions explicit with
little integration work; nested or parallel states could justify a library later.
```

Distinguish verified facts, proposed designs, and remaining assumptions.

## Done

Continue until the in-scope technical choices are resolved or explicitly open with their implementation consequences understood. Finish with a conversational summary, then stop so the user chooses what happens next:

- **Settled technical decisions** (with rationale, noting delegated choices)
- **Proposed contract additions or changes**
- **Remaining uncertainties** (affected design areas and what would resolve each)
