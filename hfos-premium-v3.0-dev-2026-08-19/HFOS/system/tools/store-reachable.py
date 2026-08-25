#!/usr/bin/env python3
"""Reachability precheck for the external stores.

Mounts differ between interactive and scheduled sessions. A loop that assumed
reachability once skipped its step silently for seven consecutive nights. So:
confirm before writing, and treat an unreachable store as a stated degradation
— stage the reachable half, name the placement as a human step, say so.

Reads store paths from system/adapters/<harness>.md §4. Never hard-codes them.

Repaired 2026-07-27 (first-load check): the tool tested only the host absolute
path, but in this harness shell commands run in a sandbox where mounted folders
appear under /sessions/<session>/mnt/<folder-name>. It therefore reported every
store UNREACHABLE in every sandboxed session, mounted or not — a check that can
never pass is as wrong as one that can never fail. It now also tries the
sandbox mount equivalent of each host path before declaring a store unmounted.

Usage:  store-reachable.py --all
        store-reachable.py --stores @coms @resources
        store-reachable.py --store @coms [--harness cowork] [--json]
Exit:   0 all requested stores reachable, 1 one or more unreachable.
"""
import sys, json, glob, pathlib, argparse
from _lib import adapter_stores, active_harness


def resolve_store(path: str):
    """Return the pathlib.Path where this store is reachable this session, or None.

    Tries the host path as written, then — for sandboxed sessions — each
    /sessions/*/mnt/<name> mount whose name matches a component of the host
    path, re-rooting any remaining components beneath it (so a store defined
    inside another store, e.g. @publish inside @dev, still resolves).
    """
    p = pathlib.Path(path)
    if p.is_dir():
        return p
    parts = p.parts
    for mnt in glob.glob("/sessions/*/mnt/*"):
        m = pathlib.Path(mnt)
        if m.name in parts:
            cand = m.joinpath(*parts[parts.index(m.name) + 1:])
            if cand.is_dir():
                return cand
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--harness", default=None,
                    help="adapter name; default = active_harness() from ACTIVE / HFOS_HARNESS")
    ap.add_argument("--store", action="append", help="one store; repeatable")
    ap.add_argument("--stores", action="append", nargs="+", default=None,
                    help="several stores at once, e.g. --stores @coms @resources")
    ap.add_argument("--all", action="store_true", help="every store the adapter defines")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    harness = a.harness or active_harness()
    defined = adapter_stores(harness)
    if not defined:
        print(f"== stores\n   FAIL adapter system/adapters/{harness}.md defines no stores")
        return 1

    asked = list(a.store or []) + [s for group in (a.stores or []) for s in group]
    want = list(defined) if (a.all or not asked) else list(dict.fromkeys(asked))

    results = []
    for s in want:
        path = defined.get(s)
        if path is None:
            results.append({"store": s, "reachable": False, "why": "not defined in adapter"})
            continue
        resolved = resolve_store(path)
        results.append({"store": s, "path": path, "reachable": resolved is not None,
                        "resolved": str(resolved) if resolved else None,
                        "why": "" if resolved else "not mounted this session"})

    if a.json:
        print(json.dumps(results, indent=2))
    else:
        print("== stores")
        for r in results:
            print(f"   {'ok       ' if r['reachable'] else 'UNREACHABLE'} {r['store']:<12} {r.get('path','')} {r['why']}")
    return 1 if any(not r["reachable"] for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
