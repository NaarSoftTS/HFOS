#!/usr/bin/env python3
"""Measure session-start files against their ceilings.

The script measures. The model decides what to compress. That split is the
judgment line: a model counting lines in a prompt is expensive, unverifiable,
and eventually wrong without saying so.

When a ceiling breaches, the fix is branching, compression, or archiving. Never raise it.

Usage:  check-ceilings.py [--file PATH --max N]
        check-ceilings.py --dir PATH [--pattern SUBSTRING] [--max N] [--json]
Exit:   0 all under, 1 one or more breached.

Repaired 2026-07-27 (pre-first-chain audit): `--file` without `--max` measured
against the generic default (150) instead of the file's configured ceiling, so
`--file momentum/NEEDS_ME.md` reported 40/150 while the registry says 40. A
per-file call now consults CEILINGS, then GLOB_CEILINGS, before the default —
the runbooks' `--file` invocations and the no-argument sweep now agree.

Extended 2026-07-31 (performance audit, operator instruction): ceilings now
bind in BYTES as well as lines. Line ceilings were being satisfied by 200+
character lines (BLOCKED.md: 67 lines, 15KB) — bytes are what a context window
actually pays. A file breaches when EITHER measure is over. The fix is branching, then
compression, then archiving to the file's `archive/` sibling — never raising.
(Rolling history to `archive/` is mechanical and may run FIRST where it clears the
breach on its own — `STRUCTURE.md` licenses that, and the sweep's RUNBOOK does it
in that order at §39/§40. The ordering above is about what to reach for when a
roll does not clear it, not a rule against rolling early.)
Branch first (`system/core/SIGNAL.md` -> split_rule): what this file's readers
do not need on EVERY load moves to a sibling behind a pointer naming the
trigger to open it; guardrails (prohibitions, thresholds, escalations) never
move, and neither does content the pointer would outweigh. Only what genuinely
belongs in the hot file gets squeezed. A branch does not clear a breach by
itself — this script measures the file as it stands.
"""
import sys, json, argparse, fnmatch, os
from _lib import ROOT, rel, paths_arg, SKIP_DIRS


def safe_glob(pattern):
    """ROOT.glob that survives cloud-synced filesystems.

    Dropbox/iCloud virtual mounts can present transient phantom entries
    (a half-removed `__pycache__` yielded OSError 35 mid-glob, 2026-08-19) —
    and pathlib.glob dies mid-iteration on the first stat error, taking the
    whole sweep with it. Walk instead: skip SKIP_DIRS by name, swallow
    per-entry OSErrors, match against the pattern. A phantom file costs one
    skipped entry, never the scan.
    """
    hits = []
    base = str(ROOT)
    for dirpath, dirnames, filenames in os.walk(base, onerror=lambda e: None):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            full = os.path.join(dirpath, name)
            r = os.path.relpath(full, base).replace(os.sep, "/")
            if fnmatch.fnmatch(r, pattern) or fnmatch.fnmatch(r, pattern.replace("**/", "")):
                try:
                    if os.path.isfile(full):
                        hits.append(ROOT / r)
                except OSError:
                    continue
    return sorted(hits)

CEILINGS = {
    "AGENTS.md": 100,
    "NOW.md": 60,
    "foundations/SUMMARY.md": 120,
    "foundations/COMPASS.md": 150,
    "foundations/voice.md": 80,
    "foundations/boundaries.md": 60,
    # Raised 40 → 60 by operator recalibration: the constraint had started
    # excluding real blockers while several list entries were not blockers.
    # "Never raise" governs loops, not the person. Entry count is the real
    # discipline; the line count follows it.
    "momentum/NEEDS_ME.md": 60,
    # Hot-path registry (2026-07-31): everything a loop's Load step reads every
    # run is ceiling-bearing, so the no-argument sweep measures it nightly.
    "momentum/BLOCKED.md": 80,
    "momentum/WAITING.md": 60,
    "momentum/COMMITMENTS.md": 60,
    # Simple shape (single-file momentum): one ledger file, all five sections.
    "momentum/MOMENTUM.md": 120,
    "system/loops/hero/state/build-ledger.md": 60,
    "system/loops/hero/state/backlog.md": 120,
    "system/loops/hero/state/objectives.md": 120,
    "system/memory/working-log.md": 200,
    # WORKING.md: the working-memory layer (SIGNAL.md). 10 chunks ≈ 3 lines
    # each + frame; the byte cap (8KB) is the binding constraint.
    "system/memory/WORKING.md": 60,
    "system/memory/ask-ledger.md": 80,
    "system/memory/findings-ledger.md": 100,
    # Judgment spine (JIT on judgment — still ceiling-bearing so growth is visible)
    "system/wisdom/CORE.md": 100,
    "system/wisdom/README.md": 120,
    # Operator 2026-08-01: coach WISDOM deliberately not distilled — instruments are exact phrasings
    "system/agents/coach/WISDOM.md": 80,
}
# Recursive: a group's member workspaces carry the same face, so they carry the
# same ceilings. The earlier top-level-only globs covered 10 of 34 face files.
GLOB_CEILINGS = [
    ("**/HOME.md", 80),
    ("**/STATE.md", 150),
    ("**/NEXT.md", 60),
    # Live agent faces — deep prose lives in references/AGENT-full.md
    ("system/agents/*/AGENT.md", 120),
    ("system/agents/*/WISDOM.md", 80),
    # Role job packs (_FORMAT.md): ≤80 lines / ~4KB. Practice areas exempt by path.
    ("system/playbooks/cso/*.md", 80),
    ("system/playbooks/cpo/*.md", 80),
    ("system/playbooks/cto/*.md", 80),
    ("system/playbooks/cxo/*.md", 80),
    ("system/playbooks/cmo/*.md", 80),
    ("system/playbooks/coo/*.md", 80),
    ("system/playbooks/cpoo/*.md", 80),
    ("system/playbooks/cio/*.md", 80),
    ("system/playbooks/shared/*.md", 80),
    ("system/wisdom/*.md", 80),
]

