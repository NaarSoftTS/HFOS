# Adapter template — generic AGENTS-first runtime

_For Codex, Cursor-class, or any runtime that can pin a project root and read `AGENTS.md` (or `.cursorrules` / equivalent that points at it). Copy to `system/adapters/{{HARNESS_ID}}.md`._

---

## 1 · Entry

| | |
|---|---|
| **Runtime name** | `{{HARNESS_ID}}` |
| **File read first** | `{{ENTRY_FILE}}` (ideal: `AGENTS.md`) |
| **Kernel path** | Always reach `AGENTS.md` in prose |
| **Session workdir** | `{{TREE_ROOT}}` |
| **Extra entry files** | Optional `.cursorrules` / `.codex` **pointers only** — do not fork kernel doctrine into them |

## 2 · Schedule

| | |
|---|---|
| **Store** | `{{SCHEDULE_STORE_OR_NONE}}` |
| **Pattern** | Pointer stub + workdir; or **declared** on-demand-only |
| **Definitions** | `system/automations/` in tree |

## 3 · Connectors

| Capability | Mapping | Status |
|---|---|---|
| Mail | `{{…}}` | |
| Calendar | `{{…}}` | |
| Task system | `{{…}}` | |
| Files | `{{…}}` | |

## 4 · Paths

| Logical | Absolute |
|---|---|
| Tree root | `{{TREE_ROOT}}` |
| `@resources` | `{{RESOURCES}}` |
| `@dev` | `{{DEV}}` |
| `@coms` | `{{COMS}}` |
| `@publish` | `{{PUBLISH}}` |

## 5 · Gates

State which gates the runtime can enforce vs instruction-only. Fail open on honesty: if it cannot block send/publish, say so.

---

## ACTIVE

Write `{{HARNESS_ID}}` into `system/adapters/ACTIVE` when primary.
