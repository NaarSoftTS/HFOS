#!/usr/bin/env python3
"""No host-specific path may exist outside system/adapters/.

This is harness-contract violation #3, closed by construction and kept closed
by this script. The tree names external stores logically (@resources, @dev,
@coms, @publish); the adapter resolves them. That indirection is the entire
mechanism that lets a self-contained client install run the identical tree.

Usage:  check-paths.py
Exit:   0 clean, 1 violations.
"""
import re, sys
from _lib import walk, rel, report

ALLOWED_PREFIX = "system/adapters/"
PATTERNS = [
    (re.compile(r"/Users/[A-Za-z0-9._-]+/"), "absolute user path"),
    (re.compile(r"/home/[A-Za-z0-9._-]+/"), "absolute home path"),
    (re.compile(r"[A-Z]:\\\\"), "absolute Windows path"),
    (re.compile(r"CloudStorage[/\\]Dropbox"), "named cloud provider"),
    # Invariant 6 is about meaning, not syntax. A bare store name outside the
    # adapter is a host detail even without a leading slash — it is exactly the
    # form that slipped past the /Users/ pattern.
    (re.compile(r"(?<![\w@/`-])AIOS-Resources/"), "store named directly (use @resources)"),
    (re.compile(r"(?<![\w@/`-])HFOS-Resources/"), "store named directly (use @resources)"),
    (re.compile(r"(?<![\w@/`-])AIOS Resources/"), "store named directly (use @resources)"),
    (re.compile(r"(?<![\w@/`-])HFOS Resources/"), "store named directly (use @resources)"),
    (re.compile(r"(?<![\w@/`-])DevProjects/"), "store named directly (use @dev)"),
    (re.compile(r"(?<![\w@/`-])AIComs/"), "store named directly (use @coms)"),   # split so this line is not its own finding
]


def main():
    bad = []
    for f in walk(exts=(".md", ".py", ".html")):
        r = rel(f)
        if r.startswith(ALLOWED_PREFIX) or r == "system/tools/check-paths.py":
            continue   # a scanner's own patterns are not violations
        try:
            lines = f.read_text(encoding="utf-8").splitlines()
        except Exception:
            continue
        for i, line in enumerate(lines, 1):
            for rx, label in PATTERNS:
                if rx.search(line):
                    bad.append(f"{r}:{i}  [{label}]  {line.strip()[:90]}")
                    break

    n = report("host-path scan", sorted(bad), "no host paths outside system/adapters/")
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
