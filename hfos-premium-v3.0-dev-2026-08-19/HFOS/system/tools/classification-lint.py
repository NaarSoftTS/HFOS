#!/usr/bin/env python3
"""classification-lint.py — are classification tags well-formed, and is the
always-on surface clean?

Checks (form only — judgment stays with the model and the person):
  1. Every `classification::` value is one of: public, shared, internal, restricted.
  2. Every `shared` or `restricted` tag has an `audience::` within 3 lines.
  3. The always-on files (AGENTS.md, NOW.md, foundations/SUMMARY.md) carry
     nothing tagged above internal — hot files hold no restricted branches.
  4. `derived-from::` lines point at paths that resolve.

Untagged files are fine: untagged = internal by doctrine (system/core/DISCLOSURE.md),
and internal already cannot leave. Exit 0 clean; exit 1 findings (a signal, not an error).
"""
import re, sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
if not (ROOT / "AGENTS.md").exists():          # tools may sit one level deeper
    ROOT = ROOT.parent

VALID = {"public", "shared", "internal", "restricted"}
CLS = re.compile(r"^\s*classification::\s*(\S+)", re.I)
AUD = re.compile(r"^\s*audience::\s*(\S+)", re.I)
DRV = re.compile(r"derived-from::\s*(\S+)")
HOT = ["AGENTS.md", "NOW.md", "foundations/SUMMARY.md"]

findings = []
files = [p for p in ROOT.rglob("*.md") if ".git" not in p.parts]

for p in files:
    try:
        lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        continue
    rel = p.relative_to(ROOT)
    for i, line in enumerate(lines):
        m = CLS.match(line)
        if m:
            val = m.group(1).strip("`*_").lower()
            if val not in VALID:
                findings.append(f"{rel}:{i+1}  unknown class '{val}' (valid: public/shared/internal/restricted)")
            elif val in ("shared", "restricted"):
                window = lines[i:i+4]
                if not any(AUD.match(w) for w in window):
                    findings.append(f"{rel}:{i+1}  '{val}' without an audience:: line — who is it for?")
            if val == "restricted" and str(rel) in HOT:
                findings.append(f"{rel}:{i+1}  restricted material tagged in an always-on file — branch it out")
        d = DRV.search(line)
        if d:
            tgt = d.group(1).strip("`,.")
            if not tgt.startswith("@") and not (ROOT / tgt).exists():
                findings.append(f"{rel}:{i+1}  derived-from:: points at missing '{tgt}'")

for h in HOT:
    p = ROOT / h
    if p.exists():
        t = p.read_text(encoding="utf-8", errors="ignore").lower()
        for m in re.finditer(r"classification::\s*(shared|restricted)", t):
            findings.append(f"{h}  always-on file carries a '{m.group(1)}' tag — hot files stay ≤ internal")

print("== classification lint")
if findings:
    seen = set()
    for f in findings:
        if f not in seen:
            print("   " + f); seen.add(f)
    sys.exit(1)
print("   tags well-formed; always-on surface clean")
sys.exit(0)
