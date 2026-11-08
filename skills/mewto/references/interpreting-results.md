# Interpreting mutation results

## Read the outcome

Distinguish **no coverage** (changed code was not exercised) from **survived** (covering tests passed). Neither establishes equivalence. Tool labels differ: Stryker includes timeouts in detected mutants. See [Stryker's outcome definitions](https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/).

## Find the missing link

For an undetected fault, trace these links until the cause is clear:

1. **Reach:** do the selected tests execute the mutated production code? Check discovery, imports, mocks, and coverage evidence.
2. **Distinguish:** do the inputs make the mutation produce a different state? Inputs can execute the changed expression while producing the same value.
3. **Propagate:** does that difference reach required observable behavior, or is it overwritten or masked first?
4. **Observe:** does an assertion check that behavior with a requirement-derived expectation?

Repair the missing link at the appropriate test boundary. Inspecting intermediate state for diagnosis does not make private-state assertions the desired repair. This sequence applies [Cornell's reachability, infection, propagation, and revealability model, slide 21](https://www.cs.cornell.edu/courses/cs5154/2021fa/resources/MutationTesting.pdf).

## Explain rather than force a kill

An **equivalent** mutant cannot change observable behavior for the applicable input domain. Give a concrete argument across that domain; matching results on existing examples is insufficient. An **irrelevant** mutant can change behavior outside the requirements in scope; name that contract boundary instead of calling it equivalent. Conflicting or missing requirements remain ambiguous. See [Stryker's equivalent-mutant discussion](https://stryker-mutator.io/docs/mutation-testing-elements/equivalent-mutants/).
