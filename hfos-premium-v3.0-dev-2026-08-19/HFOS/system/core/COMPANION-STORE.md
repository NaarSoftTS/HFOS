# Companion store — `@resources`

_Product standard for every Human Flourishing OS: core tree ≠ file warehouse. **Sources are not brain intelligence.**_

## Why two layers

| | **Core tree (brain)** | **Companion store (`@resources`)** |
|---|---|---|
| Holds | Judgment, truth, momentum, people, operating notes — **compressed signal** | Binaries, decks, media, shipped packs, **raw/source material**, cold history, rendered surfaces |
| Edit surface | Obsidian + agents (hot load) | Finder / Explorer / studio tools |
| Backup | Git | Dropbox / OneDrive / iCloud / local sync |
| Logical name | _(tree root)_ | `@resources` |
| Inside git? | Yes | **Never** |
| Ambient load? | Session / face / judgment paths | **No** — open only on explicit source-work |

A rebuild that stuffs multi‑GB media **or multi‑MB source dumps** into the brain has failed the standing check: the operator should stay free, and the OS should stay fast to sync, review, and ship to others.

---

## Sources vs brain (hard)

**Source material is not intelligence.** Transcripts, book full-texts, course lesson dumps, raw meeting captures, scraped exports, research PDFs, and any file kept only so it can be re-processed later belong in `@resources` — not in workspace face, not in `system/memory/` hot, not as ambient context.

| Class | Lives | Load rule |
|---|---|---|
| **Brain** — STATE, DECISIONS, TIMELINE gist, HOME, FOUNDATIONS, NEXT, wisdom, playbooks | Core tree | JIT per kernel |
| **Operating note** — short distilled brief that *is* current judgment | Core tree (ceilings apply) | With its subject |
| **Source** — raw or near-raw material to process, quote, rebuild from | `@resources/library/<slug>/…` (or `_system/backup/` if cold) | **Only** when the task is to process that source |
| **Ship artifact** | `@resources/exports/<slug>/` | When shipping / reviewing the pack |
| **Cold history** | `@resources/_system/backup/…` | Almost never; recovery only |

### Size trigger (practical)

- Prefer **any** multi-file source corpus and **any single file ≳40–50KB of undigested source** out of the tree.
- Living DECISIONS/TIMELINE that *are* the record may stay larger — still compress/branch per SIGNAL; do not use that exception for dumps.
- If in doubt: **distill signal into STATE/DECISIONS; park the dump under `@resources` with a pointer.**

### Pointer shape (tree side)

Keep a **short pointer at the old path** (or in workspace `RESOURCES.md`) so routes do not break. Pointers must name **kind** and **load gate**:

```markdown
# SOURCE — not brain

kind:: source
load:: only when this session must process the underlying source
  (extract · quote · rebuild curriculum · re-ingest · audit original).
  Never ambient. Never judgment, briefing, hero, or default workspace face.
canonical:: `@resources/library/<slug>/…`

Was: `workspaces/…` (or prior tree path)
Moved: YYYY-MM-DD
```

- **kind:: source** is required language — agents treat it as non-intelligence.
- Do not leave a second full copy in the tree after the move.
- Distilled notes (short) may remain in-tree and **point down** to the full source.


### Pointer shapes (unified)

One agent-facing shape for anything that is **not brain**:

| Stub in tree | Use for |
|---|---|
| `# SOURCE — not brain` + `kind:: source` + `load::` + `canonical::` | Raw dumps, full texts, course bodies, **and** bulk binaries (html/pdf/docx stubs) |
| Legacy `*.MOVED.md` filename | Allowed if body is SOURCE-shaped. Prefer that body over a separate “Moved” dialect |

**Cold vs hot inbox:**

| Shelf | Path | Loop load |
|---|---|---|
| Hot processed | `inbox/_processed/` | The overnight loops *(when installed)* write daily tables and may harvest **recent** files here |
| Cold processed / RAW | `@resources/_system/backup/aios-processed/…` | **SOURCE** — recovery or deliberate re-process only |
| Rule of thumb | RAW or ≳80KB undigested → cold companion; short ops logs stay hot days/weeks | |

Do **not** empty the hot shelf into cold so aggressively that overnight loops lose recent process tables.


### Where sources go under `@resources`

| Material | Path |
|---|---|
| Workspace/project sources & bulk | `library/<workspace-slug>/…` (mirror tree shape when helpful) |
| Shared reference (books, frameworks full text) | `library/reference/…` |
| Inbox RAW / processed cold | `_system/backup/aios-processed/…` (cold) · hot ops tables stay in `inbox/_processed/` · `ingest/` only while raw-hot |
| Cold OS memory archives | `_system/backup/memory-cold/…` |
| Shipped packs | `exports/<slug>/` — not library |

---

## Recommended disk name

**`HFOS-Resources`** (no spaces).

Host path appears **only** in `system/adapters/<harness>.md` §4.  
All runbooks, skills, and workspace notes use `@resources/…`.

## Standard layout

```
the companion resources folder (@resources)/
├── README.md
├── exports/<slug>/      # shipped
├── library/<slug>/      # sources + working bulk
├── ingest/              # raw intake (still hot)
├── briefings/           # rendered mornings
├── studios/             # engines (image-studio, …)
├── external-os/         # OS packs for others
└── _system/             # backup, packs, to_delete, memory-cold
```

**Minimal client install:** `README.md` + `exports/` + `library/` + `ingest/`.

**Slug rule:** same as `workspaces/<slug>/` in the core tree.

## Adapter mapping (example)

```markdown
| `@resources` | `<absolute path to your resources folder>` | Companion file store — see system/core/COMPANION-STORE.md |
```

Mac / OneDrive / plain folder: change the absolute path only; keep the layout and `@resources` name.

## Indexes

- `@resources/README.md` — store map  
- `@resources/library/INDEX.md` / `exports/INDEX.md` — zone maps  
- `@resources/library|exports/<slug>/INDEX.md` — when bulk exists  
- Workspace hub (optional): `workspaces/<slug>/RESOURCES.md` — **pointers only**, with load gates  

## Related stores

| Name | Role | Backup |
|---|---|---|
| `@dev` | Code repos | Git |
| `@publish` | Live web copy | Host / CI |
| `@coms` | Inbound drop | Provider + optional archive |

## Distribution (HFOS for others)

1. Ship **core tree** as git (clean-build: empty rooms + engine).  
2. Instruct: create **`HFOS-Resources`** beside the tree (or under their cloud root).  
3. Point their adapter `@resources` at that folder.  
4. Start minimal zones; grow studios/external-os only if needed.  
5. Never require Dropbox specifically — any reliable file sync works.  
6. Teach **sources ≠ brain** on day one — full texts and course dumps never ship inside the clean brain.

## This install

Live path: adapter `hermes` §4 (Windows) / `cowork` §4 (Mac).  
Tree `exports/` is a **room stub** → canonical ship files at `@resources/exports/`.  
Doctrine cross-links: `STRUCTURE.md` (heavy artifacts) · `SIGNAL.md` (split / load frequency) · `AGENTS.md` (where things go).
