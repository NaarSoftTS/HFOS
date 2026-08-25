# Morning Briefing — Runbook

_Execute exactly. Charter and permissions: `CHARTER.md` in this folder. Where a step says a tool does the mechanics, call the tool. This runbook assumes only what ships in the box — every optional capability is checked before use, and an unreachable capability is a named gap, never a silent omission._

---

## Ground

1. **Judgment load:** `system/wisdom/CORE.md`; add the `people` facet if the day is relationally heavy (`system/wisdom/README.md`).
2. Read `NOW.md` — the season's constraints, focus, and fronts. If it still holds elicitation prompts, the correct move is one line inviting the person to set the season — never an invented one.
3. Read `foundations/SUMMARY.md` — the compass card. The briefing coaches from their values, or (before elicitation) from none.
4. Read **yesterday's briefing** if one exists in `system/memory/briefings/` (newest = highest `YYYY-MM-DD` in the filename). Continuity is what makes this coaching rather than daily commentary. No previous briefing = first run; say so warmly in one line.

## The momentum read

5. Read `momentum/NEEDS_ME.md` and `momentum/BLOCKED.md` in full, and `momentum/READY_TO_SHIP.md`.
6. Read `momentum/WAITING.md` **only for entries `system/tools/due-dates.py --file momentum/WAITING.md` returns as due.** An entry on someone else's clock with a future check date must not appear in the briefing at all.
7. **For each due waiting entry, make the call:** did it release, or did it become a chase? Released → say so. Became a chase → it moves to `momentum/BLOCKED.md` with the person and the release condition named.
8. **Reading is not listing.** Render: every `NEEDS_ME.md` entry (the only list asking for their time) · every `BLOCKED.md` chase, marking those now due · every due waiting entry with the step-7 call · `READY_TO_SHIP.md` entries (finished work sitting at a gate is the most expensive thing in the system; an empty outbox is worth one honest line).
9. Read `momentum/COMMITMENTS.md` and merge any commitment needing motion into the entry that carries it — one entry per thread, never the same item under two headings.

## The day itself

10. Check `system/adapters/connections.md` for what this install can actually reach. **Calendar connected:** read today's schedule. **Mail connected:** scan for overnight messages needing the person. **Neither connected:** the briefing simply has no calendar/mail section — one line names the gap the first few runs, then silence is understood.
11. For each person on today's calendar (if any), load `relationships/people/<slug>.md` when a file exists, so the briefing carries relational context. **Care material never becomes pipeline** — what someone shared in confidence shapes tone, never appears as intelligence.

## Write it

12. **Convene the coach lens once** — `system/team/coach/TEAM.md` — and write the whole briefing in its voice: calm, practical, purposeful. Structure, empty parts collapsed to a line:
    - **Ground** — the kind of day ahead and a healthy pace, inferred from evidence, never presumed
    - **Aim** — the one meaningful outcome that would make today successful. Never task volume. Closes: *"If today only produces three moves: X, Y, Z"*
    - **The workspace journey** — one workspace at a time: what matters there, the best next move, then that workspace's momentum items as a focused path. A workspace that can't get real attention today gets its minimum meaningful move or an honest "nothing needed here today"
    - **Quick clears** — small items batched in one light sitting, one line each
    - **Not today** — visible work deliberately not receiving attention, named without guilt
    - **One practice** — a single behavioral emphasis grounded in this day. Never stacked; never a new one while the last went unanswered
    - **Questions** — anything the system needs the person to answer, batched last
13. **Two pages is the ceiling, one page is the target** (cap: 120 lines). Cut counted remainders and least-load-bearing coaching first — never `NEEDS_ME.md` entries, never the questions.
14. Save to `system/memory/briefings/YYYY-MM-DD-morning.md` (create the folder on first run). The archive is also the evidence this loop ran.

## Verification

Before reporting done: the briefing file exists · it fits 120 lines (`check-ceilings.py --file … --max 120`) · no future-dated waiting entry appears · every due waiting entry carries a decision · no item appears twice · every unreachable connector is named, not silently omitted · nothing was added to `momentum/NEEDS_ME.md` that the person didn't put there.

## Escalation

- A due waiting entry that became a chase moves to `momentum/BLOCKED.md` in this run, naming the person and the release condition.
- Anything requiring the person's judgment, authority, voice, or presence is already in `momentum/NEEDS_ME.md` — the briefing renders it, never adds to it.
- Everything else the briefing simply reports. **It never manufactures urgency** — nothing in this system benefits from making a person feel behind.
