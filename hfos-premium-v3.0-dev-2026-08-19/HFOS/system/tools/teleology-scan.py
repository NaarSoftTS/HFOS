#!/usr/bin/env python3
"""Scan entity faces for ANCHOR blocks (system/core/SIGNAL.md · STRUCTURE.md).

The script measures; the model judges. Three mechanical checks:

1. ENTITY-NO-ANCHOR  — a workspace / sub-workspace FOUNDATIONS.md (or life-area
   HOME.md) missing <serves> or <objectives>. Entities need their own heart.
2. STALE-ANCHOR      — an anchor whose last-validated date is older than
   --stale-days (default 60). Stale filters silently filter the wrong things.
3. MATURED-NO-ANCHOR — a project that has grown its own DECISIONS.md,
   PEOPLE.md, or identity/ but whose PROJECT.md carries no anchor. Maturity
   earns a why.

What this tool deliberately does NOT flag: a plain project without an anchor.
Inheritance-first (operator decision, 2026-08-01) — a project inherits its workspace's
FOUNDATIONS, and empty is correct. Orphaned heart material inside captures is
a judgment call and belongs to the sweep, not to a grep.

Usage:  teleology-scan.py [--stale-days N] [--json]
Exit:   0 clean, 1 findings.
"""
import sys, json, re, argparse, datetime
from _lib import ROOT, rel

STALE_DEFAULT = 60
MATURITY_MARKS = ("DECISIONS.md", "PEOPLE.md", "identity")


def has_anchor(text):
    return "<serves>" in text and "<objectives>" in text


def last_validated(text):
    m = re.search(r"last-validated:\s*(\d{4}-\d{2}-\d{2})", text)
    if not m:
        return None
    try:
        return datetime.date.fromisoformat(m.group(1))
    except ValueError:
        return None


def entity_faces():
    """Workspace + sub-workspace FOUNDATIONS.md, life-area HOME.md."""
    faces = []
    vroot = ROOT / "workspaces"
    for v in sorted(vroot.iterdir()) if vroot.is_dir() else []:
        if not v.is_dir():
            continue
        faces.append((v / "FOUNDATIONS.md", "workspace"))
        for s in sorted(v.iterdir()):
            skip = {"projects", "resources", "possibilities", "shared", "_archive"}
            if s.is_dir() and s.name not in skip and (s / "HOME.md").exists():
                faces.append((s / "FOUNDATIONS.md", "sub-workspace"))
    lroot = ROOT / "life"
    for a in sorted(lroot.iterdir()) if lroot.is_dir() else []:
        if a.is_dir() and (a / "HOME.md").exists():
            faces.append((a / "HOME.md", "life-area"))
    return faces


def matured_projects():
    for pdir in ROOT.glob("workspaces/**/projects/*/"):
        if any((pdir / m).exists() for m in MATURITY_MARKS):
            yield pdir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stale-days", type=int, default=STALE_DEFAULT)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    today = datetime.date.today()
    findings = []

    for face, kind in entity_faces():
        if not face.exists():
            findings.append({"check": "ENTITY-NO-ANCHOR", "file": rel(face),
                             "note": f"{kind} face file missing entirely"})
            continue
        text = face.read_text(encoding="utf-8")
        if not has_anchor(text):
            findings.append({"check": "ENTITY-NO-ANCHOR", "file": rel(face),
                             "note": f"{kind} face lacks <serves>/<objectives>"})
            continue
        lv = last_validated(text)
        if lv is None:
            findings.append({"check": "STALE-ANCHOR", "file": rel(face),
                             "note": "anchor has no last-validated date"})
        elif (today - lv).days > a.stale_days:
            findings.append({"check": "STALE-ANCHOR", "file": rel(face),
                             "note": f"last-validated {lv} ({(today - lv).days}d ago)"})

    for pdir in matured_projects():
        pf = pdir / "PROJECT.md"
        marks = [m for m in MATURITY_MARKS if (pdir / m).exists()]
        if not pf.exists() or not has_anchor(pf.read_text(encoding="utf-8")):
            findings.append({"check": "MATURED-NO-ANCHOR", "file": rel(pdir),
                             "note": f"carries {'/'.join(marks)} but no anchored PROJECT.md"})

    if a.json:
        print(json.dumps(findings, indent=2))
    else:
        print(f"== teleology ({len(findings)} findings)")
        for f in findings:
            print(f"   {f['check']:<18} {f['file']}   ({f['note']})")
        if not findings:
            print("   all entity faces anchored and fresh")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
