# Behavioral evaluation

Choose a proportional evaluation before editing. A useful small set covers an
ordinary task, a near-miss trigger, a missing dependency or ambiguous input, and
an authorization boundary. Use realistic artifacts rather than asking whether
the agent likes the instructions.

Record each request, initial state, permitted actions, and observable pass
criteria before runs. Score the produced result and side effects, not preferred
wording. Keep expected answers and prior findings out of the executor's prompt.
Test discovery separately from execution: forcing a skill into context does not
show that its description selects it correctly.

For comparison, use the existing skill or normal no-skill workflow as baseline.
Keep model, tools, permissions, inputs, and budget equivalent; isolate workspaces
and start fresh sessions. Repeat trials when practical and include held-out cases
not used to revise the candidate. Do not weaken required safeguards in a baseline.

Record correctness, constraint adherence, unwanted actions, and cost/time
separately. If usage or latency is unavailable, say so; do not substitute prose
length for cost. Preserve failed, inconclusive, and tied results. Human review
and model judging should use a fixed rubric, preferably blinded to condition;
identify the judge and any subjective criteria.

Small samples support smoke-test conclusions, not statistical or general
performance claims. Test changes prompted by failures on both the failing case
and untouched cases. If the comparison cannot run, report the proposed test plan
and static checks, not an empirical improvement.
