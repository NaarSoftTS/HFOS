#!/usr/bin/env python3
"""Cross-platform path router for the HFOS tree.

Agents and runbooks never hardcode host paths (drive letters, /Users/…). They use:

  tree-relative     system/memory/foo.md
  explicit tree     @tree/system/memory/foo.md
  external store    @resources/briefings/foo.md   (@dev @coms @publish)

This tool resolves those specs through _lib (ROOT from this file's location +
adapter stores from system/adapters/<ACTIVE>.md).

Usage:
  path.py root                              print tree ROOT
  path.py stores                            print adapter store map
  path.py resolve <spec> [<spec>...]        logical → absolute for this host
  path.py check <spec> [<spec>...]          exit 1 if invalid / missing
  path.py ls <spec>                         list a directory (or show a file)
  path.py find <query>                      substring or glob under tree
  path.py find <query> --under momentum/    limit scope
  path.py read <spec>                       print file text (utf-8)
  path.py read <spec> --head 40             first N lines
  path.py read <spec> --tail 20             last N lines
  path.py write <spec> --text "..."         write (tree-safe)
  path.py write <spec> --file other.md      copy text from a host path
  path.py write <spec> --append --text ...  append
  path.py stray-scan                        ~/system ~/inbox … wrong roots

Exit: 0 ok, 1 error / strays found / check failed / no find hits.
"""
import argparse, sys, json
from pathlib import Path

from _lib import (
    ROOT, resolve_spec, display_path, tree_rel_or_abs,
    adapter_stores, active_harness, scan_strays, report,
    find_paths, list_dir, read_text_file,
)


def cmd_root(_):
    print(display_path(ROOT))
    return 0


def cmd_stores(a):
    stores = adapter_stores(a.harness)
    print(f"== stores (harness={a.harness or active_harness()})")
    if not stores:
        print("   (none)")
        return 1
    for k in sorted(stores):
        print(f"   {k:<12} {stores[k]}")
    return 0


def cmd_resolve(a):
    bad = 0
    rows = []
    for spec in a.specs:
        p, kind, detail = resolve_spec(spec, harness=a.harness, must_exist=a.must_exist)
        if kind == "error" or p is None:
            bad += 1
            rows.append(f"FAIL  {spec}  ({detail})")
            continue
        abs_s = display_path(p)
        rel_s = tree_rel_or_abs(p)
        if a.json:
            rows.append({"spec": spec, "path": abs_s, "kind": kind,
                         "detail": detail, "tree_rel": rel_s if kind == "tree" else None,
                         "exists": p.exists()})
        else:
            extra = f"  [{kind}{(' ' + detail) if detail else ''}]"
            if a.verbose:
                rows.append(f"{abs_s}{extra}  <- {spec}")
            else:
                rows.append(abs_s)
    if a.json:
        print(json.dumps(rows if len(rows) != 1 else rows[0], indent=2))
    else:
        for r in rows:
            print(r)
    return 1 if bad else 0


def cmd_check(a):
    bad = 0
    print("== path check")
    for spec in a.specs:
        p, kind, detail = resolve_spec(spec, harness=a.harness, must_exist=True)
        if kind == "error" or p is None:
            print(f"   FAIL  {spec}  ({detail})")
            bad += 1
        elif kind == "host-absolute":
            print(f"   FAIL  {spec}  (host absolute outside tree/stores — use @store or tree-relative)")
            bad += 1
        else:
            print(f"   ok    {spec}  ->  {tree_rel_or_abs(p) if kind == 'tree' else display_path(p)}")
    return 1 if bad else 0


def cmd_ls(a):
    rows, kind, detail = list_dir(a.spec, harness=a.harness, max_entries=a.max)
    if rows is None:
        print(f"   FAIL ls {a.spec}: {detail}")
        return 1
    if a.json:
        print(json.dumps({"spec": a.spec, "kind": kind, "detail": detail, "entries": rows}, indent=2))
        return 0
    print(f"== ls {a.spec}  [{kind}{(' ' + detail) if detail else ''}]")
    for r in rows:
        if r.get("dir"):
            print(f"   {r['name']:<40}  {r.get('rel') or r['path']}")
        else:
            b = r.get("bytes")
            print(f"   {r['name']:<40}  {b:>8}B  {r.get('rel') or r['path']}")
    print(f"   {len(rows)} entr(y/ies)")
    return 0


def cmd_find(a):
    hits, err = find_paths(
        a.query, under=a.under, max_results=a.max,
        files_only=not a.include_dirs, harness=a.harness,
    )
    if err:
        print(f"   FAIL find: {err}")
        return 1
    if a.json:
        print(json.dumps(hits, indent=2))
        return 0 if hits else 1
    scope = a.under or "@tree"
    print(f"== find {a.query!r}  under {scope}")
    if not hits:
        print("   nothing matched")
        return 1
    for h in hits:
        kind = "dir " if h["dir"] else "file"
        b = "" if h["bytes"] is None else f"{h['bytes']}B"
        print(f"   {kind}  {h['rel']:<56}  {b}")
    print(f"   {len(hits)} hit(s)")
    return 0


