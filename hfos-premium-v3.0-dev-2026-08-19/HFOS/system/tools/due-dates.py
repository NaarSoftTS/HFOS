#!/usr/bin/env python3
"""All date arithmetic in one place.

No runbook does date math. A model computing "is this 7 days old" is doing
unverifiable arithmetic in a prompt, and it will be wrong eventually without
telling anyone. This script answers; the model decides what to do about it.

Windows are written the way a runbook says them — 7d, 4w, 60d — and parsed in
one place, so a window never means two things in two callers.

Usage:
  due-dates.py --file momentum/WAITING.md
  due-dates.py --file momentum/WAITING.md --file momentum/BLOCKED.md
  due-dates.py --file system/loops/hero/state/backlog.md --older-than 7d
  due-dates.py --dir relationships/people --older-than 30d
  due-dates.py --stale momentum/
  due-dates.py --file relationships/INDEX.md --no-contact 60d
Exit: 0 nothing due, 1 something due (a signal, not an error).
"""
import re, sys, json, argparse
from _lib import rel, parse_date, parse_duration, paths_arg, today

FIELD = lambda name: re.compile(rf"{re.escape(name)}\s*::\s*(\d{{4}}-\d{{2}}-\d{{2}})", re.I)
ANY_DATE = re.compile(r"(\d{4}-\d{2}-\d{2})")

# Structured dates only — the default for --due.
#
# The tool used to match ANY date-like string, so every narrative date surfaced
# as "due": header dates, dates inside prose annotations, dates quoted in a
# sweep's own commentary. On 2026-08-01 the sweep reported 15 of 15 lines were
# prose. Every consumer had learned to hand-filter the output, which is exactly
# the drift a tool exists to prevent — and a hand-filtered instrument gets
# hand-filtered wrongly eventually.
#
# A date is structured when it is (a) the value of an inline `name:: ` field,
# or (b) a table cell that is nothing but a date. Both are places a date was
# *written to be read by a machine*. A date in a sentence was not.
# `--any-date` restores the old behaviour explicitly for anyone who wants it.
ANY_FIELD_DATE = re.compile(r"(?:^|[\s(|*_>\[])([A-Za-z][\w-]*)\s*::\s*(\d{4}-\d{2}-\d{2})")
CELL_DATE = re.compile(r"^[\s*_`]*(\d{4}-\d{2}-\d{2})[\s*_`]*$")

# Structured is not the same as due-bearing, and conflating them was the second
# half of the same defect. `check::` is a forcing date; `stamped::` is "a loop
# touched this entry today." Both are machine-written, and reporting the second
# as due is how "every BLOCKED entry is due" became a nightly untruth.
#
# Due-bearing fields answer "when does this force a move." Everything else is
# counted, not listed — the same treatment stale_mode already gives undated
# entries, and for the same reason: a fact belongs in one report, once.
DUE_FIELDS = {"check", "check-date", "due", "deadline", "follow-up", "followup",
              "revisit", "expires", "review",
              # table-column headers that carry a clock
              "queued", "due date", "next check", "cell"}


def structured_dates(line, headers=None):
    """Yield (date string, field name) for machine-written dates on one line.

    In a table, the column's own header is the field name — so a `Queued`
    column reads as due-bearing and a `Closed` column does not. Without that,
    every date-shaped cell in every table looked like a deadline.
    """
    for m in ANY_FIELD_DATE.finditer(line):
        yield m.group(2), m.group(1)
    if line.lstrip().startswith("|"):
        for idx, cell in enumerate(line.split("|")):
            m = CELL_DATE.match(cell)
            if m:
                yield m.group(1), (headers or {}).get(idx, "cell")


def table_headers(lines):
    """{line number: {column index: header word}} for every markdown table.

    A header row is the line above a `|---|---|` separator, and it governs
    every row until the table ends — so a cell can know which column it is in.
    """
    out, cur = {}, None
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if SEPARATOR.match(s) and i >= 2:
            cur = {j: c.strip().strip("*_` ").lower()
                   for j, c in enumerate(lines[i - 2].split("|")) if c.strip()}
            continue
        if not s.startswith("|"):
            cur = None
        if cur:
            out[i] = cur
    return out
CONTACT = re.compile(r"(?:last[-\s]?contact|contacted|last[-\s]?spoke)\s*::?\s*(\d{4}-\d{2}-\d{2})", re.I)
SEPARATOR = re.compile(r"^\|[\s:\-|]+\|?$")
# An entry is a bullet or a heading plus everything under it until the next one.
ENTRY_START = re.compile(r"^(?:\s{0,3}[-*+]\s+|#{1,6}\s+)")

# The sweep stamps every entry it touches, so an entry whose newest date is a
# fortnight old is one no loop has touched in a fortnight. Overridable with
# --older-than; named here so the window is a constant and not a prompt's guess.
DEFAULT_STALE = 14
DEFAULT_NO_CONTACT = 60


def lines_of(f):
    try:
        return f.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []


def entries(lines):
    """Yield (first line number, block of lines) for each entry in a file."""
    start, block = None, []
    for i, line in enumerate(lines, 1):
        if ENTRY_START.match(line):
            if start is not None:
                yield start, block
            start, block = i, [line]
        elif start is not None:
            block.append(line)
    if start is not None:
        yield start, block


