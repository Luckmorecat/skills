# Resume and older plans

Compare current state, relevant history, Git commits, and the working tree. A log entry alone is not completion: check landed revisions, acceptance evidence, and review results. If a commit landed before logging, inspect it and recover missing checks or review instead of implementing it again.

Preserve the original starting revision and dirty snapshot. Distinguish owned changes from pre-existing and newly unrelated work; resolve uncertain ownership before staging. Continue from the recorded next action, updating evidence if the working tree changed.

For older plans, retain their execution order and recover state from their log and Git. Existing slice files remain executable when the approved acceptance and verification are available. If these are missing or prerequisites remain unresolved, checkpoint and return to `slice` for preparation. Record a deliberate checkout change; resolve unexplained repository or branch mismatches before editing.
