#!/usr/bin/env python3
"""The momentum ledgers have a grammar. This is the mechanical half of it.

An entry that cannot name its person, its release condition, or where its
canonical context lives is not tracked work — it is a note that will read as
tracked for weeks. A waiting entry with no check date is the severe case: it is
invisible to every automated reader in the system, including the loop that
would have chased it. Structure is checkable, so a script checks it. Whether an
entry is in the right room at all — the room test — stays with the reader.

Two momentum shapes, one tool (auto-detected by what's on disk):
  full   — five ledger files under momentum/ (NEEDS_ME.md, BLOCKED.md, …)
  simple — one momentum/MOMENTUM.md whose `## ` sections are the same ledgers
           (entries are `###` blocks, bullets, or table rows — same grammar)

Usage:  momentum-lint.py [--file momentum/WAITING.md | --file momentum/MOMENTUM.md] [--json]
Exit:   0 clean, or nothing migrated yet. 1 violations found (a signal).
"""
import re, sys, json, argparse
from _lib import ROOT, rel, parse_date

ROOTS = ("foundations/", "life/", "relationships/", "workspaces/", "momentum/",
         "system/", "inbox/", "exports/")

# Per-ledger required fields: (what it must name, accepted field names, kind).
# The field names are alternates, not synonyms to be mixed within one entry —
# the lint accepts whichever spelling the migration settles on.
LEDGERS = {
    "BLOCKED.md": [
        ("person to chase", ("chase", "person", "who", "owner"), "text"),
        ("release condition", ("releases", "release", "unblocks"), "text"),
    ],
    "WAITING.md": [
        ("party", ("party", "person", "who", "with"), "text"),
        ("release condition", ("releases", "release"), "text"),
        ("check date", ("check", "check-date"), "date"),
    ],
    "COMMITMENTS.md": [
        ("person", ("person", "who", "to"), "text"),
        ("promise", ("promised", "promise"), "text"),
        ("where evidence would appear", ("evidence", "evidence-at"), "text"),
    ],
    "NEEDS_ME.md": [
        ("why it needs this person", ("why", "why-me"), "text"),
    ],
    "READY_TO_SHIP.md": [
        ("ship target", ("ships-to", "ships", "target"), "text"),
        ("value created there", ("value", "creates"), "text"),
    ],
}
# Simple shape: `## ` section headings in MOMENTUM.md map to the same specs.
SINGLE_NAME = "MOMENTUM.md"
SECTION_MAP = {
    "needs me": "NEEDS_ME.md",
    "commitments": "COMMITMENTS.md",
    "blocked": "BLOCKED.md",
    "waiting": "WAITING.md",
    "ready to ship": "READY_TO_SHIP.md",
}
# These hold entries too, but only the pointer rule applies to them.
POINTER_ONLY_DIRS = ("delegated", "cross-workspace")

# Ceilings are imported from check-ceilings.py so the two tools share one
# registry and cannot drift. A second copy of a number is a second thing to
# remember to change, and this is what forgetting looks like.
try:
    from check_ceilings import CEILINGS as _LINE_CEILINGS, BYTE_CEILINGS as _BYTE_CEILINGS
except ImportError:  # module name has a hyphen on disk
    import importlib.util as _ilu
    _spec = _ilu.spec_from_file_location(
        "check_ceilings", str(__import__("pathlib").Path(__file__).parent / "check-ceilings.py"))
    _cc = _ilu.module_from_spec(_spec)
    _spec.loader.exec_module(_cc)
    _LINE_CEILINGS, _BYTE_CEILINGS = _cc.CEILINGS, _cc.BYTE_CEILINGS


def ceiling_for(rel_path):
    """(line ceiling, byte ceiling) from the one registry. None if unregistered."""
    return _LINE_CEILINGS.get(rel_path), _BYTE_CEILINGS.get(rel_path)

TOKEN = re.compile(r"`([^`\n]+?)`|\[[^\]]*\]\(([^)\s]+)\)")
SEPARATOR = re.compile(r"^\|[\s:\-|]+\|?$")


