#!/usr/bin/env python3
"""File and directory ages, counts, gaps, and archive candidates.

Counting files and measuring age is mechanics. Deciding what to archive is
judgment. This does the first so a model never does it in a prompt — including
the two questions a prompt is worst at: what has arrived since this loop last
ran, and which day of a daily series is missing. Both are answered against the
recorded run stamp rather than against "today" assumed, because cron drifts and
a loop that assumes its schedule held processes the wrong window confidently.

Usage:
  file-ages.py --dir inbox/drop --cap 7d
  file-ages.py --dir inbox --exclude planning
  file-ages.py --dir inbox/documents --oldest 20
  file-ages.py --dir workspaces --quiet-for 14d
  file-ages.py --dir workspaces --pattern possibilities --older-than 90d
  file-ages.py --dir inbox/_processed --since-last-run hero
  file-ages.py --dir system/memory/briefings --expect daily --since-last-check
  file-ages.py --file system/loops/hero/state/build-ledger.md --older-than 60d
Exit: 0 nothing flagged, 1 candidates found (a signal, not an error).
"""
import sys, json, argparse, datetime
from _lib import ROOT, rel, parse_date, parse_duration, paths_arg, load_state, today

DEFAULT_OLDER = 7
DEFAULT_CHECK_LOOP = "health"       # --since-last-check with no --loop is the health check's
MAX_GAP_WINDOW = 90                 # days; a series gap report longer than a quarter is a wall,
                                    # not a finding, so the window is clamped and says so.
STEP = {"daily": 1, "weekly": 7, "monthly": 30}


def age_days(p):
    return (datetime.datetime.now() - datetime.datetime.fromtimestamp(p.stat().st_mtime)).days


def stamp_of(loop):
    raw = load_state("last-run").get(loop)
    if not raw:
        return None
    try:
        return datetime.datetime.fromisoformat(raw)
    except ValueError:
        return None


def arrival_ts(f):
    """When a file 'arrived' for --since-last-run semantics.

    Prefer a leading YYYY-MM-DD in the filename (inbox/_processed, briefings,
    sessions) over mtime. Bulk tree copies on Windows refresh every mtime and
    otherwise flood the night packet with the whole archive as 'new'.
    """
    name = f.name
    d = parse_date(name[:10]) if len(name) >= 10 else None
    if d is not None:
        return datetime.datetime.combine(d, datetime.time(12, 0, 0)).timestamp()
    return f.stat().st_mtime


def quiet_contexts(base_spec, window, exclude, pattern):
    """Immediate subdirectories nothing has touched inside the window."""
    rows = []
    base = ROOT / base_spec.strip("/")
    if not base.is_dir():
        return rows
    for d in sorted(x for x in base.iterdir() if x.is_dir() and not x.name.startswith("_")):
        if d.name in exclude:
            continue
        files = paths_arg(dirs=[rel(d)], pattern=pattern)
        if not files:
            continue
        youngest = min(age_days(f) for f in files)
        if youngest >= window:
            rows.append({"path": rel(d), "days": youngest, "files": len(files)})
    return rows