# Byte ceilings — the measure that binds (2026-07-31). Hot-path files first:
# everything a loop's Load step reads every run. A breach here is the nightly
# sweep's compression queue, oldest-history-first.
BYTE_CEILINGS = {
    "AGENTS.md": 8_000,
    "NOW.md": 6_000,
    "foundations/SUMMARY.md": 9_000,
    "foundations/COMPASS.md": 10_000,
    "foundations/voice.md": 6_000,
    "foundations/boundaries.md": 6_000,
    "momentum/NEEDS_ME.md": 8_000,
    "momentum/BLOCKED.md": 8_000,
    "momentum/WAITING.md": 6_000,
    "momentum/COMMITMENTS.md": 8_000,
    "momentum/MOMENTUM.md": 12_000,
    "system/loops/hero/state/build-ledger.md": 15_000,
    # Live findings only — open + recent closed. Archive the rest (operator 2026-08-03).
    "system/memory/findings-ledger.md": 12_000,
    "system/loops/hero/state/backlog.md": 15_000,
    "system/loops/hero/state/objectives.md": 10_000,
    "system/memory/working-log.md": 8_000,  # dropped 15K → 8K 2026-08-01: truth
    # lives in STATE files now; this is a sparse run log + day review only
    "system/memory/WORKING.md": 8_000,
    "system/memory/ask-ledger.md": 6_000,
    "system/wisdom/CORE.md": 6_000,
    "system/wisdom/README.md": 6_000,
    # Operator 2026-08-01: do not compress coach WISDOM; question phrasings are the tools
    "system/agents/coach/WISDOM.md": 12_000,
}
GLOB_BYTE_CEILINGS = [
    ("**/HOME.md", 8_000),
    ("**/STATE.md", 12_000),
    ("**/NEXT.md", 5_000),
    ("system/agents/*/AGENT.md", 12_000),
    ("system/agents/*/WISDOM.md", 6_000),
    ("system/playbooks/cso/*.md", 4_000),
    ("system/playbooks/cpo/*.md", 4_000),
    ("system/playbooks/cto/*.md", 4_000),
    ("system/playbooks/cxo/*.md", 4_000),
    ("system/playbooks/cmo/*.md", 4_000),
    ("system/playbooks/coo/*.md", 4_000),
    ("system/playbooks/cpoo/*.md", 4_000),
    ("system/playbooks/cio/*.md", 4_000),
    ("system/playbooks/shared/*.md", 4_000),
    ("system/wisdom/*.md", 6_000),
]
DEFAULT_BYTE_CEILING = 15_000

# Exempt: not loaded by default, and meant to grow. Added 2026-08-02, because
# `--dir` and `--file` scans did not know about the exemption the doctrine
# already granted: `--dir system/agents` reported ten BREACHes against the very
# `references/` files `STRUCTURE.md` names as exempt — and RUNBOOK §40 tells the
# loop reading that output to compress what it finds. A tool that contradicts
# the doctrine it enforces is the item-9 defect wearing different clothes.
#
# This list is `STRUCTURE.md` -> Ceilings -> Exempt plus the regions the
# no-argument scan already skipped, which are exempt for the same reason
# (not loaded, not this tree's live content) and are named here so one list
# governs every mode. The two sides were reconciled after an audit found them
# describing each other inaccurately in both directions.
#
# `references/` stands in for "branch sibling" wherever the convention is
# followed. A branch that lives elsewhere (`agents/pastoral/formation-practice.md`)
# cannot be recognized by path alone; a BREACH on one is a prompt to check
# whether it is a branch, not an instruction to compress it.
EXEMPT_NAMES = ("DECISIONS.md", "TIMELINE.md")
EXEMPT_PARTS = ("_archive", "archive", "references")
# `system/memory/` cold storage: everything except the two hot files the registry
# names explicitly (`working-log.md`, `WORKING.md`) — and a registry entry
# outranks this list anyway, so naming the directory is safe.
EXEMPT_PREFIX = ("system/library/", "system/memory/", "system/upgrades/",
                 "inbox/", "_processed/")