def field(text, names):
    """Inline `name:: value` — the same field syntax due-dates.py reads.

    An entry is one line carrying several fields, so a value ends where the
    next field or separator begins; otherwise every field swallows the rest.
    """
    alts = "|".join(re.escape(n) for n in names)
    m = re.search(rf"(?:^|[\s(|*_>])(?:{alts})\s*::\s*([^\n|]+)", text, re.I)
    if not m:
        return None
    v = re.split(r"\s+[·•;]\s*|\s{2,}", m.group(1))[0]
    v = re.split(r"\s+[\w-]+\s*::", v)[0]
    return v.strip().strip("`\"'*") or None


def pointer(text):
    """A tree-relative path, named either as a field or in a link/backtick."""
    p = field(text, ("context", "canonical", "lives-in"))
    if p:
        p = p.split("#")[0].strip().strip("`<>[]()")
        if p.startswith(ROOTS):
            return p
    for m in TOKEN.finditer(text):
        cand = (m.group(1) or m.group(2) or "").split("#")[0].strip()
        if cand.startswith(ROOTS) and " " not in cand.rstrip("/"):
            return cand
    return None


def resolves(p):
    if any(ch in p for ch in "*?<>[{"):      # templates and globs are not claims
        return True
    return (ROOT / p).exists()


def table_header_map(header, spec):
    """Which required fields does this table carry as columns?

    A ledger is often more readable as a table than as inline fields, and a
    header row names its fields perfectly well. Returns {field_index: column}.
    """
    cols = [c.strip().strip("`*").lower() for c in header.strip("|").split("|")]
    found = {}
    for idx, (_, names, _) in enumerate(spec):
        for ci, col in enumerate(cols):
            if any(col == n or col.startswith(n) or n in col.split() for n in names):
                found[idx] = ci
                break
    return found, cols


def entries(text):
    """One entry per table row, else per top-level bullet, else per ### section.

    Ledger shape is not settled yet, so the splitter picks whichever form the
    file actually uses rather than dictating one.
    """
    lines = text.splitlines()
    rows, bullets, sections = [], [], []
    cur_header = None
    fence = False
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("```"):
            fence = not fence
            continue
        if fence or not s:
            continue
        if s.startswith("|") and s.count("|") >= 3:
            if SEPARATOR.match(s):
                continue
            nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
            if SEPARATOR.match(nxt):          # this row is the header
                cur_header = s
                continue
            rows.append((i + 1, s, cur_header))
        elif re.match(r"^(?:[-*+]|\d+\.)\s+\S", line):
            block = [s]
            for cont in lines[i + 1:]:
                if cont.strip() and cont[:1].isspace():
                    block.append(cont.strip())
                else:
                    break
            bullets.append((i + 1, " ".join(block), None))
        elif s.startswith("### "):
            block, j = [s], i + 1
            while j < len(lines) and not lines[j].startswith(("### ", "## ")):
                block.append(lines[j].strip())
                j += 1
            sections.append((i + 1, " ".join(x for x in block if x), None))
    return rows or bullets or sections


def strip_comments(text):
    """Blank out HTML comments so entry-shape examples never lint as entries.
    Line count is preserved, so reported line numbers stay true."""
    out, in_comment = [], False
    for line in text.splitlines():
        s = line
        if in_comment:
            if "-->" in s:
                in_comment = False
            out.append("")
            continue
        if "<!--" in s:
            if "-->" not in s[s.index("<!--"):]:
                in_comment = True
            out.append(s[:s.index("<!--")])
            continue
        out.append(s)
    return "\n".join(out)


def lint_text(text, spec, relname, offset=0):
    """Grammar checks on one ledger's text. Line numbers are offset for slices."""
    bad = []
    for line_no, entry, header in entries(strip_comments(text)):
        short = entry[:90]
        cells, hmap = [], {}
        if header:
            hmap, _ = table_header_map(header, spec)
            # A table whose header carries fewer than half the required fields is
            # not an entry table — a Chases or Closed table has its own shape and
            # linting it against the entry spec produces noise, not findings.
            if len(hmap) * 2 < len(spec):
                continue
            cells = [c.strip() for c in entry.strip("|").split("|")]
        for idx, (label, names, kind) in enumerate(spec):
            val = field(entry, names)
            if not val and idx in hmap and idx < len(cells) + 1:
                ci = hmap[idx]
                val = cells[ci].strip().strip("*`") if ci < len(cells) else None
                val = val or None
            if not val:
                bad.append({"file": relname, "line": line_no + offset,
                            "issue": f"no {label} ({names[0]}::)", "text": short})
            elif kind == "date" and not parse_date(val):
                bad.append({"file": relname, "line": line_no + offset,
                            "issue": f"{label} is not a date: {val}", "text": short})
        p = pointer(entry)
        if not p:
            bad.append({"file": relname, "line": line_no + offset,
                        "issue": "no pointer to canonical context", "text": short})
        elif not resolves(p):
            bad.append({"file": relname, "line": line_no + offset,
                        "issue": f"context pointer does not resolve: {p}", "text": short})
    return bad


