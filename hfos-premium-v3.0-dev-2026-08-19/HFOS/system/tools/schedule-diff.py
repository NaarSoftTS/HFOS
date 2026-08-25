#!/usr/bin/env python3
"""What the tree says is scheduled, against what is actually installed.

The registry is the definition of record and the harness holds the live copy,
so the two drift silently — that drift is what once let five tasks run
unregistered and a health check fire nine days late while its registry row
insisted otherwise. Neither side is authoritative on its own: the live list
wins on execution state, the definitions win on intent. This only reports the
difference, because deciding which side to correct is the operator's call.

The live list is a connector's output, so a loop pipes it in rather than this
script reaching for a harness it is not allowed to know about.

Usage:
  schedule-diff.py --live live-tasks.json
  list_scheduled_tasks-output | schedule-diff.py
  schedule-diff.py                 definitions only, live side unsupplied
Exit: 0 in sync, or the live side was not supplied. 1 drift found.
"""
import re, sys, json, pathlib, argparse
from _lib import ROOT, rel, parse_date, today

DEFS = ROOT / "system" / "automations"
CRON = re.compile(r"((?:[-*/,0-9]+\s+){4}[-*/,0-9A-Za-z]+)")   # no \b: cron ends in *
SEPARATOR = re.compile(r"^\|[\s:\-|]+\|?$")
PENDING = re.compile(r"pending install", re.I)
PENDING_GRACE = 14              # days a declared "pending install" stays declared


def _stdin_has_data():
    """True only when something is actually piped in.

    `sys.stdin.isatty()` is False for any non-interactive shell, so relying on
    it alone makes this script hang whenever a loop calls it without a pipe.
    select() answers the real question: is there data to read right now.
    """
    if sys.stdin is None or sys.stdin.closed or sys.stdin.isatty():
        return False
    try:
        import select
        return bool(select.select([sys.stdin], [], [], 0.0)[0])
    except Exception:
        return False


def norm(sched):
    return " ".join(str(sched or "").replace("`", " ").split()).lower()


def schedule_in(text):
    m = re.search(r"schedule\s*::\s*([^\n|]+)", text, re.I)
    if m:
        c = CRON.search(m.group(1))
        return (c.group(1) if c else m.group(1)).strip()
    m = re.search(r"\*\*Schedule:?\*\*\s*([^\n]+)", text, re.I)
    if m:
        c = CRON.search(m.group(1))
        return (c.group(1) if c else m.group(1)).strip()
    c = CRON.search(text)
    return c.group(1).strip() if c else ""


def defined():
    """One file per task is the record. An INDEX table is the fallback shape."""
    out = []
    if not DEFS.is_dir():
        return out, f"{rel(DEFS)} does not exist yet"
    files = [f for f in sorted(DEFS.glob("*.md"))
             if f.name.upper() not in ("INDEX.MD", "README.MD")]
    for f in files:
        text = f.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"(?:^|\n)(?:name|task)\s*::\s*([^\n|]+)", text, re.I)
        out.append({"task": (m.group(1).strip() if m else f.stem),
                    "schedule": schedule_in(text), "where": rel(f),
                    "pending": pending_note(text)})
    idx = DEFS / "INDEX.md"
    if not out and idx.exists():
        lines = idx.read_text(encoding="utf-8", errors="replace").splitlines()
        for i, line in enumerate(lines):
            s = line.strip()
            if not s.startswith("|") or SEPARATOR.match(s) or s.count("|") < 3:
                continue
            nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
            if SEPARATOR.match(nxt):
                continue
            c = [x.strip().strip("`*") for x in s.strip("|").split("|")]
            out.append({"task": c[0], "schedule": schedule_in(s), "where": rel(idx),
                        "pending": pending_note(s)})
    if not out:
        return out, f"{rel(DEFS)} defines no tasks yet"
    return out, None


def pending_note(text):
    """A declared state is not drift — but a declaration has a shelf life."""
    if not PENDING.search(text):
        return None
    line = next((l for l in text.splitlines() if PENDING.search(l)), "")
    d = parse_date(line)
    age = (today() - d).days if d else None
    return {"declared": str(d) if d else "undated",
            "days": age, "stale": age is None or age > PENDING_GRACE}


