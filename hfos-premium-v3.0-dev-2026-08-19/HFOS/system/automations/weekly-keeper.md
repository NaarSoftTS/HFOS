# Weekly keeper — self-maintenance

_No schedule is active at install (deliberate). Ask for it when you want it: **"Run my keeper."**_

**Definition of record:** `system/loops/keeper/RUNBOOK.md` — the session reads that runbook and follows it; this file is the pointer, never a copy.

**What it does:** checks the system's own health — paths, ceilings, momentum hygiene, staleness — and leaves one page in `inbox/` with proposals. **It never edits your files;** every finding waits for your decision.

**Turning on a schedule (recommended: weekly):** after a manual run feels right, have your agent app schedule a task whose entire prompt is: *"Open this project's tree, read `system/automations/weekly-keeper.md`, follow its runbook pointer, fail closed on any missing file."*

**Fail closed:** if the runbook can't be found, say so and stop — never improvise a substitute pass.
