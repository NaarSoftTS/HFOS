# Upgrade guide — receiving packets

_Premium capability. A packet is a small markdown file carrying one improvement, written so **your own system** can merge it intelligently — no installer, no control plane, nothing phones home._

## How it works

1. A packet arrives (from the membership's monthly update, or shared in the community).
2. Drop it in `inbox/` and say: **"Apply this upgrade packet."**
3. Your OS reads the packet's integration instructions and merges it: **keep what's yours, absorb what's new, flag anything that conflicts.**
4. It logs one line (what changed, why) so you can see every upgrade after the fact.

## The rules your system follows when merging

- **Already have something covering this?** The packet is an *upgrade* to yours, not a replacement — your additions and edits are preserved.
- **Nothing like it yet?** It's added new, following *your* structure's conventions — packets adapt to your tree, not the other way around.
- **Conflict with a choice you made?** Your version stays; the conflict is flagged to you with both versions visible. Nothing you decided is ever silently overwritten.
- **Terminology translates.** A packet's examples might use different workspace names than yours — your system translates the pattern, not the literal names.

## Trust, verified

After any packet: "What did that change?" gets you the exact list. Every merge is reviewable, and because packets are plain markdown, you can read one *before* applying it — they're short by design (one improvement each, readable in a sitting).

## If you've customized heavily

Good — that's the point of the system. Packets are written against patterns, not file paths, precisely so customized trees merge cleanly. If a packet ever lands wrong, say so: "undo that packet" works (the log is the undo map), and telling the community what happened improves the next one.

## If you cancel

Everything already merged stays yours forever. You stop receiving new packets; nothing installed ever deactivates.
