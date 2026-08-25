# Structure

_JIT — load when creating folders/files. Kernel: `AGENTS.md`. Index: `INDEX.md`.  
**Ceilings registry of record:** `system/tools/check-ceilings.py` — summary table in `STRUCTURE-CEILINGS.md`._

---

## Progressive structure

**Create on first write. Never scaffold empty.** Missing file = honest signal. Empty templates destroy the signal and fake a populated tree (earned: 37 empty memory files once had to be deleted).

- Workspace at birth = `HOME.md`. Project at birth = `PROJECT.md`. Everything else appears the day it carries a real entry.
- **Deliberate asymmetry** — do not "normalize" contexts by filling missing files.

---

## Workspace face

```
workspaces/<workspace>/
├── HOME.md          routing card
├── FOUNDATIONS.md   mission, model, non-negotiables (+ ANCHOR)
├── STATE.md         current truth — rewritten, dated (the one file that can go stale)
├── OUTCOMES.md      optional — earned by maturity (`TRACE.md`); never owed
├── DECISIONS.md     permanent + reasoning
├── TIMELINE.md      append-only gist log
├── PEOPLE.md        linked people + transient contacts
├── projects/
├── NEXT.md          workspace-level next moves
├── possibilities/   explored / not-now
└── _archive/        never current truth
```

**Depth is the point** — load HOME → FOUNDATIONS/STATE → project PROJECT/NEXT as work narrows. Pending work that must move registers in **`momentum/`**, not only in a quiet workspace file.

**`NEXT.md` / `PEOPLE.md`** may sit at workspace or project — nearest context that knows them. Create-on-first-write.

**ANCHOR** on entity faces (`FOUNDATIONS.md`, life `HOME.md`) — see block below. `teleology-scan.py` checks presence + 60-day freshness. **Projects inherit** until they earn their own heart material.

```
last-validated: YYYY-MM-DD
<serves>Serves [parent] by [contribution].</serves>
<objectives> max 3 current dated; derived:: when applicable </objectives>
<signals> Material if … · Ignore: … </signals>
```

**STATE skeleton:** now-true · open · blocked · pointers to DECISIONS/TIMELINE. Rewrite on delta only.  
**TIMELINE:** date + 1-line gist + source pointer (2 lines only for high-value decisions).

**Sub-workspaces / partner groups:** same face; default operate at **group** level; pull a member out only when it has earned distinct focus.

---

## Project face

```
workspaces/<workspace>/projects/<project>/
├── PROJECT.md       why · who benefits · definition of shipped
├── STATE.md         where it stands
├── NEXT.md          next moves (not a task dump)
├── PEOPLE.md        only if contacts the workspace doesn't hold
├── working/         workbench
├── deliverables/    finished artifacts
└── history/         what happened
```

`PROJECT.md` is coaching, not a spec header. No definition of shipped → not a project yet.

## Life areas

Same shapes **when earned**. Most need only `HOME.md` for a long time — correct, not incomplete.

---

## Heavy artifacts & sources (outside this tree)

Logical names only; absolute paths once, in `system/adapters/`.  
Full rule: **`COMPANION-STORE.md`** — **sources are not brain intelligence.**

| Class | Store | Rule |
|---|---|---|
| Deliverables, media, decks | `@resources` | ship → `exports/<slug>/`; bulk → `library/<slug>/` |
| **Source material** (raw MD dumps, full texts, course bodies, transcripts, research dumps) | `@resources/library/…` | **Not ambient.** Tree keeps a short **SOURCE pointer** (`kind:: source` + load gate). Open only when processing that source |
| Cold inbox / cold memory archives | `@resources/_system/backup/…` | Recovery only |
| Runnable code | `@dev` | Own git repo — never in this tree |
| Published web | `@publish` | Firewall — only what is copied there |
| External messages | `@coms` | Inbound; sweep → `inbox/` |

**Tree = signal.** Distill into STATE/DECISIONS/TIMELINE; do not keep undigested source as workspace “intelligence.”  
Practical trigger: multi-file source corpora and undigested files ≳40–50KB → companion store + pointer.  
**Reachability precheck** before any out-of-tree write. Unreachable → stage in-tree, name human placement, never report shipped.

---

## Freshness & naming

- **Stale** = subject moved and file didn't. Age alone ≠ stale. Contradiction with live evidence = finding immediately.
- Archives: `_archive/` beside subject; never current truth.
- Files/folders: `kebab-case`. Face files: `SCREAMING-CASE`. One canonical file per person/workspace/project. Dated outputs: `YYYY-MM-DD-slug.md`. Root = permanent undated only.

---

## Ceilings

**Branch then compress — never raise quietly.** Bytes bind as well as lines. Script measures; model decides what to branch.  
Reader summary + exemptions → **`STRUCTURE-CEILINGS.md`**. Registry of record → **`check-ceilings.py`**.
