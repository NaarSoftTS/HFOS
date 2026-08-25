# Structure — Ceilings (branch of STRUCTURE.md)

_Load when measuring or authoring hot files. **Registry of record:** `system/tools/check-ceilings.py` — this table is a reader's summary, never a second source._

## Breach rule

A file breaches when **either** lines or bytes are over.  
**Fix:** branch (SIGNAL split_rule) → compress → archive history. **Never raise** without explicit recorded operator decision.

Branch first: what readers don't need on every load moves behind a **triggered** pointer. Guardrails never branch. A branch does not clear a breach by itself — the hot file is still measured as it stands.

## Reader summary (common faces)

| File | Lines | Bytes |
|---|---|---|
| `AGENTS.md` | 100 | 8,000 |
| `NOW.md` | 60 | 6,000 |
| `foundations/SUMMARY.md` | 120 | 9,000 |
| any `HOME.md` | 80 | 8,000 |
| any `STATE.md` | 150 | 12,000 |
| any `NEXT.md` | 60 | 5,000 |
| `momentum/` ledgers | 60–80 | 6,000–8,000 |
| `system/wisdom/CORE.md` | 100 | 6,000 |
| `system/wisdom/README.md` | 120 | 6,000 |
| other `system/wisdom/*` | 80 | 6,000 |
| role/shared job packs (`playbooks/<role|shared>/*.md`) | 80 | 4,000 |
| `system/agents/*/WISDOM.md` | 80 | 6,000 |
| anything else that loads | 150 | 15,000 |


Take the number from the script when it matters — ceilings live in one registry so tools cannot drift.

## Exempt (meant to grow; not default-load)

`DECISIONS.md` · `TIMELINE.md` · `_archive/` · cold `system/memory/` · `system/library/` · **branch siblings** (JIT depth) · `inbox/` · `system/upgrades/` · `_processed/`.

`check-ceilings.py` honours this list. **`--file` still measures** a named branch.  
**Registry entry outranks exemption** — e.g. `WORKING.md` / `working-log.md` stay measured inside an otherwise-exempt room.

## Judgment line

Script measures. Model decides what to branch and what to compress.
