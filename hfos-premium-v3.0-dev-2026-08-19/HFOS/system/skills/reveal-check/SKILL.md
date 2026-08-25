# Skill — Reveal Check (the ship gate)

_Run before anything leaves the system: an email, a post, a document for a client, a shared file. This is `system/core/DISCLOSURE.md` §reveal-filter made procedural. Two minutes; it has one job — **nothing above the audience's line leaves.**_

## When it runs

Every outbound draft, automatically as the last step before handing the person the final version. The person can also invoke it directly: **"reveal-check this."** Skipping it is allowed only by the person's explicit say-so, never by the session's convenience.

## The procedure

1. **Name the audience.** Recipient(s) and channel, concretely — "Sarah at Acme, email," not "external." If the audience can't be named, the draft isn't ready to leave.
2. **Walk the draft fact by fact.** For each fact, figure, name, or quote: what is its classification (its source's, or its container's default — untagged = INTERNAL)?
3. **Apply the line:** PUBLIC passes anywhere · SHARED passes only to its named audience · **INTERNAL and RESTRICTED never appear** — they may have informed the reasoning; they do not appear in the text.
4. **Third parties get their own check:** a fact *about* someone other than the recipient (another client's name, a partner's numbers, anything from `relationships/people/` or `life/`) passes only if the person has cleared it for this audience before. When in doubt, it stays out.
5. **Violation → HOLD, not a silent trim.** Name the sentence and its source classification; propose the revealable version; the person decides. Silent removal teaches the person the check does nothing.
6. **Downgrade honestly.** If the output legitimately carries a lower classification than its sources (a public post reasoned from internal material), passing this check *is* the sanitization; note `derived-from::` on the kept copy.

## What this skill never does

Never blocks the person overriding it (their call, stated) · never classifies new material itself beyond container defaults — it flags, the person decides escalations · never reads `life/` or person files *into* a draft to "be helpful"; those enter drafts only by the person's explicit act.

## Mechanical companion

If the tools are available: `python system/tools/classification-lint.py` keeps tags well-formed so this check has clean inputs. The lint checks form; **this skill checks judgment.**