# Working ledger — registry BYTE_CEILINGS entry above (12KB). Retention: keep
# open + ~20 recent closed; archive older closed rows (prune / health enforce).
NEVER_EXEMPT = ("system/memory/findings-ledger.md",)


def exempt(r):
    if r in NEVER_EXEMPT:
        return False
    return (r.rsplit("/", 1)[-1] in EXEMPT_NAMES
            or any(p in r.split("/") for p in EXEMPT_PARTS)
            or r.startswith(EXEMPT_PREFIX))


def count(p):
    try:
        t = p.read_text(encoding="utf-8")
        return len(t.splitlines()), len(t.encode("utf-8"))
    except Exception:
        return None


def byte_cap_for(r):
    if r in BYTE_CEILINGS:
        return BYTE_CEILINGS[r]
    for pat, cap in GLOB_BYTE_CEILINGS:
        if fnmatch.fnmatch(r, pat) or fnmatch.fnmatch(r, pat.replace("**/", "")):
            return cap
    return DEFAULT_BYTE_CEILING


def check(path, cap, honour_exempt=True):
    c = count(path)
    if c is None:
        return None
    r = rel(path)
    if honour_exempt and r not in CEILINGS and exempt(r):
        return None          # STRUCTURE.md names it exempt; an explicit registry
                             # entry still wins, so nothing can be hidden by accident
    n, b = c
    bcap = byte_cap_for(rel(path))
    breach = n > cap or b > bcap
    return {"file": rel(path), "lines": n, "ceiling": cap,
            "bytes": b, "byte_ceiling": bcap,
            "over": max(0, n - cap), "over_bytes": max(0, b - bcap),
            "status": "BREACH" if breach else "ok"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file"); ap.add_argument("--dir")
    ap.add_argument("--pattern", help="substring filter under --dir, or a glob on its own")
    ap.add_argument("--max", type=int, default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    def cap_for(path, explicit):
        """Explicit --max wins; else the registry above; else the 150 default."""
        if explicit is not None:
            return explicit
        r = rel(path)
        if r in CEILINGS:
            return CEILINGS[r]
        for pat, cap in GLOB_CEILINGS:
            if fnmatch.fnmatch(r, pat) or fnmatch.fnmatch(r, pat.replace("**/", "")):
                return cap
        return 150

    results = []
    if a.file:
        # Naming one file explicitly is a deliberate act — measure it even if it
        # is exempt, so "how big is this branch?" stays an answerable question.
        p = ROOT / a.file
        r = check(p, cap_for(p, a.max), honour_exempt=False)
        if r: results.append(r)
    elif a.dir:
        # Recursive, and --pattern narrows it to the paths that contain that
        # substring — "the history files under workspaces/" is a question about
        # names, not a glob a runbook should have to spell.
        for p in paths_arg(dirs=[a.dir], pattern=a.pattern):
            r = check(p, cap_for(p, a.max))
            if r: results.append(r)
    elif a.pattern:
        for p in safe_glob(a.pattern):
            r = check(p, cap_for(p, a.max))
            if r: results.append(r)
    else:
        # Glob scans skip non-live regions: upgrade payloads are duplicate
        # copies of tree files, archives and inbox are not loaded surfaces.
        SKIP = ("system/upgrades/", "_archive/", "inbox/", "_processed/")
        for f, cap in CEILINGS.items():
            r = check(ROOT / f, cap)
            if r: results.append(r)
        for pat, cap in GLOB_CEILINGS:
            for p in safe_glob(pat):
                if any(s in rel(p) for s in SKIP):
                    continue
                # Explicit registry entry outranks glob (CORE/README vs wisdom/*).
                if rel(p) in CEILINGS:
                    continue
                r = check(p, cap)
                if r: results.append(r)

    if a.json:
        print(json.dumps(results, indent=2))
    else:
        print("== ceilings")
        if not results:
            print("   no ceiling-bearing files exist yet")
        for r in results:
            flag = "BREACH" if r["status"] == "BREACH" else "     "
            over = []
            if r["over"]:
                over.append(f"+{r['over']} lines")
            if r["over_bytes"]:
                over.append(f"+{r['over_bytes']:,}B")
            print(f"   {flag} {r['lines']:>4}/{r['ceiling']:<4} {r['bytes']:>6,}B/{r['byte_ceiling']:<6,}B {r['file']}"
                  + (f"   ({', '.join(over)} — compress or archive, do not raise)" if over else ""))
    return 1 if any(r["status"] == "BREACH" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