def due_mode(files, field, older, t, any_date=False):
    """Dates that were written to be read by a machine, unless --any-date.

    Returns (hits, skipped) — skipped counts structured dates that are real
    fields but not due-bearing ones, so the caller can say so without listing
    them as due.
    """
    hits, skipped = [], 0
    for f in files:
        lines = lines_of(f)
        heads = table_headers(lines)
        for i, line in enumerate(lines, 1):
            if field:
                m = FIELD(field).search(line)
                found = [(m.group(1), field)] if m else []
            elif any_date:
                found = [(s, "prose") for s in ANY_DATE.findall(line)[:1]]
            else:
                found = list(structured_dates(line, heads.get(i)))
            for raw, fname in found:
                d = parse_date(raw)
                if not d:
                    continue
                if not (field or any_date) and fname.lower() not in DUE_FIELDS:
                    skipped += 1
                    continue
                age = (t - d).days
                if age >= older if older is not None else d <= t:
                    hits.append({"file": rel(f), "line": i, "date": str(d),
                                 "days": age, "field": fname,
                                 "text": line.strip()[:100]})
    return hits, skipped


def stale_mode(files, window, t):
    """Entries whose most recent date is older than the staleness window.

    Undated entries are counted, not listed: a missing check date is
    momentum-lint's finding, and reporting it twice in two vocabularies is how
    the same problem gets fixed zero times.
    """
    hits, undated = [], 0
    for f in files:
        for i, block in entries(lines_of(f)):
            dates = [d for d in (parse_date(x) for x in ANY_DATE.findall("\n".join(block))) if d]
            if not dates:
                undated += 1
                continue
            newest = max(dates)
            age = (t - newest).days
            if age >= window:
                hits.append({"file": rel(f), "line": i, "date": str(newest),
                             "days": age, "text": block[0].strip()[:100]})
    return hits, undated


def contact_mode(files, window, t):
    hits = []
    for f in files:
        for i, line in enumerate(lines_of(f), 1):
            if SEPARATOR.match(line.strip()):
                continue
            m = CONTACT.search(line)
            dates = [parse_date(m.group(1))] if m else \
                    [d for d in (parse_date(x) for x in ANY_DATE.findall(line)) if d]
            dates = [d for d in dates if d]
            if not dates:
                continue
            newest = max(dates)
            age = (t - newest).days
            if age >= window:
                hits.append({"file": rel(f), "line": i, "date": str(newest),
                             "days": age, "field": "contact",
                             "text": line.strip()[:100]})
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", action="append", help="tree-relative file or directory; repeatable")
    ap.add_argument("--dir", action="append", help="directory to scan; repeatable")
    ap.add_argument("--scan", action="append", help="original spelling of --file; kept working")
    ap.add_argument("--field", default=None,
                    help="inline field name, e.g. check / releases / last-contact")
    ap.add_argument("--older-than", default=None,
                    help="window (7d, 4w, 30) — report entries whose date is older")
    ap.add_argument("--stale", nargs="?", const="momentum", default=None,
                    help="entries whose most recent date is past the staleness window")
    ap.add_argument("--no-contact", nargs="?", const=str(DEFAULT_NO_CONTACT) + "d", default=None,
                    help="rows whose contact date is older than this window")
    ap.add_argument("--any-date", action="store_true",
                    help="match narrative dates too (pre-2026-08-01 behaviour; noisy by design)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    older = parse_duration(a.older_than)
    t = today()
    specs = (a.file or []) + (a.scan or [])

    if a.stale is not None:
        label = a.stale
        window = older if older is not None else DEFAULT_STALE
        files = paths_arg(files=[a.stale])
        title = f"stale entries ({label}, untouched {window}d or more)"
    elif a.no_contact is not None:
        window = parse_duration(a.no_contact, DEFAULT_NO_CONTACT)
        files = paths_arg(files=specs, dirs=a.dir)
        label = ", ".join(specs + (a.dir or [])) or "(nothing)"
        title = f"no contact ({label}, {window}d or more)"
    else:
        if not specs and not a.dir:
            print("== due dates\n   FAIL name what to scan: --file PATH, --dir PATH, or --stale PATH")
            return 1
        files = paths_arg(files=specs, dirs=a.dir)
        label = ", ".join(specs + (a.dir or []))
        title = f"due dates ({label}{', field ' + a.field if a.field else ''}" \
                + (f", older than {older}d)" if older is not None else ")")

    if not files:
        target = a.stale or label
        print(f"== {title}\n   nothing to scan at {target} (not yet migrated)")
        return 0

    undated = skipped = 0
    if a.stale is not None:
        hits, undated = stale_mode(files, window, t)
    elif a.no_contact is not None:
        hits = contact_mode(files, window, t)
    else:
        hits, skipped = due_mode(files, a.field, older, t, a.any_date)

    if a.json:
        print(json.dumps(hits, indent=2))
    else:
        print(f"== {title}")
        if not hits:
            print("   nothing due")
        for h in sorted(hits, key=lambda x: -x["days"]):
            src = f"[{h.get('field', '?')}]"
            print(f"   {h['date']}  {h['days']:>4}d  {src:<12} {h['file']}:{h['line']}  {h['text']}")
        if hits:
            print(f"   {len(hits)} item(s)")
        if undated:
            print(f"   ({undated} entr(ies) carry no date at all — momentum-lint's finding, not this one)")
        if skipped:
            print(f"   ({skipped} structured date(s) skipped — record-keeping fields "
                  f"like stamped::/since::, not due-bearing. --any-date to see everything)")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
