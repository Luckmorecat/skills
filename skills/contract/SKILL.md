---
name: contract
description: Turn settled conversation or supplied documents into a concise work contract for implementation or slicing.
disable-model-invocation: true
---

Create or amend a self-contained work contract from the current conversation, supplied documents, and codebase understanding. Do NOT interview the user; synthesize what is already known. Reuse settled intent and preserve existing approval, delegation, and identifiers.

Capture agreed user or caller needs and derive observable acceptance examples. Inspect relevant code for component responsibilities, interfaces, existing test boundaries, and verification commands; distinguish current facts from intended changes. Keep proposals and unverified assumptions separate from agreed decisions.

Capture every agreed need and settled decision, link acceptance to observable proof, and identify delegated discretion. Record unresolved choices or conflicting intent with the affected work and what would resolve them.

Use [CONTRACT-FORMAT.md](CONTRACT-FORMAT.md) to present and save the contract. Keep its detail proportional to the work. Return the absolute path.
