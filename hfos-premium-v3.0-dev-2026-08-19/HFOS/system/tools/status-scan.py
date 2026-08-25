#!/usr/bin/env python3
"""Work that has sat in one state longer than that state can honestly hold it.

A state is a claim about right now. Left alone it keeps making that claim
indefinitely, and a stale claim is worse than no claim: the portfolio reads as
decided, or moving, or delivered, when nothing has happened for a month. The
transitions this catches are not failures — they are the ones that get skipped
quietly, which is exactly why a script counts the days instead of a reader
noticing.

Usage:
  status-scan.py --older-than 30d
  status-scan.py --state Shipped
  status-scan.py --older-than 14 --json
Exit: 0 nothing stale, 1 stale entries found (a signal, not an error).
"""
import re, sys, json, argparse, datetime
from _lib import ROOT, walk, rel, parse_date, today

# Days a piece of work may sit in a state before it needs a look. Keys are the
# states in system/core/STATES.md; None means terminal, nothing to chase.
# A work state is a short token. A sentence in a `status:` field is prose that
# happens to share a key name — reporting it as a stuck work item is noise, and
# noise is how a scan stops being read.
MAX_STATUS_LEN = 32

THRESHOLDS = {
    "captured": 7,
    "exploring": 21,
    # Chosen that never became Committed and was never dropped is the quiet
    # overcommit. Chosen is cheap and reversible; leaving it sitting turns it
    # into an implied obligation nobody ever actually made. Either it becomes a
    # commitment someone is holding us to, or it goes to not-now, honestly.
    "chosen": 21,
    "committed": 30,
    "moving": 14,
    "blocked": 7,
    "ready to ship": 7,
    # Shipped without reaching Learned is the most commonly skipped transition
    # in the whole system, and skipping it is why the same expensive mistake
    # recurs with total sincerity. The gap is meant to be visible, so this is
    # short on purpose: work sits at Shipped until the reflection runs.
    "shipped": 14,
    "learned": None,
    # Not states of work — document lifecycle statuses. The prune and health
    # loops call this script at --older-than 30d for exactly these.
    "proposed": 30,
    "in-progress": 30,
    "draft": 30,
}
# Where the age is measured from, most explicit first; mtime is the fallback
# and is reported as such, because a touched file is not a moved state.
SINCE_FIELDS = ("status-since", "since", "state-since", "updated", "last-updated")

INLINE = re.compile(r"(?:^|[\s(|*_>])status\s*::\s*([^\n|]+)", re.I)
FM_STATUS = re.compile(r"^status\s*:\s*(.+?)\s*$", re.I | re.M)


def days(v, default=None):
    if v is None:
        return default
    m = re.match(r"^\s*(\d+)\s*([dwm]?)\s*$", str(v), re.I)
    if not m:
        return default
    n, unit = int(m.group(1)), m.group(2).lower()
    return n * {"": 1, "d": 1, "w": 7, "m": 30}[unit]


def value(raw):
    """One inline field ends where the next one begins — entries are one line."""
    s = re.split(r"\s+[·•|;]\s*|\s{2,}", raw)[0]
    s = re.split(r"\s+[\w-]+\s*::", s)[0]
    return s.strip().strip("`\"'*")


def frontmatter(text):
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[3:end] if end > 0 else ""


def state_of(text):
    fm = frontmatter(text)
    m = FM_STATUS.search(fm) if fm else None
    if m:
        return value(m.group(1)), "frontmatter"
    m = INLINE.search(text)
    if m:
        return value(m.group(1)), "inline"
    return None, None


def since(path, text):
    fm = frontmatter(text)
    for name in SINCE_FIELDS:
        m = re.search(rf"(?:^|[\s(|*_>]){re.escape(name)}\s*::\s*([^\n|]+)", text, re.I)
        if not m and fm:
            m = re.search(rf"^{re.escape(name)}\s*:\s*(.+)$", fm, re.I | re.M)
        if m:
            d = parse_date(value(m.group(1)))
            if d:
                return d, name
    ts = datetime.date.fromtimestamp(path.stat().st_mtime)
    return ts, "mtime"


def _is_state_token(v):
    return bool(v) and len(v) <= MAX_STATUS_LEN and "." not in v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--older-than", default=None,
                    help="days, or 30d / 4w — overrides the per-state thresholds")
    ap.add_argument("--state", default=None, help="only this state")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    override = days(a.older_than)
    if a.older_than and override is None:
        print(f"== status scan\n   FAIL --older-than {a.older_than} is not a duration")
        return 1
    want = a.state.strip().lower() if a.state else None

    rows, unknown = [], []
    for f in walk():
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        raw, where = state_of(text)
        if not raw:
            continue
        state = raw.lower()
        if want and state != want:
            continue
        if state not in THRESHOLDS:
            unknown.append(f"{rel(f)}  status '{raw}' is not a state in system/core/STATES.md")
            continue
        cap = override if override is not None else THRESHOLDS[state]
        if cap is None:
            continue
        d, basis = since(f, text)
        age = (today() - d).days
        if age >= cap:
            rows.append({"file": rel(f), "state": raw, "days": age, "threshold": cap,
                         "since": str(d), "basis": basis, "field": where})

    rows.sort(key=lambda r: -r["days"])
    if a.json:
        print(json.dumps({"stale": rows, "unrecognised": unknown}, indent=2))
    else:
        label = f", older than {a.older_than}" if a.older_than else ""
        print(f"== status scan{label}")
        for r in rows:
            print(f"   {r['days']:>4}d  {r['state']:<14} {r['file']}"
                  f"   (since {r['since']} by {r['basis']}, cap {r['threshold']}d)")
        if not rows:
            print("   nothing has sat past its state's threshold")
        else:
            print(f"   {len(rows)} stale")
        for u in unknown:
            print(f"   -- {u}")
    return 1 if rows else 0


if __name__ == "__main__":
    sys.exit(main())
