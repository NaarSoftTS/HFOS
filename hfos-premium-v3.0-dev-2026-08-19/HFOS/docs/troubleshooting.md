# Troubleshooting & FAQ

_When something feels off, in order._

## Orientation feels wrong ("it doesn't know me")

Say exactly what's missing in-session. The fix is almost always the compass card (`foundations/SUMMARY.md`) being thin — a deepening sitting with the coach beats any amount of re-explaining. If you're pasting context every session, that *is* the defect; make the OS write it down where it belongs.

## The agent invents things

It shouldn't — "never invent" is doctrine. When it happens: point at the invented item and say "where did this come from?" The answer locates the broken file. Facts about you belong in foundations or the owning workspace; if they're nowhere, the honest answer was "I don't know," and the OS should be told so.

## It did something without asking

Gate violation — treat seriously. Tell it: "You released X without me. Log it, and state which instruction failed." Then check the fix landed in the file it names. The gates are the system's spine; drift gets corrected immediately, not tolerated.

## A tool/script errors

The tools need Python 3 available in your agent app's environment. No Python? Everything still works — the tools are measurements, not the brain; the OS just measures by reading instead. A traceback is worth reporting to the community; exit code 1 with findings is *normal* (findings are a signal, not an error).

## "It says a folder/store is unreachable"

Honest by design. `../resources/` not created yet (INSTALL step 1), or a connector not actually connected (`system/adapters/connections.md` is the truth register). Create/connect it, or leave the gap named — the system works around named gaps; it only breaks on pretended coverage.

## It feels heavy / too much structure

The right move is usually **less**. "This feels heavy — compress it" is a legitimate instruction the OS knows how to follow. Empty rooms cost nothing; delete nothing in `system/` without asking what it does first.

## FAQ

**Do I need the membership for the system to work?** No. It's yours forever, fully functional. Membership carries upgrades, the Academy, and the community.
**Can I move it to another computer / AI app?** Yes — it's a folder. Copy it, update `system/adapters/` per the README there, done.
**Can I use it for a client's business?** Your license covers you and your own organizations — a client needs their own copy. Partner options exist; ask.
**Where's my data?** In the folder. All of it. Nowhere else.
