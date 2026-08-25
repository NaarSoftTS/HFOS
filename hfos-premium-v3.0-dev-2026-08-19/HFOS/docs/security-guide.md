# Security guide

_The posture in plain language. This system is powerful because it can act; it is safe because of where it is built to stop._

## The two gates

1. **Nothing leaves without you.** No send, publish, spend, or commit in your name without your explicit act. The AI prepares; you release.
2. **Your compass is yours.** `foundations/` changes only when you say so.

Your AI apps may technically be *able* to send once you connect mail or other tools — the gates are carried by the system's instructions and by you. That honesty matters: keep yourself at the gate, and treat any drift (the system sending without asking) as a defect to fix immediately, not a convenience.

## Fail closed

A missing file, an unreachable folder, an unresolvable instruction — the system says so and stops. It never improvises a substitute procedure, never invents what a missing document probably said, and never reports work as done when its artifact didn't land.

## Secrets stay out of the tree

Passwords, API keys, tokens, account numbers: **never** in these files, never pasted into chat. They live in your password manager and your apps' own secure storage. If a secret ever lands in the tree, treat it as exposed: rotate it, then delete the file content.

## What not to load

- Plugins/bundles you haven't reviewed — especially anything that can send, post, or spend
- Anything granting an automation the power to act as you without a gate
- Bulk personal data of *other* people (clients, contacts) without deciding where it lives and who may see it first (see `classification-guide.md`)
- Hype-driven "auto-pilot" workflows — a system acting on your reputation should be boringly conservative

## Sensible defaults this box ships with

No connectors at install · no schedules at install · every capability gap named in `system/adapters/connections.md` rather than assumed · `life/` and person files outside any shareable surface by construction · classification defaults to INTERNAL, so an unlabeled file cannot leave.

## Back it up

Your whole operation ends up in this folder — treat it accordingly. Put the tree somewhere continuously backed up (iCloud, Dropbox, OneDrive) **or** make it a git repository and commit weekly; either is fine, having neither is the one genuinely dangerous configuration. The `resources/` folder beside it deserves the same.

## Your responsibility (plainly)

This is a template that directs AI systems running under your accounts. AI can misread, err, and act with real consequences. We ship strong defaults and honest gates; **operating the system, reviewing its outputs, and everything released through it remains yours.**
