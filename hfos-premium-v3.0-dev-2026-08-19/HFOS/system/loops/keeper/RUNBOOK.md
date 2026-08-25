# Weekly Keeper — Runbook

_The system's self-maintenance pass. One job: keep the OS light and true so the person stays free. **The keeper proposes; it never edits.** Runs weekly by schedule, or any time the person asks: "Run my keeper."_

---

## What it is

A structural health check, not a briefing. It doesn't read the person's day or coach their work — it checks whether the *system itself* is staying light, current, and honest. (Where a briefing loop is installed, that loop owns the day; the keeper owns the structure.)

## Ground (minimal load)

1. `AGENTS.md` → `NOW.md` → `foundations/SUMMARY.md` — orientation only.
2. No team lens. No wisdom facets. This is mechanics plus honesty.

## The pass

**3 · Tools (if shell is available):** run and record results — `system/tools/check-paths.py` · `system/tools/check-ceilings.py` · `system/tools/momentum-lint.py` · `system/tools/store-reachable.py`. No shell → named degradation: do the same checks by reading, and say the tools didn't run.

**4 · Freshness sweep (read, don't judge the person — judge the files):**
- `NOW.md` — season set? Does it still read current, or has it quietly gone stale?
- The momentum room (five ledger files, or the single `momentum/MOMENTUM.md` — read what ships):
  Waiting — entries past their check date (`due-dates.py` if installed; otherwise read the dates) · Commitments — anything due or overdue · Blocked — chases that have sat without motion · Ready to ship — finished work sitting at a gate (the most expensive thing in the system)
- `inbox/` — items older than a week that never got routed
- `foundations/SUMMARY.md` — untouched for ~6+ weeks → one gentle question: "still true?"

**4½ · Ask-ledger tally (only where `system/memory/ask-ledger.md` exists):** update the profile block at its top — counts by class×subject, trailing 4 weeks + season-to-date; drill into a `>` sub-level only where one dominates. Pure arithmetic, no proposals; one line in the report. On the ledger's own ceiling breach, roll raw lines into the profile and archive. Ledger absent → skip silently (this version doesn't keep one).

**5 · Ceiling breaches:** for each file `check-ceilings` flags, propose a *specific* compression — quote the candidate lines and where the depth would branch to. Never apply it.

## Write the report

**6 ·** One page (ceiling: 60 lines) to `inbox/keeper-YYYY-MM-DD.md` — an inbox item like any other: the person processes it, then it goes. Structure, empty sections collapsed to a line:

- **Green** — what's healthy, in one line
- **Needs a decision** — due/overdue/stale items, each with a pointer to its file
- **Proposed compressions** — per breach, ready to accept or decline
- **Questions** — batched last; at most three

All green → the whole report may be three lines: *"System is light; nothing needs you. Tools clean. See you next week."* Empty is a good report, not a thin one.

## Hard bounds

- **Writes exactly one file:** the report. Never edits `foundations/`, `NOW.md`, momentum, workspaces, or any owner file.
- **Creates nothing else:** no tasks, no commitments, no memory entries. A keeper finding becomes work only by the person's act.
- **Deletes nothing.** Keeps no index of declined proposals.
- **Fail closed:** missing file or unreachable store → named in the report, never guessed around.

## Schedule posture

Ships unscheduled (deliberate). After a manual run or two feels right, schedule it **weekly** — the scheduler's entire prompt: *"Open this project's tree, read `system/automations/weekly-keeper.md`, follow its runbook pointer, fail closed on any missing file."* The definition stays in the tree; the scheduler holds only the pointer. No scheduler in your agent app → just ask weekly; nothing else degrades.