def cmd_read(a):
    text, kind, detail = read_text_file(
        a.spec, harness=a.harness, max_bytes=a.max_bytes,
        head=a.head, tail=a.tail,
    )
    if text is None:
        print(f"   FAIL read {a.spec}: {detail}", file=sys.stderr)
        return 1
    # meta on stderr so stdout is pure content for pipes
    if a.meta or a.json:
        p, _, _ = resolve_spec(a.spec, harness=a.harness)
        meta = {
            "spec": a.spec,
            "path": display_path(p) if p else None,
            "kind": kind,
            "bytes": len(text.encode("utf-8")),
            "lines": text.count("\n") + (0 if text.endswith("\n") or not text else 1),
        }
        if a.json:
            print(json.dumps({**meta, "text": text}, indent=2))
            return 0
        print(f"# {meta['path']}  [{kind}]  {meta['bytes']}B  ~{meta['lines']} lines", file=sys.stderr)
    sys.stdout.write(text)
    if text and not text.endswith("\n"):
        sys.stdout.write("\n")
    return 0


def cmd_write(a):
    p, kind, detail = resolve_spec(a.spec, harness=a.harness)
    if kind == "error" or p is None:
        print(f"   FAIL resolve {a.spec}: {detail}")
        return 1
    if kind == "host-absolute":
        print(f"   FAIL refuse host-absolute outside tree/stores: {a.spec}")
        return 1
    if kind == "store":
        if not p.parent.exists() and not a.makedirs:
            print(f"   FAIL parent missing for store path (create store or pass --makedirs): {display_path(p.parent)}")
            return 1
    if a.file:
        src = Path(a.file)
        # allow logical --file too
        sp, sk, sd = resolve_spec(a.file, harness=a.harness)
        if sk != "error" and sp is not None and sk != "host-absolute" and sp.exists():
            src = sp
        data = src.read_bytes()
        text = data.decode("utf-8")
    elif a.text is not None:
        text = a.text
        if a.newline and not text.endswith("\n"):
            text += "\n"
    else:
        if sys.stdin.isatty() and not a.force_stdin:
            print("   FAIL write needs stdin, --text, or --file")
            return 1
        text = sys.stdin.read()
    if a.makedirs or kind == "tree":
        p.parent.mkdir(parents=True, exist_ok=True)
    if a.append:
        with p.open("a", encoding="utf-8", newline="\n") as f:
            f.write(text)
        op = "appended"
    else:
        p.write_text(text, encoding="utf-8", newline="\n")
        op = "wrote"
    print(f"== {op}\n   {display_path(p)}\n   {len(text.encode('utf-8'))} bytes  kind={kind}")
    return 0


def cmd_stray_scan(a):
    found = scan_strays(max_files=a.max_files)
    if a.json:
        print(json.dumps(found, indent=2))
        return 1 if found else 0
    rows = [f"{s['rel_home']}  ({s['bytes']}B)" for s in found]
    n = report("stray scan (~/system, ~/inbox, …)", rows, "no home-level tree mirrors")
    if found and not a.quiet_ok:
        print("   tip: compare to tree, move keepers via path.py write / cp into ROOT, then rm strays")
    return 1 if n else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--harness", default=None, help="adapter override (default ACTIVE / HFOS_HARNESS)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("root", help="print tree ROOT")
    p.set_defaults(func=cmd_root)

    p = sub.add_parser("stores", help="print adapter store map")
    p.set_defaults(func=cmd_stores)

    p = sub.add_parser("resolve", help="logical/tree path → absolute for this host")
    p.add_argument("specs", nargs="+")
    p.add_argument("--must-exist", action="store_true")
    p.add_argument("--json", action="store_true")
    p.add_argument("-v", "--verbose", action="store_true")
    p.set_defaults(func=cmd_resolve)

    p = sub.add_parser("check", help="validate specs resolve + exist")
    p.add_argument("specs", nargs="+")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("ls", help="list directory (logical path)")
    p.add_argument("spec")
    p.add_argument("--max", type=int, default=200)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_ls)

    p = sub.add_parser("find", help="find files by substring or glob")
    p.add_argument("query")
    p.add_argument("--under", default=None, help="limit to a logical/tree path")
    p.add_argument("--max", type=int, default=40)
    p.add_argument("--include-dirs", action="store_true")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_find)

    p = sub.add_parser("read", help="read text file via logical path")
    p.add_argument("spec")
    p.add_argument("--head", type=int, default=None)
    p.add_argument("--tail", type=int, default=None)
    p.add_argument("--max-bytes", type=int, default=200_000)
    p.add_argument("--meta", action="store_true", help="print path meta on stderr")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_read)

    p = sub.add_parser("write", help="write content to a resolved path (safe rooting)")
    p.add_argument("spec")
    p.add_argument("--text", default=None)
    p.add_argument("--file", default=None, help="read content from host or logical path")
    p.add_argument("--append", action="store_true")
    p.add_argument("--newline", action="store_true", help="ensure trailing newline on --text")
    p.add_argument("--makedirs", action="store_true", help="create parents for store paths too")
    p.add_argument("--force-stdin", action="store_true")
    p.set_defaults(func=cmd_write)

    p = sub.add_parser("stray-scan", help="detect ~/system ~/inbox … mistaken writes")
    p.add_argument("--json", action="store_true")
    p.add_argument("--max-files", type=int, default=200)
    p.add_argument("--quiet-ok", action="store_true")
    p.set_defaults(func=cmd_stray_scan)

    a = ap.parse_args()
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
