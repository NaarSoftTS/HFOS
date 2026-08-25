# tools/ — The Judgment Line

**Scripts do mechanics. Models judge.**

This folder exists because a model doing arithmetic inside a prompt is expensive, unverifiable, and eventually wrong without telling anyone. Counting lines, comparing dates, diffing directories, resolving paths, assembling evidence — these are deterministic, cheap, and checkable. Deciding what to compress, whom to chase, what to build, and what a finding means is judgment, and that stays with the model and the person.

**The rule this enforces:** *if a loop's runbook contains date math, line counting, or file mechanics, that is a defect with a fix.*

---

## The scripts

| Script | Answers |
|---|---|
| `orphan-scan.py` | Does every tree path this system mentions resolve? Tree-relative paths plus branch siblings (`references/…`, `archive/…`) — **not** other relative forms |
| `check-paths.py` | Does any host-specific path exist outside `system/adapters/`? |
| `check-ceilings.py` | Which session-start files are over their ceilings, and by how much? |
| `store-reachable.py` | Is `@resources` / `@dev` / `@coms` / `@publish` mounted *this session*? |
| `path.py` | Resolve/write/read/find/ls logical paths (`system/…`, `@tree/…`, `@resources/…`); stray-scan home mirrors |
| `loop-integrity.py` | Did this loop actually complete? Artifacts vs last-run stamp; unrecovered cron `[SILENT]` |
| `last-run.py` | When did this loop actually last run, and did its input finish first? |
| `due-dates.py` | What is due, overdue, stale, or out of contact? |
| `file-ages.py` | What has aged past its cap, what arrived since a stamp, what is missing from a dated series? |
| `momentum-lint.py` | Does every ledger entry obey the momentum grammar? |
| `ask-ledger-lint.py` | Do ask-ledger lines follow the grammar — date · canonical class · subject, nothing else? *(ships where system adaptation does)* |
| `classification-lint.py` | Are classification tags well-formed, audiences named, and the always-on surface ≤ internal? |
| `teleology-scan.py` | Which entity faces carry no ANCHOR, and which are stale? |
| `schedule-diff.py` | Do the defined automations match what is actually scheduled? |
| `status-scan.py` | What has sat in one work state too long? |
| `render-briefing.py` | Place a rendered briefing on a store — **refusing when it is unreachable** |
| `_lib.py` | Shared helpers: tree root, safe walking, duration parsing, adapter stores, **logical path router** (`resolve_spec`) |

---

## Conventions every script follows

**Exit 0 is clean. Exit 1 means findings — a signal, not an error.** A loop reading exit 1 has something to think about, not something that failed. Only a traceback is a failure.

**Nothing crashes on an unmigrated tree.** Most content files don't exist yet. A script that finds nothing prints *not yet migrated* and exits 0. This matters: during migration these scripts run constantly against a tree that is half-built.

**No absolute paths, anywhere.** The tree root is derived from the script's own location. External stores are resolved through `system/adapters/` — the one place a host path is allowed to exist. `check-paths.py` keeps that true.

**`--json` on everything that reports.** Loops parse; humans read the plain output.

**Standard library only.** A tool that needs a dependency install is a tool that will be broken on some harness at 1 AM.

---

## Adding a tool

Add one when you find a runbook step doing mechanics — that is the trigger, and it's the only one. The test: *could this step be wrong in a way nobody would notice?* If yes, it belongs here, because a script is wrong loudly and a model is wrong quietly.

Match the house shape: a docstring that says **why** the script exists in judgment-line terms rather than restating its flags, `_lib` for shared behaviour, the `== <title>` output block, and the exit convention above.

---

## Deferred

`dashboards/` — the dashboard generators from the previous tree. Not ported: they read the old kanban board and its JSON snapshot, both of which the momentum grammar replaces. They are rebuilt against `momentum/` when the migration reaches that step, not before.
