# The Harness Contract

_JIT — porting or adapter work. What any runtime must provide. One page._

---

## The claim it makes precise

The OS is written against a **harness**: the runtime that gives a model file access, a shell, scheduled execution, and connectors. Cowork is one harness. Codex is another. **The OS should not know which one it is running on.**

Everything host-specific belongs in an **adapter** — one small file per harness in `system/adapters/`. Everything else is portable by construction. Where the OS reaches a host detail directly, that is a defect with a name.

---

## The five capabilities

A harness must provide all five. Anything less and the OS runs degraded **in a stated way, never silently.**

**1 · File I/O over a single tree.** Read, write, create, move, and delete inside one root, with paths stable between runs. The OS addresses everything by tree-relative path. *Not required:* version control, sync, file watching.

**2 · Shell.** Run scripts and read their output. This is what makes the judgment line possible — `system/tools/` does the mechanics, the model judges. A harness without a shell forces mechanics back into prompts, where they are expensive and unverifiable.

**3 · Scheduled execution that resolves pointers.** Fire a named task on a cron-like schedule, where the task's instructions are **a pointer into the tree, not a stored copy.** This is the hardest requirement and the one most likely to be missing. Where a harness can only store an inline prompt, the adapter's job is to make that prompt a pointer — a short stub that reads its real instructions from the tree, carries the hard rules inline as a safety floor, and **fails closed.**

**4 · Connectors, named indirectly.** Access to mail, calendar, task systems, and similar. **The OS must never hard-code a connector ID.** It asks for a capability — *the calendar*, *the task system* — and the adapter maps capability to whatever this harness calls it. A missing capability is a declared coverage gap, never an error and never an inference.

**5 · Permission gates.** The harness must be able to stop an action rather than trust a prompt not to take it. Send, publish, spend, commit, change direction, and foundations writes are gates. **A prompt is not a permission system** — where a harness cannot enforce, the adapter states that plainly and the person carries the gate manually.

---

## What the adapter owns

One file per harness, and only these five mappings:

| Mapping | Question it answers |
|---|---|
| **Entry** | Which filename does this runtime read first, and how does it reach `AGENTS.md`? |
| **Schedule** | Where do scheduled tasks live, how is one created, and how does it point rather than copy? |
| **Connectors** | What is this harness's name for each capability the OS asks for? |
| **Paths** | What is the tree's absolute root here, where are the external stores, and are there read-only regions? |
| **Gates** | Which parts of the two gates (`AGENTS.md`, Boundaries) can this harness actually *enforce*, and which are carried by instruction? |

**Nothing else.** A sixth section means either the contract is missing a capability or personalization has leaked into the harness layer — check which before adding it.

_Permission gates are capability 5 above: a harness that cannot enforce a gate must say so where a reader will look._

---

## Adapter templates (builder ships these)

| Harness | Entry | Template in delivered tree |
|---|---|---|
| **Hermes Agent** | `AGENTS.md` (native) | `system/adapters/hermes.md` ← `_engine/adapters/hermes.template.md` |
| **Cowork / Claude Code** | `CLAUDE.md` → `AGENTS.md` | `cowork.template.md` |
| **OpenWork** | project entry → `AGENTS.md` | `openwork.template.md` (fill on first real install) |
| **Generic AGENTS-first** (Codex, Cursor-class, …) | `AGENTS.md` / rules pointer | `generic.template.md` |
| **Self-contained install** | per host | Same adapters; `@resources` `@dev` `@coms` `@publish` point at local folders |

**Filled adapters are written when a real install commits.** Templates ship; guessed host paths do not. A missing capability is a **declared degradation**, never silent.

---

## Violations — the honest list

| # | Violation | Status |
|---|---|---|
| 1 | Connector registry recorded MCP connector UUIDs directly | **Closed** — capability names in `system/adapters/connections.md`, IDs in the adapter |
| 2 | Root entry used `@./file.md` import syntax, a Claude-family feature | **Closed** — `AGENTS.md` states its load order in prose any runtime can follow |
| 3 | Prompts and playbooks carried absolute `/Users/...` paths | **Closed by construction** — logical store names in the tree, absolute roots only in the adapter. Enforced by `system/tools/check-paths.py` |
| 4 | Scheduled-task registry documented one harness's store as if universal | **Closed** — `system/automations/` describes tasks; the adapter describes where they live |
| 5 | A harness artifact directory sits inside the tree | **Accepted, with a rule.** It is where this harness keeps its tasks, it is read-only to agents, and it is neither engine nor operator data. It stays at root as harness territory and is excluded from every scan |

---

## The test

**Could a competent operator on an unsupported runtime read this page, write five mappings, and have the OS run?** If not, the missing thing belongs in the capability list above — not discovered later inside a build.
