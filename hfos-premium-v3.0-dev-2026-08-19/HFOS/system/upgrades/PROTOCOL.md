# Upgrades — Counsel, Not Overwrite

**The whole Human Flourishing OS belongs to its owner, customizations included.**

That is not a courtesy. It is the design constraint every upgrade mechanism here answers to. An owner who has adapted an agent, sharpened a playbook, or built a skill for their own operation has made the system *theirs* — and an upgrade that silently reverts that work teaches them never to customize again. A system nobody dares modify is a system that stops fitting its owner within a year.

So upgrades are **applied by inference, never by overwrite.**

---

## What an upgrade packet contains

| File | Holds |
|---|---|
| `UPGRADE.md` | What this packet is for, in plain words, and who it's for |
| `MANIFEST.md` | Every file the packet touches, and how — add, merge, adapt, replace |
| `RATIONALE.md` | **Why each change exists.** The reasoning, not the changelog |
| `additions/` | New material — agents, skills, playbooks, tools |
| `migrations/` | Changes to material the instance already has |
| `EVALUATIONS.md` | How to tell whether the change actually helped, after it lands |
| `ROLLBACK.md` | How to undo it |

`RATIONALE.md` is the load-bearing one. **A packet that says what changed but not why cannot be applied intelligently** — the applying system has no basis on which to decide whether a local customization should survive the change or be replaced by it.

---

## How a packet is applied

The applying agent does this, in order:

1. **Inspect the local instance.** What exists, what has been customized, what the customization was evidently trying to achieve.
2. **Classify each change** in the manifest against what it finds:

| Verdict | When | What happens |
|---|---|---|
| **Add** | The instance doesn't have this | Land it |
| **Merge** | The instance has it, unmodified | Take the new version |
| **Adapt** | The instance has it, **customized** | Combine — keep the local intent, take the improvement. Explain what was kept and why |
| **Decline** | The change conflicts with a deliberate local decision | Don't apply it. **Record the decline and its reason** |

3. **Never touch** `foundations/`, `life/`, `relationships/`, `workspaces/`, `momentum/`, or `system/memory/`. No packet has any business in the owner's identity, their people, their work, or their history. This boundary has no exceptions.
4. **Record what happened** — every add, merge, adapt, and decline, with reasoning — in `system/upgrades/applied/YYYY-MM-DD-<packet>.md`.
5. **Run the evaluations** when enough time has passed to tell.

**Adapt is the interesting verdict and the whole reason this is inference rather than a patch tool.** A diff can tell you a file changed locally. Only reasoning can tell you whether the local change and the upstream change are pursuing the same goal — in which case they combine — or different ones, in which case the owner's goal wins and the decline gets recorded.

**When in doubt, decline and ask.** A declined change costs one conversation. A wrongly-merged change costs the owner's trust in the upgrade channel, which is far more expensive and much harder to notice.

---

## What packets are used for

**Capability packs.** *"I need a CFO"* is a folder drop — an agent plus its skills plus its wisdom. New skills delivered into agents the instance already has. A wisdom pack for a niche.

**Engine improvements.** A better runbook, a sharper tool, a corrected playbook.

**Niche editions.** A ministry build, a clinical build, a build for a particular trade — **the same core, plus a wisdom pack, plus an agent set.** Not a fork. The moment an edition forks, every improvement has to be made twice and one copy starts falling behind.

---

## Sending upgrades outward

This instance is also the one that *produces* packets for other installs. The same discipline applies in reverse:

- **A packet carries no personal data.** Not a name, not a workspace, not a number from this operation. A packet that leaks the author's context into someone else's system is a serious defect. `system/tools/check-paths.py` and a personal-data scan run before any packet ships.
- **A packet explains itself.** If `RATIONALE.md` can't say why a change matters to a recipient who has never met the author, the change isn't ready to send.
- **A packet is reversible.** `ROLLBACK.md` is written before the packet ships, not after someone needs it.

---

## Deferred

**An upgrade tool ships with the system later** — one that does the inspection, classification, and recording mechanically, so the applying agent judges rather than bookkeeps. Same judgment line as everywhere else. Until then this protocol is applied by reasoning, and the record in `applied/` is written by hand.
