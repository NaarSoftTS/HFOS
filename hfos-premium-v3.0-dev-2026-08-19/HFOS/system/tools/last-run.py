#!/usr/bin/env python3
"""When did this loop actually last run?

Cron fires drift — by minutes usually, by nine days once. A loop that assumes
its schedule held will process the wrong window and report success. So every
loop reads its own last actual run stamp instead of trusting the cadence.

Usage:
  last-run.py --loop board                 report last run + elapsed
  last-run.py --loop briefing --loop hero --loop sweep --loop board
  last-run.py --loop board --write         record a run now
  last-run.py --all                        every loop, with overdue flags
  last-run.py --loop hero --check-window --after board --minutes 30
Exit: 0 ok, 1 overdue / window not satisfied.
"""
import sys, json, argparse, datetime
from _lib import load_state, save_state

STATE = "last-run"
# cadence in hours; None = irregular
EXPECTED = {"sweep": 24, "hero": 24, "briefing": 24,
            "prune": 24 * 7, "health": 24 * 31}
# Overnight chain (2026-08-03): sweep → hero → briefing. Daily board retired.
# --check-window with no --after asks about the link immediately upstream.
PRECEDES = {"hero": "sweep", "briefing": "hero"}


def now():
    return datetime.datetime.now().replace(microsecond=0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--loop", action="append", help="loop name; repeatable")
    ap.add_argument("--stamp", action="store_true")
    ap.add_argument("--write", action="store_true", help="the same thing --stamp does")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--check-window", action="store_true")
    ap.add_argument("--after"); ap.add_argument("--minutes", type=int, default=30)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    loops = a.loop or []
    s = load_state(STATE)

    if a.stamp or a.write:
        if not loops:
            print("   FAIL --write needs --loop"); return 1
        for name in loops:
            s[name] = now().isoformat()
        save_state(STATE, s)
        print("== last-run")
        for name in loops:
            print(f"   stamped {name} at {s[name]}")
        return 0

    def entry(name):
        raw = s.get(name)
        if not raw:
            return {"loop": name, "last_run": None, "hours_since": None,
                    "overdue": True, "note": "never recorded"}
        t = datetime.datetime.fromisoformat(raw)
        h = round((now() - t).total_seconds() / 3600, 1)
        exp = EXPECTED.get(name)
        return {"loop": name, "last_run": raw, "hours_since": h,
                "overdue": bool(exp and h > exp * 1.5),
                "note": "" if not exp else f"expected every {exp}h"}

    if a.check_window:
        if not loops:
            print("   FAIL --check-window needs --loop"); return 1
        this = loops[0]
        after = a.after or PRECEDES.get(this)
        if not after:
            print(f"== window\n   FAIL {this} has no upstream loop — name one with --after")
            return 1
        prior = entry(after)
        if not prior["last_run"]:
            print(f"== window\n   FAIL {after} has no recorded run — {this} runs without its input")
            return 1
        gap = (now() - datetime.datetime.fromisoformat(prior["last_run"])).total_seconds() / 60
        ok = gap >= a.minutes
        print(f"== window\n   {'ok  ' if ok else 'FAIL'} {after} finished {gap:.0f}m ago "
              f"(need {a.minutes}m before {this})")
        return 0 if ok else 1

    rows = [entry(n) for n in (EXPECTED if a.all or not loops else loops)]
    if a.json:
        print(json.dumps(rows, indent=2))
    else:
        print("== last run")
        for r in rows:
            flag = "OVERDUE" if r["overdue"] else "ok     "
            since = f"{r['hours_since']}h ago" if r["hours_since"] is not None else "never"
            print(f"   {flag} {r['loop']:<10} {since:<14} {r['note']}")
    return 1 if any(r["overdue"] for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
