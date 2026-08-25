#!/usr/bin/env python3
"""Every tree path this system mentions must resolve.

Checks markdown links and backticked tree-relative paths across all .md files.
A broken pointer is the failure mode this whole architecture is built to avoid:
a loop that cannot resolve its runbook fails closed, which is designed behaviour
but is no reason to ship dangling pointers.

Usage:  orphan-scan.py [--under system] [--quiet]
Exit:   0 clean, 1 orphans found.
"""
import re, sys, argparse
from _lib import ROOT, walk, rel, report

ROOTS = ("foundations/", "life/", "relationships/", "workspaces/", "momentum/",
         "system/", "inbox/", "exports/")
# `system/` is also the prefix of a common Obsidian nested tag (`system/immune`,
# `system/nervous` in the wellness research). A path under system/ is only a path
# if its second segment is one of the rooms that actually exist there.
SYSTEM_ROOMS = ("core", "adapters", "agents", "skills", "playbooks", "tools",
                "loops", "memory", "automations", "upgrades", "library",
                "licenses", "HEALTH.md", "ACKNOWLEDGEMENTS.md", "README.md")
FILES = ("AGENTS.md", "NOW.md", "CLAUDE.md", "START_HERE.md")
LOGICAL = ("@resources", "@dev", "@coms", "@publish", "<tree root>")

# Content roots the migration has not reached yet. A pointer into one of these
# is an unmet expectation, not a broken link — the migration map says the target
# is coming. Separating the two is the whole value of this scan during a rebuild:
# 357 undifferentiated "orphans" is noise nobody reads twice.
# CLOSED 2026-07-27. This was a migration-window hatch that excluded all eight
# operator rooms from failure, which meant the scan could not fail where almost
# all content lives — while ARCHITECTURE.md cited it as the check for "every
# pointer resolves." An audit tuned to agree with its own documentation is worse
# than no audit. Only genuinely create-on-first-write targets remain exempt.
PENDING_ROOTS = ()
PENDING_GLOBS = ()
# Files a loop creates on its first run. Absent is correct until then.
CREATED_BY_LOOPS = (
    "system/memory/lessons/", "system/memory/health/", "system/memory/briefings/",
    "system/memory/dispatches/", "system/memory/minutes/", "system/memory/sessions/",
    "system/memory/pruning/", "system/memory/meetings/", "momentum/READY_TO_SHIP.md",
    "momentum/cross-workspace/", "exports/", "system/memory/ask-ledger.md",
    # Loop state dirs: empty scaffolds were deleted 2026-07-27 (structure audit #7,
    # operator-approved); each loop recreates its own state/ on first write.
    "system/loops/sweep/state/", "system/loops/briefing/state/",
    "system/loops/prune/state/", "system/loops/health/state/",
)
# Template placeholders that are meant to be filled in, not resolved.
PLACEHOLDER = re.compile(r"YYYY|MM-DD|<[^>]+>|\[[a-z-]+\]|\bx\b")
# Generated files: they exist after the loop that writes them has run once.
GENERATED = ("system/HEALTH.md",)
# Declared-but-unbuilt: a pointer at a path this system has committed to and
# has not built yet is an unmet promise, not a broken link. Each one is named
# in a README so the promise is written down somewhere a person reads.
DECLARED = ("system/tools/dashboards/",)
# Documents whose job is to describe the OLD tree. Their dead paths are the point.
DESCRIBES_OLD_TREE = ("system/core/_archive/MIGRATION-MAP.md",
                      "system/core/_archive/BUILD-LOG.md")   # moved there 2026-08-01
# Documents whose job is to describe ANOTHER tree, or a tree that does not exist
# yet. Same reasoning as DESCRIBES_OLD_TREE, two directions it also points:
#   inbox/planning/ holds proposals. A proposal names the file it proposes to
#     create; that the file is absent is what makes it a proposal. Scoped to
#     `planning/` deliberately — a first pass exempted `inbox/` wholesale and an
#     audit caught it: 23 live files sit there, including the session handoff
#     every new thread reads first, and a blanket directory exemption over the
#     tree's most-read routing document is not what "capture" licenses.
#   system/upgrades/<packet>/ describes a post-apply tree plus its own apply-time
#     directories (`applied/`, `packets/`, backups). Those resolve on the
#     receiving system after the packet runs, never here before it
#     (`system/upgrades/PROTOCOL.md`).
# Added 2026-08-02, when this scan was wired into the nightly sweep: its eight
# standing findings were all of these two shapes, and a nightly check whose first
# run reports eight non-defects teaches the loop to stop reading it.
DESCRIBES_OTHER_TREE = ("inbox/planning/", "system/upgrades/")
# Append-only records of what was true when written. Rewriting their pointers
# would falsify the record; auditing them reports history as breakage. Neither
# is useful, so they are read as evidence rather than as live routing.
HISTORICAL = ("DECISIONS.md", "TIMELINE.md", "session-log.md", "prune-log.md")
HISTORICAL_DIRS = ("system/memory/sessions/", "system/memory/pruning/",
                   "system/memory/dispatches/", "system/memory/minutes/",
                   "system/memory/reports/", "inbox/_processed/")

LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
TICK = re.compile(r"`([^`\n]+?)`")

# The branch-sibling convention, resolved relative to the file that wrote it.
# Added 2026-08-02. `SIGNAL.md` -> `<split_rule>` makes pointers the main way
# depth leaves a hot file, and the tree writes those pointers RELATIVELY —
# `references/AGENT-full.md`, `archive/build-ledger-2026-08.md`. Every gate above
# is keyed to a leading tree root, so the entire class fell through: 39 live
# `references/...` pointers, none checked, while the sweep's verification step
# claimed they were. A dangling branch pointer is the worst kind, because the
# parent file has already given the material away.
#
# Only `references/` and `archive/` qualify. Widening this to relative paths in
# general was measured and rejected: bare `STATE.md` / `DECISIONS.md` /
# `context.md` are type names in prose, not sibling pointers, and `projects/x`
# is written relative to a workspace rather than to the file. That rule produced
# 3,315 false positives; this one produces 53 checks and finds real breakage.
BRANCH = re.compile(r"^(references|archive|_archive)/[\w.-]+(/[\w.-]+)*/?$")


def candidates(text):
    for m in LINK.finditer(text):
        yield m.group(1).split("#")[0].strip()
    for m in TICK.finditer(text):
        t = m.group(1).strip()
        if t.startswith(LOGICAL) or " " in t.rstrip("/"):
            continue
        if t.startswith("system/") and not t[len("system/"):].startswith(SYSTEM_ROOMS):
            continue                        # an Obsidian tag, not a tree path
        if t.startswith(ROOTS) and not looks_like_path(t):
            continue                        # a nested tag, not a tree path
        if t.startswith(ROOTS) or t in FILES or BRANCH.match(t.split("#")[0]):
            yield t


def resolve(raw, src):
    p = raw.split("#")[0].strip()
    if not p or p.startswith(("http://", "https://", "mailto:")) or p.startswith(LOGICAL):
        return True
    if any(ch in p for ch in "*?<>"):          # globs and placeholders
        return True
    if "[" in p or "{" in p:                    # <workspace>, [slug] templates
        return True
    if BRANCH.match(p):
        return (src.parent / p).exists()     # a branch sibling, by convention
    if p.startswith("./") or p.startswith("../"):
        target = (src.parent / p).resolve()
    elif p.startswith(ROOTS) or p in FILES:
        # Tree-relative first, then relative to the file that wrote it. A path
        # beginning with a root name may still be folder-relative — a research
        # index listing `foundations/x.md` from inside its own folder is not a
        # break, and calling it one trains the reader to ignore the scan.
        if (ROOT / p).resolve().exists():
            return True
        return (src.parent / p).resolve().exists()
    else:
        return True                             # not addressed as a tree path
    return target.exists()


def looks_like_path(t):
    """A tag and a path are spelled alike. Only one has a file extension, a
    trailing slash, or more than two segments — nested Obsidian tags such as
    `foundations/terrain` are neither, and flagging them as breaks is noise."""
    return t.endswith("/") or "." in t.rsplit("/", 1)[-1] or t.count("/") > 1


def pending(p, src=None):
    if PLACEHOLDER.search(p) or p in GENERATED or p.startswith(DECLARED):
        return True
    if p.startswith(("./", "../")) and src is not None:
        # A relative pointer is judged by where it lands, not how it is written.
        try:
            p = str((src.parent / p).resolve().relative_to(ROOT))
        except ValueError:
            return False
    return p.startswith(CREATED_BY_LOOPS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--under", default=None)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--all", action="store_true",
                    help="include pointers awaiting content migration")
    a = ap.parse_args()

    bad, waiting = [], []
    for f in walk(under=a.under):
        r = rel(f)
        if (r in DESCRIBES_OLD_TREE or f.name in HISTORICAL
                or r.startswith(HISTORICAL_DIRS) or r.startswith(DESCRIBES_OTHER_TREE)):
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        seen = set()
        for c in candidates(text):
            if c in seen:
                continue
            seen.add(c)
            if resolve(c, f):
                continue
            (waiting if pending(c, f) else bad).append(f"{rel(f)}  ->  {c}")

    n = report("orphan scan", sorted(bad), "every pointer resolves")
    if waiting:
        uniq = len({w.split("->")[1].strip() for w in waiting})
        print(f"   -- {len(waiting)} pointer(s) to {uniq} target(s) awaiting content "
              f"migration (see system/core/_archive/MIGRATION-MAP.md)")
        if a.all:
            for w in sorted(waiting):
                print(f"      {w}")
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