def ceiling_violations(text, relname):
    """Ceiling check, for any momentum ledger the registry covers. Bytes bind
    as well as lines (2026-07-31 performance audit)."""
    bad = []
    line_cap, byte_cap = ceiling_for(relname)
    n, b = len(text.splitlines()), len(text.encode("utf-8"))
    if line_cap and n > line_cap:
        bad.append({"file": relname, "line": 0,
                    "issue": f"{n}/{line_cap} lines — move entries out, never raise",
                    "text": ""})
    if byte_cap and b > byte_cap:
        bad.append({"file": relname, "line": 0,
                    "issue": f"{b:,}/{byte_cap:,} bytes — compress or archive, never raise",
                    "text": ""})
    return bad


def lint(path, spec):
    """Returns (violations, note). A missing file is a note, never a violation."""
    if not path.exists():
        return [], f"{rel(path)} not yet migrated"
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return [{"file": rel(path), "line": 0, "issue": f"unreadable ({e})", "text": ""}], None
    bad = lint_text(text, spec, rel(path))
    bad += ceiling_violations(text, rel(path))
    return bad, None


def lint_single(path):
    """Simple shape: `## ` sections of MOMENTUM.md are the ledgers, linted with
    the same specs. Unknown sections are the reader's business, not findings."""
    if not path.exists():
        return [], f"{rel(path)} not present"
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return [{"file": rel(path), "line": 0, "issue": f"unreadable ({e})", "text": ""}], None
    lines = strip_comments(text).splitlines()
    heads = [(i, s.strip()[3:].strip().lower())
             for i, s in enumerate(lines)
             if s.strip().startswith("## ") and not s.strip().startswith("###")]
    bad = []
    for n, (start, name) in enumerate(heads):
        ledger = SECTION_MAP.get(name)
        if not ledger:
            continue
        end = heads[n + 1][0] if n + 1 < len(heads) else len(lines)
        slice_text = "\n".join(lines[start + 1:end])
        bad += lint_text(slice_text, LEDGERS[ledger], rel(path), offset=start + 1)
    bad += ceiling_violations(text, rel(path))
    return bad, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", help="lint one ledger, tree-relative")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    bad, notes = [], []
    single = ROOT / "momentum" / SINGLE_NAME

    if a.file:
        p = ROOT / a.file
        if p.name == SINGLE_NAME:
            v, note = lint_single(p)
        else:
            v, note = lint(p, LEDGERS.get(p.name, []))
        bad += v
        if note:
            notes.append(note)
    else:
        if single.exists():                    # simple shape
            v, note = lint_single(single)
            bad += v
            if note:
                notes.append(note)
        else:                                  # full shape
            for name, spec in LEDGERS.items():
                v, note = lint(ROOT / "momentum" / name, spec)
                bad += v
                if note:
                    notes.append(note)
        for d in POINTER_ONLY_DIRS:
            base = ROOT / "momentum" / d
            if base.is_dir():
                for f in sorted(base.rglob("*.md")):
                    if f.name != "README.md":
                        v, note = lint(f, [])
                        bad += v
                        if note:
                            notes.append(note)

    if a.json:
        print(json.dumps({"violations": bad, "not_migrated": notes}, indent=2))
    else:
        print("== momentum lint")
        for v in bad:
            where = f"{v['file']}:{v['line']}" if v["line"] else v["file"]
            print(f"   {where}  {v['issue']}" + (f"   {v['text']}" if v["text"] else ""))
        if not bad:
            print("   every entry names what its room requires")
        else:
            print(f"   {len(bad)} violation(s)")
        for n in notes:
            print(f"   -- {n}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
