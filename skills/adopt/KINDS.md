# Prototype kinds

Each kind names what to pin, what to inventory, what a prototype can conflict with, and the default precedence it adds to the rules every kind shares.

## `ui`

- **Pin**: the prototype's code, or an artifact's HTML, and screenshots of every state and viewport it shows.
- **Inventory**: actors and permissions, feature flags, entry points, actions, empty, loading, error, and first-run states, data extremes such as long, missing, or many values, and narrow viewports.
- **Reference**: states, viewports, interactions, components, tokens, copy, and data assumptions, from both code and rendered output.
- **Conflicts**: the design system and accessibility (WCAG).
- **Precedence**: the prototype wins on layout, hierarchy, components, copy, and interactions for what it shows; the design system and WCAG win on conflict unless the prototype changes them deliberately.

## `logic`

- **Pin**: the prototype's code and the scenarios, inputs, and outputs or traces it was judged by.
- **Inventory**: callers and entry points, states and transitions, invariants, inputs including invalid and extreme ones, error and retry paths, concurrency and ordering, persisted data and its existing shapes, and side effects on other systems.
- **Reference**: states, transitions, invariants, data shapes, interfaces, and the error behavior it demonstrates, from both code and exercised scenarios.
- **Conflicts**: public contracts and existing callers, persisted data and migrations, security, and performance limits.
- **Precedence**: the prototype wins on the model, transitions, and data shapes it exercises; existing public contracts and persisted data win on conflict unless the prototype changes them deliberately, and such a change names its migration or compatibility path.
