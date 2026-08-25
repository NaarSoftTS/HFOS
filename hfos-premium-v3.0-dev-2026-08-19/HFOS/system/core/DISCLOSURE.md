# Disclosure — what this OS knows vs. what it may say

_JIT — load when drafting anything that leaves the system, or when classifying material. The one-page doctrine; the plain-language version is `docs/classification-guide.md`._

## The one question

Classification answers exactly one question: **what is the widest audience this information may safely be shared with?** Audience, not importance — a strategic plan is usually just INTERNAL.

## Four words

| Class | Meaning | Human test |
|---|---|---|
| **PUBLIC** | Anyone may see it | "Could this go on the website?" |
| **SHARED** | Named outside parties may see it (`audience::` names them) | "Okay for *this* partner?" |
| **INTERNAL** | The operation only — **the default** | "Fine inside, not outside?" |
| **RESTRICTED** | Specific people only (`audience::` names them) | "Need-to-know even inside?" |

**The decision tree:** anyone may see it → PUBLIC · intended for approved outsiders → SHARED + audience · the operation may see it → INTERNAL · otherwise → RESTRICTED + audience.

**Anti-inflation (hard):** classify by largest safe audience, never by how important it feels. RESTRICTED needs a concrete need-to-know reason (deal terms, personal/HR, privileged legal, client pricing, care material). If everything is restricted, nothing is.

**Secrets are outside the system entirely.** Passwords, keys, tokens, credentials never enter the tree or the AI's context — they live in your harness/password manager only.

## Reason vs. reveal — the rule that keeps the system smart

> **Authorized information may be used to reason. Only audience-authorized information may be revealed.**

Drafting a client email may legitimately *reason over* INTERNAL project status — and *reveal* only what that client is cleared to see. No hard silos (they make the system stupid); the reveal filter sits at the boundary.

**The reveal filter, before anything leaves:** (1) name the audience · (2) every fact revealed must be classified at-or-below that audience — INTERNAL and RESTRICTED inform the draft, they never appear in it · (3) a violation is a HOLD naming the section, not a silent trim. **Procedure: `system/skills/reveal-check/` — runs as the last step of every outbound draft.**

## Inheritance — 90% never needs a decision

Classification inherits from the container: a workspace or file gets a `classification::` (+ `audience::`) marking **only when it differs** from its surroundings. Untagged = INTERNAL — which already sits above the disclosure line, so an unclassified file still cannot leave. The boundary fails closed without a tagging tax inside.

`life/` and `relationships/people/` are effectively RESTRICTED-to-you by construction — never part of any shared surface.

## Moving something up or down

Everything starts INTERNAL by default. The person may **escalate** a thing to RESTRICTED (+ who may know it) when it earns need-to-know protection, or **open it downward** — SHARED with a named partner, or PUBLIC — and every downward move is a clearance record: who cleared it, when. The system proposes; the person moves the line.

## Outputs

An output takes the classification of what it actually contains, with `derived-from::` remembering its sources. Lowering classification (a public post reasoned from internal material) requires the reveal filter to have passed — that pass *is* the sanitization check.

**Who may *know* (vs. hear): `system/core/AUTHORIZATION.md`** — one page now, the extension point for shared workspaces later.
