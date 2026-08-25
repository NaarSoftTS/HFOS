# Adapter — Claude Cowork / Claude Code (primary)

_Five mappings, nothing else — everything host-specific for this harness lives on this page. Filled at install by `INSTALL.md`; until then the honest state is "not yet set," never an invented path._

---

## 1 · Entry

| | |
|---|---|
| **File this runtime reads first** | `CLAUDE.md` — thin prose pointer → read `AGENTS.md` (the kernel) |
| **Session workdir** | the folder this tree was installed into (set at install — see `INSTALL.md`) |
| **Nested contexts** | None. The kernel routes; folders do not re-announce themselves |

## 2 · Schedule

| | |
|---|---|
| **Store** | Cowork scheduled tasks (if used). Definition of record stays `system/automations/<task>.md` in the tree; the host holds a pointer stub only |
| **Status** | **No schedules active at install.** Suggested: the **weekly keeper** (`system/automations/weekly-keeper.md`) · the morning brief after one manual run feels good (`START_HERE.md`) · monthly, together: `state-of-my-system` + `system-adaptation` (on ask, or scheduled once the rhythm feels right) |

## 3 · Connectors

Capabilities are declared in `connections.md`; this table names what this install has actually connected. **At install: nothing.** Add rows as you connect tools — a connector that lists is not a connector that works; the first real call is the verification.

| Capability | Connected as | Status |
|---|---|---|
| Mail | — | not connected |
| Calendar | — | not connected |
| Task system | — | not connected |
| Files / drive | — | not connected |

## 4 · Paths

**Self-contained install (default).** The tree root is the installed folder; everything is addressed tree-relative. External stores resolve to local folders beside the tree:

| Logical | Resolves to | Notes |
|---|---|---|
| `@resources` | `../resources` | created by INSTALL step 1 — bulk sources + exports shelf |

Ship shelf: `@resources/exports/<workspace>/`.

No other absolute paths belong anywhere in the tree. If you later move stores to cloud storage, change **only** this table.

## 5 · Gates — what this harness can and cannot enforce

The two gates (kernel): **nothing leaves without you** · **the compass is yours.**

| Gate | Enforced by the harness? |
|---|---|
| Send / publish / spend / commit | **Mostly no** — once connectors exist, many can act. The gate is carried by instruction: the AI prepares, you release |
| Foundations changes | **No** — carried by instruction; write only on your explicit act |

This honesty is the point: the system fails closed by discipline, and you stay at every gate.
