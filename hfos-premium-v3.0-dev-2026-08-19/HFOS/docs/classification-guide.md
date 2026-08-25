# What it knows vs. what it may say

_Your OS holds things that must never surface in the wrong place — client terms, pricing, personal notes. This guide is the plain-language version; the doctrine your agent follows is `system/core/DISCLOSURE.md`._

## Four words

Everything in the system belongs to the **widest audience that may safely see it**:

- **PUBLIC** — could go on your website
- **SHARED** — cleared for named outside people ("okay for *this* client")
- **INTERNAL** — fine inside your operation, not outside. **The default: everything untagged is INTERNAL**
- **RESTRICTED** — need-to-know even inside (deal terms, personal matters, legal)

You almost never label anything. Untagged means INTERNAL, and INTERNAL already cannot leave — so the boundary is safe *without* you doing classification homework. You add a tag only when something differs from its surroundings: a public one-pager inside a workspace, a file cleared for one partner.

## The clever part: reason vs. reveal

Hard walls would make your system stupid — it couldn't use what it knows to help you. So the rule is: **the OS may *think* with everything you've authorized it to know, and may *say* only what the recipient is cleared to hear.** Drafting a delay email to a client, it can reason over your internal project mess and reveal none of it. Like a trusted executive: knows the whole picture, says the appropriate portion.

Before anything leaves — email, post, document — the **reveal check** runs (`system/skills/reveal-check/`): the system names the audience and checks every fact against that audience's line. A violation stops the draft and tells you which sentence crossed; it never silently trims.

And the line moves **both directions, always by your act**: escalate something to RESTRICTED when it earns need-to-know protection, or open it to a named partner (SHARED) or the world (PUBLIC) — each downward move is a recorded clearance, so you always know who opened what, and when.

## Two things are locked by construction

`life/` and your person files are yours alone — never part of anything shared, no tag needed. And **secrets (passwords, keys) don't get classified because they never enter the system at all** — see `security-guide.md`.

## When you share a workspace (later, Team)

Classification is what makes multiplayer safe: the workspace is the shared surface, and everything outside it simply isn't there for the other person. You'll never need to remember what's visible — the rooms already decided.
