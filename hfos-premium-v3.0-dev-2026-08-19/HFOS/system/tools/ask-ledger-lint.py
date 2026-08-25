#!/usr/bin/env python3
"""Lint the ask ledger's line grammar (system adaptation).

A ledger line is a speedometer reading: date · class > use-case · subject >
project · optional (note). The class must be canonical — the profile tallies
by it, and a free-typed class silently vanishes from every tally. Sub-levels
and subjects are the owner's vocabulary and are not judged. Notes stay
mechanics-short; a sentence in a note is a diary entry trying to happen.

Absent ledger = exit 0 silently (this version doesn't keep one).
Usage:  ask-ledger-lint.py [--json]
Exit:   0 clean or absent · 1 violations (a signal, not an error)
"""
import re, sys, json, argparse
from _lib import ROOT, rel

LEDGER = ROOT / "system" / "memory" / "ask-ledger.md"
CLASSES = {"content-gen", "comms-as-owner", "decide", "research",
           "build-ship", "people", "route-admin", "system"}
ENTRY = re.compile(r"^(\d{4}-\d{2}-\d{2})\s*·\s*([^·]+?)\s*(?:·\s*([^·]+?))?\s*(?:·\s*(\([^)]*\)))?\s*$")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if not LEDGER.exists():
        print("== ask-ledger lint\n   no ledger (this version doesn't keep one, or none yet)")
        return 0
    bad = []
    for i, line in enumerate(LEDGER.read_text(encoding="utf-8").splitlines(), 1):
        s = line.strip()
        if not s or not re.match(r"^\d{4}-\d{2}-\d{2}", s):
            continue  # profile block, headings, prose — only dated lines are entries
        m = ENTRY.match(s)
        if not m:
            bad.append({"line": i, "issue": "not `date · class > use-case · subject > project · (note)`", "text": s[:80]})
            continue
        cls = m.group(2).split(">")[0].strip()
        if cls not in CLASSES:
            bad.append({"line": i, "issue": f"unknown class '{cls}' — canonical: {', '.join(sorted(CLASSES))}", "text": s[:80]})
        note = m.group(4)
        if note and len(note.strip("() ").split()) > 6:
            bad.append({"line": i, "issue": "note too long — mechanics only, ≤4 words", "text": s[:80]})
    if a.json:
        print(json.dumps({"violations": bad}, indent=2))
    else:
        print("== ask-ledger lint")
        for v in bad:
            print(f"   {rel(LEDGER)}:{v['line']}  {v['issue']}   {v['text']}")
        print(f"   {len(bad)} violation(s)" if bad else "   every line reads clean")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
