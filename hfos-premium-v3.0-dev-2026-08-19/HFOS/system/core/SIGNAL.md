# Signal — The Write Discipline

_JIT write gate. Loading: `AGENTS.md` + `INDEX.md`. Ceilings/shapes: `STRUCTURE.md`. Default: **do not write**._

<instructions>
Before writing anything persistent, run <materiality_test>. What passes, classify per <classification>, then write per <write_rules> in the style of <format_rules>, split per <split_rule>. The memory model behind all of this: <memory_layers>. Default action at every step: **do not write.**
</instructions>

---

<materiality_test>

Information must touch at least one, in some active scope:

1. **Values** — expresses or tests a core value (`foundations/`)
2. **Objectives / outcomes** — changes, clarifies, advances, blocks, or redefines an objective or the outcome it points at — named or derivable
3. **Relationships** — materially shifts a key relationship or connector's state

Plus the local test: the owning context's `<signals>` block (its ANCHOR — `STRUCTURE.md`). `Material if` rules admit; `Ignore:` rules discard fast.

- No hit anywhere → discard, or one-line pointer max
- **The delta test is the cheapest form of this gate**: if it changes nothing a truth file currently asserts, it is noise by definition

</materiality_test>

<classification>

- **Signal** — compress gently, keep nuance + attribution: direction-changing decisions · facts that alter objectives/strategy/relationship state · material blockers, opportunities, risks · insight that shifts understanding · relationship health changes · anything that changes what a truth file asserts
- **Context** — compress hard: what's needed to interpret the signal correctly later · secondary facts · themes already captured once
- **Noise** — discard: logistics without state impact · restatements of what truth files already hold · anything useful only for replaying the event

Expected distribution: noise ≫ context ≫ signal. Signal is rare; treat it with care.

</classification>

<write_rules>

- **Scope first, classify second** — name the owning unit (person / workspace / project / relationship) before writing anything, then confirm the container's classification default fits (`DISCLOSURE.md`; untagged = internal). Never dump workspace material into the root
- **Primary write = the owning context's truth file** (`STATE.md`), update-in-place. One authoritative statement; retire variants. Rewrite only on delta
- **Secondary write = sparse log line**: date · 1-line gist · truth files touched · source pointer
- **Lowest owning level**; promote upward only the distilled signal that affects the parent
- **New file only when**: coherent new unit + parent would become mixed-purpose + will be loaded independently. **This gate is unit-level.** Splitting *depth* out of a unit that already exists is governed by `<split_rule>`, not by this bullet — a branch is a second layer, not a second unit
- **Teleology inherits**: a project without its own heart material inherits the workspace's FOUNDATIONS — empty is correct, not a gap. It earns its own ANCHOR as it matures (own DECISIONS/PEOPLE/identity). Heart material discovered *inside* a project is important — record it in the face file, never leave it orphaned in a capture
- **End-of-run consolidation**: a run may JIT-expand working memory freely; by run end, anything worth keeping consolidates into the owning `STATE.md` or a `WORKING.md` chunk. Temporary context never becomes permanent by inertia
- Provenance kept only where trust or accountability depends on it

</write_rules>

<split_rule>

**Load frequency is a write decision.** Before adding to a file that loads by default, ask what share of that file's loads actually need this material. What isn't needed on every load does not belong in the file that loads every time — it belongs one pointer away, fetched just-in-time.

