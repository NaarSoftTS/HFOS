# Adapter template — Hermes Agent

_Copy to delivered `system/adapters/hermes.md`. Replace all `{{PLACEHOLDERS}}`. Five mappings only._

---

## 1 · Entry

| | |
|---|---|
| **File this runtime reads first** | `AGENTS.md` (native — cwd only) |
| **How it reaches the kernel** | Session **workdir** = tree root. Hermes injects `AGENTS.md` automatically. No import directive required |
| **Nested contexts** | None required. Kernel routes |
| **Session workdir** | `{{TREE_ROOT}}` |
| **Profile (optional)** | `{{HERMES_PROFILE}}` — isolated memory/cron when used |

Interactive: open Project / CLI with primary folder = tree root.  
Task-level packages: workdir = package `system/` (or package root if that holds `AGENTS.md`).

## 2 · Schedule

| | |
|---|---|
| **Store** | Hermes durable cron under the active profile (`hermes cron` / in-session `cronjob`) — **outside** the tree |
| **Definition of record** | `system/automations/<task>.md` |
| **Job prompt** | **Pointer stub only** — read `system/loops/<loop>/RUNBOOK.md`; fail closed; hard rules inline; never `[SILENT]` for OS loops |
| **workdir on each job** | `{{TREE_ROOT}}` (only host-absolute field) |

Do not install full overnight chains on first boot — canary one loop, then expand.

## 3 · Connectors

Map **capabilities** → this harness's names. IDs never appear outside this adapter.

| Capability | Hermes / this install mapping | Status |
|---|---|---|
| Mail | `{{MAIL_CONNECTOR}}` | `{{connect-now \| hold + reason}}` |
| Calendar | `{{CALENDAR_CONNECTOR}}` | |
| Task system | `{{TASK_CONNECTOR}}` | |
| Files / drive | `{{FILES_CONNECTOR}}` | |

Missing capability = named gap in output; do not invent coverage.

## 4 · Paths

| Logical | Absolute on this install |
|---|---|
| Tree root | `{{TREE_ROOT}}` |
| `@resources` | `{{RESOURCES}}` |
| `@dev` | `{{DEV}}` |
| `@coms` | `{{COMS}}` |
| `@publish` | `{{PUBLISH}}` |

Self-contained install: point all four stores at folders inside or beside the tree.

## 5 · Gates

| Gate | Enforced by harness? | Notes |
|---|---|---|
| Send / publish / spend / commit-in-name | `{{yes partial / no — instruction only}}` | Prompt is not a permission system |
| Foundations / compass writes | Instruction + review | Require explicit human ask |
| Git writes | Instruction: loops never git-write | |

State honestly what the harness cannot enforce — the person carries those gates.

---

## ACTIVE

When this install is primary: write `hermes` into `system/adapters/ACTIVE`.
