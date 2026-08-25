#!/usr/bin/env python3
"""Put the saved briefing on the surface a person actually reads — or refuse to.

The surface lives outside the tree, and mounts differ between interactive and
scheduled sessions: the store that is there when someone runs this by hand is
sometimes absent at 4 AM. A renderer that wrote blindly into an absent mount
would create a directory where the mount point should be, report success, and
leave the person reading a stale surface — which is the failure that once ran
silently for seven consecutive nights.

So this refuses. When the store is unreachable it writes nothing, prints the
staging instruction, and exits 1 so the loop records an un-rendered surface as
an explicit human step. **The refusal is the point of the script**; copying a
file is the easy half.

The store is resolved through system/adapters/ the same way store-reachable.py
resolves it — one adapter, one place where an absolute path is ever named.

Usage:
  render-briefing.py
  render-briefing.py --source system/memory/briefings/2026-07-27-morning.md
  render-briefing.py --dest "@resources/briefings/2026-07-27-morning.md"
Exit: 0 rendered, 1 nothing to render or the store was unreachable (a stated
      degradation, not a crash).
"""
import sys, pathlib, argparse
from _lib import ROOT, adapter_stores, active_harness, today

BRIEFINGS = "system/memory/briefings"
SUFFIX = "-morning.md"                  # the name the briefing runbook writes
DEFAULT_DEST_DIR = "@resources/briefings"


def default_source():
    return f"{BRIEFINGS}/{today()}{SUFFIX}"


def split_dest(dest):
    """'@store/some/path' -> ('@store', 'some/path')."""
    d = dest.strip().strip("/")
    if not d.startswith("@"):
        return None, d
    head, _, tail = d.partition("/")
    return head, tail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=None, help=f"tree-relative; default {BRIEFINGS}/<today>{SUFFIX}")
    ap.add_argument("--dest", default=None, help=f"<@store>/<path>; default {DEFAULT_DEST_DIR}/<filename>")
    ap.add_argument("--harness", default=None,
                    help="adapter name; default = active_harness() from ACTIVE / HFOS_HARNESS")
    a = ap.parse_args()

    harness = a.harness or active_harness()
    src_spec = (a.source or default_source()).strip("/")
    src = ROOT / src_spec
    print("== render briefing")

    if not src.is_file():
        print(f"   FAIL no briefing at {src_spec} — nothing to render")
        print("   The briefing file is the deliverable; the surface is the convenience.")
        return 1

    store, tail = split_dest(a.dest or f"{DEFAULT_DEST_DIR}/{src.name}")
    if store is None:
        print(f"   FAIL --dest must name a logical store, e.g. {DEFAULT_DEST_DIR}/{src.name}")
        return 1

    defined = adapter_stores(harness)
    root = defined.get(store)
    if root is None:
        print(f"   FAIL {store} is not defined in system/adapters/{harness}.md")
        return 1

    base = pathlib.Path(root)
    if not base.is_dir():
        # The refusal. Nothing is written, and the human step is named.
        print(f"   UNREACHABLE {store} is not mounted this session — nothing was written")
        print(f"   STAGE       the briefing stands at {src_spec}")
        print(f"   HUMAN STEP  copy it to {store}/{tail} when the store is back")
        print("   Record the un-rendered surface in the briefing rather than reporting it rendered.")
        return 1

    target = base / tail
    if target.is_dir():
        target = target / src.name
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    except Exception as e:
        print(f"   FAIL could not write to {store}/{tail}: {e.__class__.__name__}")
        print(f"   STAGE       the briefing stands at {src_spec}")
        print(f"   HUMAN STEP  place it at {store}/{tail} by hand")
        return 1

    shown = f"{store}/{tail}" if not tail.endswith("/") else f"{store}/{tail}{src.name}"
    print(f"   rendered    {src_spec}  ->  {shown}")
    print(f"   pointer     optional row under @resources/exports/ — body in {store}; prefer real files under exports/<workspace>/ when shipping artifacts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
