# adapters/ (templates for delivered systems)

**The only place host-specific detail is allowed in a delivered tree.**

Five mappings only — entry · schedule · connectors · paths · gates.  
Contract: `../core/HARNESS-CONTRACT.md` (and `../HARNESS-CONTRACT.md` pointer if present).

## Files to stamp

| File | Holds |
|---|---|
| `ACTIVE` | One word harness id for this install (`hermes` \| `cowork` \| `openwork` \| …) |
| `<harness>.md` | Filled from the matching `*.template.md` |
| `connections.md` | Capabilities (calendar, mail, tasks…) — **no** connector UUIDs |
| `README.md` | This orientation (copy from template README) |

## Templates in this folder

| Template | Use when |
|---|---|
| `hermes.template.md` | Hermes Agent |
| `cowork.md` *(filled — active on this install)* | Claude Cowork / Claude Code |
| `openwork.template.md` | OpenWork (fill gaps on first real install) |
| `generic.template.md` | Codex, Cursor-class, or unknown AGENTS-first runtime |

## Rules

1. **Placeholders** look like `{{TREE_ROOT}}`, `{{RESOURCES}}`, `{{HARNESS_ID}}` — replace before delivery; never leave `{{` in a shipped adapter.
2. **No bi-sync of ACTIVE** across machines (dual-machine: each install sets its own).
3. **Adapters are filled when a real install commits**, not with guessed paths.
4. Tools resolve harness via `HFOS_HARNESS` → `ACTIVE` → default (document default in delivered README; prefer explicit ACTIVE).