def live_tasks(raw):
    data = json.loads(raw)
    if isinstance(data, dict):
        for key in ("jobs", "tasks", "scheduledTasks", "scheduled_tasks", "results", "items"):
            if isinstance(data.get(key), list):
                data = data[key]
                break
        else:
            data = [data]
    out = []
    for t in data:
        if not isinstance(t, dict):
            out.append({"task": str(t), "schedule": ""})
            continue
        # Prefer human name over opaque id (Hermes jobs have both).
        name = next((t[k] for k in ("name", "taskId", "task_id", "title", "id")
                     if t.get(k)), "(unnamed)")
        sched = next((t[k] for k in ("schedule", "schedule_display", "cron", "cron_expression",
                                     "cronExpression", "interval", "recurrence")
                      if t.get(k)), "")
        if isinstance(sched, dict):
            sched = (sched.get("expr") or sched.get("display") or sched.get("cron")
                     or sched.get("expression") or json.dumps(sched))
        out.append({"task": str(name), "schedule": str(sched),
                    "enabled": t.get("enabled", True)})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", help="JSON file holding the connector's task list")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    defs, note = defined()

    raw = None
    if a.live:
        p = ROOT / a.live                       # tree-relative first
        if not p.exists():
            p = pathlib.Path(a.live)            # then as the caller wrote it
        raw = p.read_text(encoding="utf-8") if p.exists() else None
        if raw is None:
            print(f"== schedule diff\n   FAIL live list not found at {a.live}")
            return 1
    elif _stdin_has_data():
        # Only read stdin when data is genuinely waiting. A bare `isatty()` check
        # blocks forever in any non-interactive shell — which is every context a
        # loop runs in — and a check that hangs is worse than one that is absent.
        raw = sys.stdin.read().strip() or None

    if raw is None:
        result = {"defined": defs, "live_supplied": False, "drift": []}
        if a.json:
            print(json.dumps(result, indent=2))
        else:
            print("== schedule diff")
            for d in defs:
                print(f"   defined  {d['task']:<28} {d['schedule'] or '(no schedule stated)'}"
                      f"   {d['where']}")
            if note:
                print(f"   -- {note}")
            print("   -- live task list not supplied; nothing was compared")
        return 0

    try:
        live = live_tasks(raw)
    except Exception as e:
        print(f"== schedule diff\n   FAIL live list is not readable JSON ({e})")
        return 1

    dmap = {d["task"]: d for d in defs}
    lmap = {l["task"]: l for l in live}
    drift = []

    for name, d in dmap.items():
        if name in lmap:
            continue
        if d["pending"] and not d["pending"]["stale"]:
            continue                        # declared state, inside its grace
        why = "defined, not installed"
        if d["pending"]:
            why = (f"pending install declared {d['pending']['declared']} "
                   f"({d['pending']['days']}d) — past {PENDING_GRACE}d")
        drift.append({"kind": "defined-not-live", "task": name, "why": why,
                      "defined": d["schedule"], "live": ""})

    for name, l in lmap.items():
        if name not in dmap:
            drift.append({"kind": "live-not-defined", "task": name,
                          "why": "running unregistered", "defined": "", "live": l["schedule"]})

    for name in sorted(set(dmap) & set(lmap)):
        d, l = dmap[name]["schedule"], lmap[name]["schedule"]
        if d and l and norm(d) != norm(l):
            drift.append({"kind": "schedule-mismatch", "task": name,
                          "why": "registry and live disagree", "defined": d, "live": l})

    if a.json:
        print(json.dumps({"defined": defs, "live": live, "live_supplied": True,
                          "drift": drift}, indent=2))
    else:
        print(f"== schedule diff ({len(defs)} defined, {len(live)} live)")
        for r in drift:
            print(f"   {r['kind']:<18} {r['task']:<28} {r['why']}")
            if r["defined"] or r["live"]:
                print(f"   {'':<18} defined: {r['defined'] or '-'}   live: {r['live'] or '-'}")
        if not drift:
            print("   registry matches live")
        else:
            print(f"   {len(drift)} difference(s)")
        if note:
            print(f"   -- {note}")
    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main())