- **Branch by default.** If it can be branched out, branch it. The parent keeps the fact, the rule, and the belief in its compressed form; the branch keeps the reasoning underneath it. Depth is the thing that branches
- **A pointer names a trigger, not just a file.** `x → read this file` is half a pointer. Name the condition that should make a reader open it — *load when the question turns on why* — or it will never be opened at the moment it was needed
- **Source material is not brain.** Undigested dumps, full texts, course bodies, transcripts → `@resources` with a `kind:: source` pointer whose load gate is *only when processing that source* (`COMPANION-STORE.md`). Never ambient with face/judgment loads
- **The exception is pointer weight.** Do not branch what the pointer would cost more than. A few sentences stay where they are; a split earns its keep only when the branch is meaningfully larger than the line that reaches it. A tree of files nobody opens is its own failure mode, and churn without a read is noise (`<format_rules>`)
- **Where an ask ledger exists** (system adaptation installed), splits are designed from the task profile — observed class×subject triggers beat guessed ones, and destination follows the use's home level
- **Guardrails never branch.** Hard rules, prohibitions, thresholds, escalation conditions, and the boundaries stay in the always-loaded file — anything a reader must not miss for want of a second read. Depth branches; what stops harm does not
- **Compression order:** branch first, squeeze second. Tightening prose that shouldn't be in the hot file at all is the expensive way to save bytes, and it is what costs nuance. **A branch does not clear a breach by itself** — `check-ceilings.py` measures the file as it stands, so a file still over after branching is still a breach

Reconciles with `<write_rules>` → *new file only when*: that rule guards against fragmenting **units**; this one governs splitting **depth** out of a unit that already exists. A branch is a second layer of the same unit, not a second unit — it inherits the parent's scope and is named from it.

</split_rule>

<memory_layers>

| Human layer | HFOS layer | Discipline |
|---|---|---|
| Sensory register — attention discards ~99% | `inbox/` | Discard-by-default; the materiality test is attention. Unattended → `_processed/` then cold → `@resources/_system/backup/` (not permanent brain weight) |
| Working memory — few chunks, forced eviction | each session's JIT-loaded set (+ `system/memory/WORKING.md` when overnight loops are installed) | Hard cap **10 chunks / 8KB**, soft 5–7. Chunk = 1–3 lines state · owning-context pointer · eviction path · date — no chunk without all four. Sections `Focus / Active / Awaiting consolidation` carry priority. 7-day TTL: promote or archive, "still here" is not an option |
| Long-term — semantic + episodic, reconstructive | Semantic = `FOUNDATIONS.md` + `STATE.md` (current truth) · Episodic = `DECISIONS.md` + `TIMELINE.md` + archives | Encode only on delta. `TIMELINE.md` = date + 1-line gist + source pointer (2 lines only for high-value decisions). Gist + pointer, never a recording |
| Sleep consolidation, pruning | Overnight/weekly review rhythm (when installed; else a manual weekly pass) | `WORKING.md` first each night: promote or decay; report chunk count + oldest age |

</memory_layers>

<format_rules>

- **Tags only where they earn it**: when instructions reference blocks, or hierarchy/pointer structure strengthens how content gets used. A tag that structures nothing is itself noise. Tags need not validate; md stays readable
- Bullets over prose wherever structure carries the meaning; no complete sentences owed
- Facts + pointers; adjectives and restatement are noise
- Conversion is **opportunistic**: any loop or session touching a file leaves it in this shape. No mass rewrites — churn without a read is noise too

- **Docs carry truth; the changelog carries history.** No dated change annotations inside foundational or doctrine docs — a date in the doc adds weight, not value. What changed, why, and when lives in `foundations/CHANGELOG.md` (created on the first foundations change; newest first: what changed · why · on whose act). Logs are the exception — `DECISIONS.md` and `TIMELINE.md` keep their dates; dating is their nature

</format_rules>

---

**Boundaries unchanged.** This gate filters volume, never authority: the two hard gates (`AGENTS.md`), the foundations write-lock, and the care-material rule sit above it. When materiality is genuinely unclear, that is a question for the dispatch — classification is judgment, and gray area is never silently discarded.

**And one question runs the opposite direction — *what should not become memory?*** Sensitivity gates before materiality: venting, half-formed views, another person's private circumstances, care material drifting toward pipeline. The write is declined even when material, and **no index is kept of what was declined** — a list of deliberately-forgotten things defeats the forgetting.
