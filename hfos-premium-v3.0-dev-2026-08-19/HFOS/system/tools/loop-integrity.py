#!/usr/bin/env python3
"""Artifact-backed completion check for overnight loops.

last-run stamps alone are not proof a loop ran — a [SILENT] cron tick can stamp
without writing a session record. This tool checks:

  1. Required artifacts exist for the loop (today's date unless --date)
  2. If a last-run stamp is fresh, at least one artifact mtime is near that stamp
  3. Optional: latest Hermes cron output for the job does not end in [SILENT]
  4. Optional: path.py stray-scan clean

Usage:
  loop-integrity.py --loop sweep
  loop-integrity.py --loop hero --loop briefing
  loop-integrity.py --all
  loop-integrity.py --loop sweep --json
  loop-integrity.py --loop sweep --require-fresh   # fail if stamp missing/old

Exit: 0 all ok, 1 one or more failures.
"""
import argparse, sys, os, re, json, datetime
from pathlib import Path

from _lib import ROOT, load_state, display_path, scan_strays, active_harness

TODAY = datetime.date.today().isoformat()

# Required artifacts relative to ROOT. {date} filled at runtime.
ARTIFACTS = {
    "sweep": [
        "system/memory/sessions/{date}-sweep.md",
        # PM / extra records still count as evidence when primary missing name
        "system/memory/sessions/{date}-sweep-pm.md",
    ],
    "hero": [
        "system/memory/dispatches/{date}.md",
        "system/memory/sessions/{date}-hero.md",
    ],
    "briefing": [
        "system/memory/briefings/{date}-morning.md",
    ],
}

# Any one of the listed globs/paths is enough for "artifact exists"
ANY_OF = {
    "sweep": True,   # sweep.md OR sweep-pm.md
    "hero": False,   # dispatch required; session encouraged
    "briefing": False,
}

HERO_REQUIRE = ["system/memory/dispatches/{date}.md"]  # hard required subset

# Cron job name → id is discovered from jobs.json when present
CRON_NAMES = {
    "sweep": "nightly-sweep",
    "hero": "action-hero",
    "briefing": "morning-briefing",
}

SILENT_RE = re.compile(r"^\s*\[SILENT\]\s*$", re.M)
FRESH_HOURS = 36  # within expected daily cadence slack


def now():
    return datetime.datetime.now().replace(microsecond=0)


def parse_stamp(raw):
    if not raw:
        return None
    try:
        return datetime.datetime.fromisoformat(raw)
    except Exception:
        return None


def hermes_home():
    env = os.environ.get("HERMES_HOME")
    if env and Path(env).is_dir():
        return Path(env)
    # Common Windows profile layout for this install
    local = os.environ.get("LOCALAPPDATA")
    if local:
        p = Path(local) / "hermes" / "profiles" / "aios"
        if p.is_dir():
            return p
    return None


def latest_cron_output(loop):
    """Return Path to newest cron output md for this loop, or None."""
    hh = hermes_home()
    if not hh:
        return None
    jobs_path = hh / "cron" / "jobs.json"
    out_root = hh / "cron" / "output"
    if not out_root.is_dir():
        return None
    job_id = None
    name = CRON_NAMES.get(loop)
    if jobs_path.is_file() and name:
        try:
            data = json.loads(jobs_path.read_text(encoding="utf-8"))
            jobs = data.get("jobs", data if isinstance(data, list) else [])
            for j in jobs:
                if j.get("name") == name:
                    job_id = j.get("id") or j.get("job_id")
                    break
        except Exception:
            pass
    candidates = []
    if job_id and (out_root / str(job_id)).is_dir():
        candidates = list((out_root / str(job_id)).glob("*.md"))
    else:
        # search all
        candidates = list(out_root.glob("*/*.md"))
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    # Prefer files whose name starts with today's date when possible
    return candidates[0]


