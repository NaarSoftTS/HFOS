# Authority — how much autonomy an action gets

_JIT — load when designing or reviewing anything that acts (loop, skill, agent), or when a session is unsure whether to act or ask. This page explains the gates; it never softens them. What the harness actually enforces lives in `system/adapters/`. Sibling page: `AUTHORIZATION.md` decides who may **know**; this page decides when to **act vs ask**._

## The rule

**Authority is set by consequence × reversibility × confidence.** Human-in-the-loop is not human-in-every-loop: an assistant that asks permission to move a file has not been made safe, it has been made useless, and the person stops reading the prompts. Ask where asking protects something real; act where acting is contained.

## The rungs

| Rung | Scope | Examples |
|---|---|---|
| **Autonomous** | Low consequence, reversible, contained | Reads · file moves inside the tree · formatting · staging drafts |
| **Supervised** | Material but recoverable — act, then show | STATE updates · routing captures · run reports. The evidence trail is the supervision |
| **Approval required** | Commitments, publication, money, anything leaving | = **Gate 1**: no send, publish, spend, or commit in the person's name |
| **Human only** | Values, direction, irreversible choices | = **Gate 2**: `foundations/` · direction · anything without an undo — including everything on the person's own human-only list (`foundations/boundaries.md`) |

## The climb rule

**Unclear consequence climbs, never descends.** Can't tell which rung an action sits on? Treat it as the higher one. Low confidence in your own read of the situation climbs one rung by itself. Nothing ever argues its way *down* a rung mid-run.

## What this page is not

- **Not a softening.** The gates are rungs three and four, hard as ever. A recommendation never silently becomes a decision, commitment, task, or memory.
- **Not enforcement.** Per-harness enforcement is stated honestly in the adapter — what the harness blocks, what is carried by instruction. A rung the harness cannot enforce is a stated limitation, never an assumed safety.
- **Not a scoring system.** No numbers, no threshold files. The three factors are judgment inputs, and `system/wisdom/CORE.md` still governs the judgment.
