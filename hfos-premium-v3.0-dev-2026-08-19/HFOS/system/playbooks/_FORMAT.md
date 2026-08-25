# Playbook format — HFOS-compressed + selective tags

_Internal standard. Not loaded in normal work._

## What a playbook is

Guidance a practitioner applies with judgment. **Not** a skill (skills are step-by-step). **Not** agent WISDOM (WISDOM loads with the role and holds the cross-cut synthesis). A playbook loads **only** when its trigger matches.

## Shape (hard)

```
<when>one line — the whole interface; include spoken trigger phrases people still use</when>
<paired_skill>path(s) or none</paired_skill>

# Job-named title

<principle>
One binding claim.
</principle>

<rules>
Numbered operating rules. No pedagogy. No case studies. No "why it works."
</rules>

<checks>
Diagnostic questions / pass-fail rows the agent runs on the work.
</checks>

<moves>
What to produce or change when the checks fail. Tables OK when verdicts are discrete.
</moves>

<refuse>
Anti-patterns. Hard stops for this discipline + flourishing bounds (owner's `foundations/`) where relevant.
</refuse>
```

Ceilings: **main file ≤ 80 lines / ~4KB**. No `references/`. No source/book headers in the body. No parallel "alias path" names — **one canonical path per pack.** Attribution lives in `system/ACKNOWLEDGEMENTS.md` only.

## Why tags here

Per `system/core/SIGNAL.md` → `<format_rules>`: **tags only where they earn it** — when instructions reference blocks, or structure strengthens use. Playbook sections are always the same five blocks an agent walks in order; tags make those blocks addressable without competing with markdown headings for the job title. Tags need not validate; md stays readable.

**Do not tag** inside rules/checks content unless a nested block is itself a referenced unit. A tag that structures nothing is noise.

## Naming

Name the **job**, not the book. `customer-discovery.md`, not `mom-test.md`. Put old book words only inside `<when>` as spoken triggers so routing still fires — never as a second filename.

## Combine rule

Merge frameworks that share one decision. Split only when load contexts diverge (different agent, different trigger, different paired skill).

## What was stripped

- Case studies and story teaching
- Copy-pattern catalogs (unless the playbook *is* messaging)
- Stage day-plans and ceremony names
- Scoring rubrics padded for humans — keep a short check list instead
- Clever wordgrams that don't change the decision
- Dual naming / alias tables as a routing system
- Book-titled folders and `references/` trees (archived under `_archive/book-form-*`)

## Practice-area exception

`content-production/` and some system protocols predate this shape and may still use longer multi-section forms. Convert opportunistically when touched; do not mass-rewrite. New role packs **must** use this shape.
