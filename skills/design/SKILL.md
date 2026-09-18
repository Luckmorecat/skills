---
name: design
description: Explore technical approaches and strengthen a supplied contract or spec with decisions that make implementation easier.
disable-model-invocation: true
---

Turn technical uncertainty into decisions precise enough for implementation. Start from the supplied contract or spec and relevant conversation. Preserve settled intent and constraints; focus on technical choices that simplify implementation or resolve ambiguity.

Identify where libraries, tools, design patterns, or simpler structures could help satisfy the requirements. Recommend approaches for concrete needs, with reasons and tradeoffs. Keep cheaply reversible implementation details open.

Dispatch a research subagent when choosing a library, tool, design pattern, or technical mechanism. Have it research currently available solutions using primary sources, including simpler approaches that avoid an additional dependency. Assess fit against the requirements, limitations, integration cost, and maintenance where relevant.

When existing code affects the choice, dispatch a separate exploration subagent to inspect relevant behavior, interfaces, dependencies, ownership, and conventions. Treat internals being replaced as current behavior, not constraints on their replacement.

Give each subagent a bounded question and request concise findings, implications, uncertainties, and supporting references. Keep detailed exploration in subagent context; compare approaches and resolve decisions in the main session. Follow up on consequential claims or gaps that could change the choice.

Compare credible alternatives against the contract's requirements and constraints. Favor the simplest approach that meets them. Explain why the recommendation fits and what costs or limitations it introduces; avoid manufacturing alternatives.

Test the approach against concrete success, failure, and boundary scenarios. Work out responsibilities, interfaces, data flow, and failure behavior where they matter to implementation. Revise choices that expose contradictions or unnecessary complexity.

Ask about unresolved consequential tradeoffs with options and a recommendation. Group independent questions and defer dependent ones until their prerequisites settle. Reuse existing decisions and delegation; otherwise wait for the user's answer before treating a recommendation as settled.

Distinguish verified facts, proposed designs, and remaining assumptions. When a choice depends on missing evidence, identify what would resolve it and which part of the design remains uncertain.

Amend the supplied contract or spec with agreed technical decisions, their rationale, and the details implementers need to preserve. Integrate changes into its existing structure, preserving identifiers and unrelated content. Keep unresolved choices explicit. Without a supplied file, return the proposed additions in conversation.

Continue until the in-scope technical choices are resolved or explicitly open with their implementation consequences understood. Finish with a brief recap of the changes, amended paths, and remaining uncertainties.
