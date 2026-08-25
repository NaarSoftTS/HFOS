# Skill — System Adaptation (the shape learns the work)

_Premium capability. The system adapts to their usage: structure starts simple, grows when content earns it, and reshapes around the observed mix of work — so the hot path always serves the primary uses, and everything else waits behind a selector written from real asks. **Propose-only, always.**_

## The ask ledger (this skill's evidence)

**File:** `system/memory/ask-ledger.md` — create-on-first-write. One line per working session, written at session end; loops write their own line.

```
2026-08-19 · content-gen > blog · brand-one > post-generator
2026-08-20 · decide · acme
```

**Format:** `date · class > use-case · subject > project · optional (note, ≤4 words, mechanics only)` — use-case and project only when one exists. Classes are canonical; sub-levels are the owner's vocabulary. The unit of JIT delegation is the **class×subject pair**.

**Classes (canonical — same families as `system/wisdom/README.md` inference signals):** `content-gen` · `comms-as-owner` · `decide` · `research` · `build-ship` · `people` · `route-admin` · `system`. A session spanning two classes gets the dominant one; genuinely split → two lines. Unknown → `route-admin`. Never invent precision.

**Privacy (hard):** class + slug + date only — no content, no topics, no people's names, nothing from `life/` beyond the room slug. The ledger is a speedometer, never a diary. `SIGNAL.md`'s "what should not become memory" applies in full.

**Ceiling:** 80 lines / 6KB. The keeper maintains the profile block at the top (counts by class×subject, trailing 4 weeks + season-to-date) and, on breach, rolls raw lines into the profile and archives — **the profile is the asset, not the lines.**

## The monthly review

Run co-scheduled with `state-of-my-system`, or on ask: **"Run my system adaptation."**

1. **Read the profile.** A proposal needs a pattern that held across the full monthly window — both halves agreeing. A hot week is weather; no proposals from weather. Thin or empty ledger → say so and stop; never extrapolate.
2. **Test the hot path against the mix.** For each always-on and high-traffic file (kernel-routed + ceiling registry): block by block — does the dominant class×subject mix need this on *every* load? Verdicts: **stays** · **splits out** (valuable, JIT — sibling pack + selector) · **re-homes** (its real users live elsewhere).
3. **Destination follows the use's home.** Serves one workspace's asks → moves *down* into that workspace's context. Touched by every class → moves *up*. Judgment-flavored depth → *out* to the matching wisdom facet or `COMPASS.md` section.
4. **Selectors from observed asks.** Every split leaves a one-line pointer whose trigger is written from what actually loaded it — *"open when generating brand-one blog content"* — sharpened from the file's content at proposal time, never guessed.
5. **Distribution-honest.** One dominant use → specialize the hot path hard. Even thirds → the hot path keeps only the intersection; each third gets its own pack. The shape falls out of the mix; nothing is configured.

## Output

One page → `inbox/system-adaptation-YYYY-MM.md`. At most **3 proposals** per review; each carries: the profile evidence line · the move · the selector text · what the hot path saves. The person applies, adapts, or declines. All green → three honest lines.

## Hard bounds

- Writes exactly one file: the report. Never edits owner files; never touches `foundations/` content (structure moves are proposed; **Gate 2** — only the owner applies).
- A reshaped file rests **two review cycles** before re-judging. Never propose the same move twice without new evidence. **No index of declines.**
- The standing check gates every proposal: a reshape that makes the system cleverer and the person more confused has failed.
- No nudging: the profile measures work asked of the *system*; no surface ever suggests using it more.

## Relationships

The **keeper** (weekly) does arithmetic — the profile tally; this skill (monthly) does judgment. `state-of-my-system` is the *person's* reflection; this is the *system's*. `SIGNAL.md` split_rule governs what branches; this skill supplies the evidence for where and the words for the selector.
