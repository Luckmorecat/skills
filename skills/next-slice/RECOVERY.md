# Resume

`plan status` lists each in-progress slice, and each blocked slice that records a fixed point, with its fixed point and checkpoint `checkpoints/<ID>.md`; `plan status --json` adds the dirty snapshot. Compare the checkpoint with relevant `log.md` history, Git commits, and the working tree. A checkpoint alone is not completion: check landed revisions, acceptance evidence, and review results. If a commit landed before `plan complete`, inspect it and recover missing checks or review instead of implementing it again.

Return a blocked slice to work with `plan resume <ID>` once its blocker is resolved; the recorded fixed point and dirty snapshot stay its baseline. Distinguish owned changes from pre-existing and newly unrelated work; resolve uncertain ownership before staging. Continue from the checkpoint's next action, updating the checkpoint if the working tree changed.
