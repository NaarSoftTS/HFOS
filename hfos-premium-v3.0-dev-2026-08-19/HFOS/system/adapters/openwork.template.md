# Adapter template — OpenWork

_Copy to delivered `system/adapters/openwork.md` on first real OpenWork install. Replace placeholders. Five mappings only._

_OpenWork surfaces evolve — fill from the product's actual project/rules/entry behavior; do not invent a sixth mapping._

---

## 1 · Entry

| | |
|---|---|
| **File this runtime reads first** | `{{ENTRY_FILE}}` — prefer `AGENTS.md` if supported; else project rules file that points at `AGENTS.md` |
| **How it reaches the kernel** | `{{ENTRY_MECHANISM}}` — must end in loading `AGENTS.md` prose without proprietary-only import syntax as the sole path |
| **Session workdir** | `{{TREE_ROOT}}` |
| **Project / workspace binding** | `{{PROJECT_BINDING_NOTES}}` |

## 2 · Schedule

| | |
|---|---|
| **Store** | `{{SCHEDULE_STORE}}` |
| **Definition of record** | Tree `system/automations/<task>.md` |
| **Pointer pattern** | Job launches with workdir = tree root and a stub that reads the RUNBOOK; fail closed |
| **If unsupported** | Declare: on-demand loops only |

## 3 · Connectors

| Capability | OpenWork mapping | Status |
|---|---|---|
| Mail | `{{MAIL_CONNECTOR}}` | |
| Calendar | `{{CALENDAR_CONNECTOR}}` | |
| Task system | `{{TASK_CONNECTOR}}` | |
| Files | `{{FILES_CONNECTOR}}` | |

## 4 · Paths

| Logical | Absolute on this install |
|---|---|
| Tree root | `{{TREE_ROOT}}` |
| `@resources` | `{{RESOURCES}}` |
| `@dev` | `{{DEV}}` |
| `@coms` | `{{COMS}}` |
| `@publish` | `{{PUBLISH}}` |

## 5 · Gates

| Gate | Enforced by harness? | Notes |
|---|---|---|
| Send / publish / spend / commit-in-name | `{{…}}` | State gaps honestly |
| Foundations writes | Instruction + human | |
| Git writes | Instruction for loops | |

---

## ACTIVE

When this install is primary: write `openwork` into `system/adapters/ACTIVE`.

## First-install checklist

1. Confirm which file OpenWork injects from the project root.
2. Ensure `AGENTS.md` is sufficient without Cowork-only `@./` imports.
3. Smoke: kernel load → `python system/tools/path.py stores` → one manual loop dry-run.
4. Promote durable OpenWork lessons back to this template in the builder.
