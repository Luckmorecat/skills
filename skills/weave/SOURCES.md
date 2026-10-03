# Sources of truth

Orchestrator steps for a brief that names sources of truth. Give every reconciler, beyond the handoff, the latest map's path when one exists.

## Map

When the sources settle behaviour beyond the brief's acceptance, such as a prototype, design, or spec with examples, dispatch a reconciler to map the brief's scope before deciding chunks. Settle each **Needs decision** item before deciding the chunks it affects.

## Discrepancies

When workers report discrepancies with the sources of truth, send all pending discrepancies to a reconciler in one batch, with the reports that raised them and the worktree of each parallel chunk. Only the chunks they affect stay paused.

## Results

Whenever a reconciler returns, add each **Resolved** item to the brief. When an item adds behaviour, write acceptance for it and assign that to the chunk that owns the affected files, or to the integration worker. Deliver **Resolved** items like any other update, and treat each **Needs decision** item as a question.

## Check

Once a reconciler has saved a map, dispatch one to check each committed result against it. Pass the brief's scope too when a reconciler mapped that scope; a map built only from discrepancies is checked item by item. Repair its gaps like any other check gap, and treat its **Needs decision** items as questions.