def check_loop(loop, date, require_fresh=False, check_silent=True, check_stray=False):
    issues = []
    notes = []
    state = load_state("last-run")
    stamp_raw = state.get(loop)
    stamp = parse_stamp(stamp_raw)
    hours = None
    if stamp:
        hours = round((now() - stamp).total_seconds() / 3600, 2)

    # --- artifacts ---
    specs = ARTIFACTS.get(loop, [])
    if not specs:
        issues.append(f"unknown loop {loop}")
        return {"loop": loop, "ok": False, "issues": issues, "notes": notes,
                "stamp": stamp_raw, "hours_since": hours}

    existing = []
    missing = []
    for spec in specs:
        rel = spec.format(date=date)
        p = ROOT / rel
        if p.is_file():
            existing.append({
                "path": rel,
                "mtime": datetime.datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec="seconds"),
                "bytes": p.stat().st_size,
            })
        else:
            missing.append(rel)

    if loop == "hero":
        hard = [s.format(date=date) for s in HERO_REQUIRE]
        if not any((ROOT / h).is_file() for h in hard):
            issues.append(f"missing required dispatch: {hard[0]}")
    elif loop == "briefing":
        if not existing:
            issues.append(f"missing briefing artifact for {date}")
    elif loop == "sweep":
        if not existing:
            issues.append(f"missing sweep session record for {date} (tried sweep.md and sweep-pm.md)")

    # --- stamp vs artifact coherence ---
    if stamp is None:
        if require_fresh:
            issues.append("no last-run stamp")
        else:
            notes.append("no last-run stamp (ok if not written yet)")
    else:
        if require_fresh and hours is not None and hours > FRESH_HOURS:
            issues.append(f"stamp stale ({hours}h > {FRESH_HOURS}h)")
        if existing and hours is not None and hours < FRESH_HOURS:
            # at least one artifact should be within 6h of stamp (or newer)
            stamp_ts = stamp.timestamp()
            near = False
            for e in existing:
                p = ROOT / e["path"]
                mt = p.stat().st_mtime
                # artifact within 6h before stamp or any time after stamp-1h
                if abs(mt - stamp_ts) <= 6 * 3600 or mt >= stamp_ts - 3600:
                    near = True
                    break
            if not near:
                issues.append(
                    "false-fresh risk: last-run stamp is recent but no artifact mtime is near it "
                    f"(stamp={stamp_raw}; artifacts={[e['path'] for e in existing]})"
                )
        if not existing and hours is not None and hours < FRESH_HOURS:
            issues.append(
                f"false-fresh: stamp {stamp_raw} ({hours}h ago) but no {date} artifacts on disk"
            )

    # --- SILENT cron output ---
    if check_silent:
        latest = latest_cron_output(loop)
        if latest and latest.is_file():
            try:
                text = latest.read_text(encoding="utf-8", errors="replace")
                cron_mtime = latest.stat().st_mtime
            except Exception:
                text = ""
                cron_mtime = 0
            notes.append(f"cron output checked: {latest.name}")
            if "## Response" in text:
                body = text.split("## Response", 1)[-1].strip()
                is_silent = body == "[SILENT]" or (
                    body.startswith("[SILENT]") and len(body) < 40
                )
                if is_silent:
                    # Recovered if a required artifact is newer than this SILENT tick
                    recovered = any(
                        (ROOT / e["path"]).stat().st_mtime > cron_mtime + 30
                        for e in existing
                    )
                    if recovered:
                        notes.append(
                            f"older cron [SILENT] superseded by newer artifacts ({latest.name})"
                        )
                    elif hours is not None and hours < FRESH_HOURS:
                        issues.append(
                            f"cron output is [SILENT] while stamp fresh and no newer artifact: "
                            f"{display_path(latest)}"
                        )
                    else:
                        notes.append(f"latest cron output is [SILENT]: {display_path(latest)}")
        else:
            notes.append("cron output not found (skip SILENT check)")

    # --- strays ---
    if check_stray:
        strays = scan_strays(max_files=50)
        if strays:
            issues.append(f"{len(strays)} home-level stray file(s) (path.py stray-scan)")

    return {
        "loop": loop,
        "ok": not issues,
        "issues": issues,
        "notes": notes,
        "stamp": stamp_raw,
        "hours_since": hours,
        "artifacts": existing,
        "missing": missing,
        "date": date,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--loop", action="append", dest="loops", help="sweep|hero|briefing; repeatable")
    ap.add_argument("--all", action="store_true", help="sweep + hero + briefing")
    ap.add_argument("--date", default=TODAY, help="artifact date YYYY-MM-DD (default today)")
    ap.add_argument("--require-fresh", action="store_true", help="fail if stamp missing or >36h")
    ap.add_argument("--no-silent-check", action="store_true")
    ap.add_argument("--stray-scan", action="store_true", help="also fail on home-level strays")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    loops = list(a.loops or [])
    if a.all:
        loops = ["sweep", "hero", "briefing"]
    if not loops:
        print("   FAIL need --loop or --all")
        return 1

    results = [
        check_loop(
            loop, a.date,
            require_fresh=a.require_fresh,
            check_silent=not a.no_silent_check,
            check_stray=a.stray_scan,
        )
        for loop in loops
    ]

    if a.json:
        print(json.dumps(results if len(results) != 1 else results[0], indent=2))
    else:
        print("== loop integrity")
        print(f"   date={a.date}  harness={active_harness()}  root={display_path(ROOT)}")
        for r in results:
            flag = "ok  " if r["ok"] else "FAIL"
            age = f"{r['hours_since']}h" if r["hours_since"] is not None else "—"
            print(f"   {flag}  {r['loop']:<10}  stamp={r['stamp'] or '—'}  age={age}")
            for e in r["artifacts"]:
                print(f"          artifact  {e['path']}  ({e['bytes']}B, mtime {e['mtime']})")
            for m in r["missing"]:
                print(f"          missing   {m}")
            for i in r["issues"]:
                print(f"          issue     {i}")
            for n in r["notes"]:
                print(f"          note      {n}")
        bad = sum(1 for r in results if not r["ok"])
        print(f"   {bad} failure(s)" if bad else "   all loops coherent")

    return 0 if all(r["ok"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