def series_gaps(files, kind, since):
    """Missing days/weeks/months in a dated series named YYYY-MM-DD-*.md."""
    have = sorted({d for d in (parse_date(f.name[:10]) for f in files) if d})
    t = today()
    start = since.date() if since else (have[0] if have else t)
    start = max(start, t - datetime.timedelta(days=MAX_GAP_WINDOW))
    step = STEP.get(kind, 1)

    def bucket(d):
        if kind == "weekly":
            return d - datetime.timedelta(days=d.weekday())
        if kind == "monthly":
            return d.replace(day=1)
        return d

    present = {bucket(d) for d in have}
    rows, cursor, guard = [], bucket(start), 0
    while cursor <= t and guard < 400:
        guard += 1
        if cursor not in present:
            rows.append({"path": f"missing  {cursor}", "days": (t - cursor).days,
                         "missing": str(cursor)})
        cursor = (cursor + datetime.timedelta(days=32)).replace(day=1) if kind == "monthly" \
            else cursor + datetime.timedelta(days=step)
    return rows, len(have), start


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", action="append", help="directory to measure; repeatable")
    ap.add_argument("--file", action="append", help="single file to measure; repeatable")
    ap.add_argument("--quiet-contexts", help="original spelling of --quiet-for; kept working")
    ap.add_argument("--quiet-for", default=None,
                    help="window; report subdirectories of --dir untouched that long")
    ap.add_argument("--older-than", default=None, help="window (7d, 4w, 90d)")
    ap.add_argument("--cap", default=None, help="the same window, said the way a cap is said")
    ap.add_argument("--since-last-run", dest="since_last_run", default=None,
                    help="loop name; report what arrived since that loop's run stamp")
    ap.add_argument("--since-last-check", action="store_true",
                    help="same, keyed to the calling loop (--loop, default health)")
    ap.add_argument("--loop", default=None)
    ap.add_argument("--expect", choices=("daily", "weekly", "monthly"), default=None,
                    help="report gaps in a dated series named YYYY-MM-DD-*.md")
    ap.add_argument("--exclude", action="append", default=None, help="subdirectory to skip; repeatable")
    ap.add_argument("--oldest", type=int, default=None, help="return the N oldest items")
    ap.add_argument("--pattern", default=None, help="keep only paths containing this substring")
    ap.add_argument("--count", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    window = parse_duration(a.older_than if a.older_than is not None else a.cap)
    quiet = parse_duration(a.quiet_for)
    exclude = set(a.exclude or [])
    dirs = list(a.dir or [])
    if a.quiet_contexts:
        dirs.append(a.quiet_contexts)
        quiet = quiet if quiet is not None else (window if window is not None else DEFAULT_OLDER)

    since_loop = a.since_last_run or ((a.loop or DEFAULT_CHECK_LOOP) if a.since_last_check else None)
    since = stamp_of(since_loop) if since_loop else None
    label = ", ".join(dirs + (a.file or [])) or "(nothing)"

    # 1 · Gaps in a dated series.
    if a.expect:
        files = paths_arg(files=a.file, dirs=dirs, exclude=exclude, pattern=a.pattern)
        rows, found, start = series_gaps(files, a.expect, since)
        title = (f"ages ({label}, expected {a.expect} since {start}"
                 + (f", stamp {since_loop}" if since_loop else "") + ")")
        note = f"{found} file(s) present"
    # 2 · Contexts nothing has touched.
    elif quiet is not None:
        rows = []
        for d in dirs:
            rows += quiet_contexts(d, quiet, exclude, a.pattern)
        title = f"ages ({label}, quiet for {quiet}d or more)"
        note = None
    # 3 · What arrived since the stamp.
    elif since_loop:
        files = paths_arg(files=a.file, dirs=dirs, exts=None, exclude=exclude, pattern=a.pattern)
        cut = since.timestamp() if since else None
        rows = []
        for f in files:
            ts = arrival_ts(f)
            if cut is None or ts >= cut:
                # days since arrival (filename date or mtime)
                days = max(0, (datetime.datetime.now() - datetime.datetime.fromtimestamp(ts)).days)
                rows.append({"path": rel(f), "days": days})
        rows.sort(key=lambda r: r["days"])
        # Cap flood: a bulk copy or wrong stamp must not dump hundreds of lines
        # into a night packet. Over 40 → head 40 + note.
        CAP = 40
        overflow = max(0, len(rows) - CAP)
        if overflow:
            rows = rows[:CAP]
        title = (f"ages ({label}, since {since_loop} last ran"
                 + (f" {since.isoformat(sep=' ')})" if since else ", never stamped — everything)"))
        note = None if since else "no run stamp for " + since_loop + " — this is every file, not a span"
        if overflow:
            extra = f"{overflow} more omitted (cap {CAP}; filename dates preferred over mtime)"
            note = f"{note}; {extra}" if note else extra
    # 4 · What is older than the window.
    else:
        floor = window if window is not None else (0 if a.oldest else DEFAULT_OLDER)
        files = paths_arg(files=a.file, dirs=dirs, exts=None, exclude=exclude, pattern=a.pattern)
        rows = [{"path": rel(f), "days": age_days(f)} for f in files if age_days(f) >= floor]
        rows.sort(key=lambda r: -r["days"])
        title = f"ages ({label}, older than {floor}d)"
        note = None

    if a.oldest:
        rows = sorted(rows, key=lambda r: -r["days"])[:a.oldest]

    if a.json:
        print(json.dumps(rows, indent=2))
    elif a.count:
        print(f"== ages\n   {len(rows)} item(s) — {title[6:-1] if title.startswith('ages (') else title}")
    else:
        print(f"== {title}")
        if not rows:
            print("   nothing flagged")
        for r in rows:
            extra = f"  {r['files']} files" if "files" in r else ""
            print(f"   {r['days']:>4}d  {r['path']}{extra}")
        if rows:
            print(f"   {len(rows)} item(s)")
        if note:
            print(f"   ({note})")
    return 1 if rows else 0


if __name__ == "__main__":
    sys.exit(main())
