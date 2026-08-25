# Morning brief — on demand

_No schedule is active at install (deliberate). Ask for it when you want it: **"Run my morning brief."**_

**Definition of record:** `system/loops/briefing/RUNBOOK.md` — the session reads that runbook and follows it; this file is the pointer, never a copy.

**Turning on a schedule (later, optional):** after a few manual runs feel right, have your agent app schedule a task whose entire prompt is: *"Open this project's tree, read `system/automations/morning-brief-on-demand.md`, follow its runbook pointer, fail closed on any missing file."* The definition stays in the tree; the scheduler holds only the pointer.

**Fail closed:** if the runbook can't be found, say so and stop — never improvise a substitute briefing.
