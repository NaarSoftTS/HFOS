"""Shared helpers. Tree root is resolved from this file's location — no absolute paths anywhere."""
import pathlib, datetime, json, re, os

ROOT = pathlib.Path(__file__).resolve().parents[2]
STATE = ROOT / "system" / "memory" / "_tool-state"
SKIP_DIRS = {".git", ".obsidian", "Claude", "_archive", "node_modules", "__pycache__", ".venv"}

DURATION = re.compile(r"^\s*(\d+)\s*([hdwmy]?)\s*$", re.I)
UNIT_DAYS = {"": 1, "d": 1, "w": 7, "m": 30, "y": 365}

# Store rows in system/adapters/<harness>.md section 4:  | `@name` | `path` | ... |
STORE_ROW = re.compile(r"^\|\s*`(@\w+)`\s*\|\s*`([^`]+)`\s*\|")


def active_harness():
    """Which adapter this install is running under.

    Resolution order (first hit wins):
      1. HFOS_HARNESS env var
      2. system/adapters/ACTIVE  (one word: hermes | cowork | …)
      3. \"cowork\" — historical default for the Mac primary

    Per-call --harness still overrides. ACTIVE is how a dual-harness setup
    (Hermes here, Cowork on the Mac) keeps tools pointed at the right stores
    without every runbook hard-coding a flag.
    """
    env = (os.environ.get("HFOS_HARNESS") or "").strip().lower()
    if env:
        return env
    active = ROOT / "system" / "adapters" / "ACTIVE"
    if active.is_file():
        raw = active.read_text(encoding="utf-8", errors="replace").strip().splitlines()
        if raw:
            word = raw[0].strip().lower().strip("`*")
            if word and not word.startswith("#"):
                return word
    return "cowork"


def walk(exts=(".md",), under=None):
    base = ROOT / under if under else ROOT
    if not base.exists():
        return
    for p in base.rglob("*"):
        if not p.is_file() or p.suffix not in exts:
            continue
        if SKIP_DIRS & set(p.relative_to(ROOT).parts):
            continue
        yield p


def rel(p):
    # Always forward slashes so prefix checks (exemptions, registries) match on Windows.
    return str(pathlib.Path(p).resolve().relative_to(ROOT)).replace("\\", "/")


def today():
    return datetime.date.today()


def parse_date(s):
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", str(s))
    if not m:
        return None
    try:
        return datetime.date(*map(int, m.groups()))
    except ValueError:
        return None


def parse_duration(v, default=None):
    """A window, written the way the runbooks say it, resolved to whole days.

    "7d" -> 7, "4w" -> 28, "30" -> 30, "24h" -> 1. Hours round up, because
    nothing here is checked at a resolution finer than a day and a window that
    silently rounded to zero would report everything as current. Unparseable
    input returns the default rather than raising: a window is an argument to a
    check, and a bad argument must not take the check down.
    """
    if v is None or isinstance(v, bool):
        return default
    if isinstance(v, int):
        return v
    m = DURATION.match(str(v))
    if not m:
        return default
    n, unit = int(m.group(1)), m.group(2).lower()
    if unit == "h":
        return -(-n // 24)                      # ceiling: any part of a day is a day
    return n * UNIT_DAYS[unit]


def paths_arg(files=None, dirs=None, exts=(".md",), exclude=(), pattern=None):
    """Resolve repeatable --file / --dir arguments into the files that exist.

    A path that does not exist yields nothing instead of an error. Most of this
    tree's content has not been written yet, and a tool that died on an
    unmigrated path would make the runbook calling it unrunnable — a worse
    failure than the empty answer, because a dead tool teaches a loop to skip it.

    exts=None means every file. exclude names directories to skip anywhere in
    the path. pattern keeps only paths containing that substring.
    """
    out, seen = [], set()

    def keep(f):
        parts = f.relative_to(ROOT).parts
        if SKIP_DIRS & set(parts) or set(exclude) & set(parts):
            return False
        if f.name.startswith("."):
            return False
        if exts and f.suffix not in exts:
            return False
        if pattern and pattern not in str(f.relative_to(ROOT)):
            return False
        return True

    for spec in list(files or []) + list(dirs or []):
        s = str(spec).strip().strip("/")
        if not s:
            continue
        p = ROOT / s
        if p.is_dir():
            found = sorted(x for x in p.rglob("*") if x.is_file() and keep(x))
        elif p.is_file():
            found = [p] if (not pattern or pattern in s) else []
        else:
            found = []
        for f in found:
            k = str(f)
            if k not in seen:
                seen.add(k)
                out.append(f)
    return out


def adapter_stores(harness=None):
    """The logical store names, resolved through system/adapters/ and nowhere else.

    Every tool that touches an external store reads it from here, so the
    absolute location of a store is still named exactly once in the whole tree.
    harness=None → active_harness() (ACTIVE file / HFOS_HARNESS / cowork).
    """
    if harness is None:
        harness = active_harness()
    f = ROOT / "system" / "adapters" / f"{harness}.md"
    if not f.exists():
        return {}
    out = {}
    for line in f.read_text(encoding="utf-8").splitlines():
        m = STORE_ROW.match(line.strip())
        if m:
            out[m.group(1)] = m.group(2)
    for k, v in list(out.items()):              # resolve one level of indirection
        for other in out:
            if v.startswith(other + "/"):
                out[k] = out[other] + v[len(other):]
    return out


# ---------------------------------------------------------------------------
# Logical path router (cross-platform)
#
# Grammar agents and runbooks use — never host absolutes outside adapters:
#   system/memory/foo.md     tree-relative  → ROOT / …
#   @tree/system/memory/foo  explicit tree  → ROOT / …
#   @resources/briefings/x   external store → adapter path / …
#   @dev @coms @publish      same
#
# Scripts always resolve via resolve_spec(). Hermes write_file on some hosts
# ignores cwd; agents call `path.py resolve` / `path.py write` instead of
# hardcoding host drive letters or /Users/….
# ---------------------------------------------------------------------------

HOST_ABS = re.compile(
    r"^(?:"
    r"[A-Za-z]:[\\/]"           # Windows drive
    r"|/"                       # POSIX absolute
    r"|\\\\"                    # UNC
    r")"
)
# git-bash / MSYS: /c/Users/... → C:/Users/...
MSYS_DRIVE = re.compile(r"^/([A-Za-z])/(.*)$")
LOGICAL_STORE = re.compile(r"^@([A-Za-z][\w-]*)(?:/(.*))?$")


def _norm_rel(s):
    """Forward-slash relative form; strip leading ./ and empty segments."""
    s = str(s).replace("\\", "/").strip()
    while s.startswith("./"):
        s = s[2:]
    return "/".join(p for p in s.split("/") if p not in ("", "."))


def _strip_wrappers(raw):
    """Strip quotes, backticks, wikilink brackets agents paste from markdown."""
    s = str(raw).strip()
    # repeat a few times for nested `[[path]]`
    for _ in range(3):
        prev = s
        s = s.strip().strip("`").strip('"').strip("'")
        if len(s) >= 4 and s.startswith("[[") and s.endswith("]]"):
            s = s[2:-2].strip()
        # wikilink with display: [[path|label]] → path
        if "|" in s and not s.startswith("@"):
            # only split when it looks like a wikilink path, not a Windows drive
            left, _, _right = s.partition("|")
            if left and not HOST_ABS.match(left) and "://" not in left:
                # prefer left if it looks like a path
                if "/" in left or left.endswith(".md") or left.startswith("@"):
                    s = left.strip()
        if s == prev:
            break
    return s


def _msys_to_windows(raw):
    """Map /c/Users/... → C:/Users/... when that form is in play (git-bash)."""
    s = raw.replace("\\", "/")
    m = MSYS_DRIVE.match(s)
    if not m:
        return raw
    drive, rest = m.group(1).upper(), m.group(2)
    return f"{drive}:/{rest}"


def resolve_spec(spec, harness=None, must_exist=False):
    """Resolve a logical or tree-relative path to an absolute pathlib.Path.

    Returns (path, kind, detail) where kind is one of:
      tree | store | host-absolute | error
    detail is @name for stores, error message for error, else ''.
    Does not create files. Rejects escaping the tree for tree-relative specs.
    """
    raw = _strip_wrappers(spec)
    if not raw:
        return None, "error", "empty path"

    # ~ and ~/… — expand against user home, then re-classify
    if raw == "~" or raw.startswith("~/") or raw.startswith("~\\"):
        try:
            expanded = str(pathlib.Path(raw).expanduser())
        except Exception as e:
            return None, "error", f"unresolvable home path: {e}"
        return resolve_spec(expanded, harness=harness, must_exist=must_exist)

    # git-bash / MSYS absolute
    if raw.startswith("/") and MSYS_DRIVE.match(raw.replace("\\", "/")):
        raw = _msys_to_windows(raw)

    # Already absolute host path — allow only if under ROOT or a known store.
    if HOST_ABS.match(raw) or (len(raw) > 1 and raw[1] == ":"):
        try:
            p = pathlib.Path(raw).expanduser().resolve()
        except Exception as e:
            return None, "error", f"unresolvable host path: {e}"
        try:
            p.relative_to(ROOT.resolve())
            if must_exist and not p.exists():
                return p, "error", "path does not exist"
            return p, "tree", ""
        except ValueError:
            pass
        for name, base in adapter_stores(harness).items():
            try:
                bp = pathlib.Path(base).expanduser().resolve()
                if not bp.exists():
                    # still allow classification under configured store root
                    try:
                        pathlib.Path(os.path.normpath(str(p))).resolve().relative_to(bp)
                    except Exception:
                        # compare string prefix when store not mounted
                        bp_s = display_path(bp).rstrip("/").lower()
                        p_s = display_path(p).rstrip("/").lower()
                        if p_s == bp_s or p_s.startswith(bp_s + "/"):
                            if must_exist and not p.exists():
                                return p, "error", "path does not exist"
                            return p, "store", name
                        continue
                else:
                    p.relative_to(bp)
                if must_exist and not p.exists():
                    return p, "error", "path does not exist"
                return p, "store", name
            except Exception:
                continue
        if must_exist and not p.exists():
            return p, "error", "path does not exist"
        return p, "host-absolute", "outside tree and adapter stores"

    # @store/... or @tree/...
    m = LOGICAL_STORE.match(raw.replace("\\", "/"))
    if m:
        name, rest = m.group(1).lower(), (m.group(2) or "").strip("/")
        if name == "tree":
            rel_s = _norm_rel(rest)
            if not rel_s:
                return ROOT.resolve(), "tree", ""
            p = (ROOT / rel_s).resolve()
            try:
                p.relative_to(ROOT.resolve())
            except ValueError:
                return None, "error", "escapes tree root"
            if must_exist and not p.exists():
                return p, "error", "path does not exist"
            return p, "tree", ""
        stores = adapter_stores(harness)
        key = f"@{name}"
        if key not in stores:
            return None, "error", f"unknown store {key} (adapter has: {', '.join(sorted(stores)) or 'none'})"
        base = pathlib.Path(stores[key]).expanduser()
        p = (base / rest).resolve() if rest else base.resolve()
        if must_exist and not p.exists():
            return p, "error", "path does not exist"
        return p, "store", key

    # Bare tree-relative
    rel_s = _norm_rel(raw)
    if not rel_s:
        return None, "error", "empty path"
    p = (ROOT / rel_s).resolve()
    try:
        p.relative_to(ROOT.resolve())
    except ValueError:
        return None, "error", "escapes tree root"
    if must_exist and not p.exists():
        return p, "error", "path does not exist"
    return p, "tree", ""


def find_paths(query, under=None, max_results=40, files_only=True, harness=None):
    """Find files/dirs under tree (or a resolved root) by glob or substring.

    query:
      - if it contains * or ?, treated as a glob (matched on name or relative path)
      - else case-insensitive substring match on the relative path / name
    under: optional logical/tree spec limiting the search root (default ROOT)
    """
    from fnmatch import fnmatch

    if under:
        base, kind, detail = resolve_spec(under, harness=harness)
        if kind == "error" or base is None:
            return [], f"under: {detail}"
        if kind == "host-absolute":
            return [], "under: host absolute outside tree/stores"
    else:
        base = ROOT.resolve()
        kind = "tree"

    if not base.exists():
        return [], f"search root does not exist: {display_path(base)}"

    q = (query or "").strip().replace("\\", "/")
    if not q:
        return [], "empty query"

    is_glob = any(ch in q for ch in "*?[")
    q_lower = q.lower()
    hits = []
    root_res = ROOT.resolve()

    try:
        iterator = base.rglob("*")
    except Exception as e:
        return [], str(e)

    for p in iterator:
        try:
            if files_only and not p.is_file():
                continue
            if not files_only and not (p.is_file() or p.is_dir()):
                continue
        except Exception:
            continue

        try:
            parts = p.relative_to(base).parts
        except Exception:
            parts = p.parts
        if SKIP_DIRS & set(parts):
            continue

        try:
            rel_to_tree = str(p.resolve().relative_to(root_res)).replace("\\", "/")
            rel_s = rel_to_tree
        except Exception:
            rel_s = display_path(p)
            rel_to_tree = None

        name = p.name
        if is_glob:
            if not (fnmatch(name, q) or fnmatch(rel_s, q) or fnmatch(rel_s, "*/" + q)):
                continue
        else:
            if q_lower not in rel_s.lower() and q_lower not in name.lower():
                continue

        hits.append({
            "path": display_path(p),
            "rel": rel_to_tree if rel_to_tree is not None else display_path(p),
            "bytes": p.stat().st_size if p.is_file() else None,
            "dir": p.is_dir(),
        })
        if len(hits) >= max_results:
            break

    hits.sort(key=lambda h: (h["dir"], len(h["rel"]), h["rel"].lower()))
    return hits, ""


def list_dir(spec, harness=None, max_entries=200):
    """List a directory resolved from a logical spec."""
    p, kind, detail = resolve_spec(spec, harness=harness)
    if kind == "error" or p is None:
        return None, kind, detail
    if kind == "host-absolute":
        return None, kind, "host absolute outside tree/stores"
    if not p.exists():
        return None, "error", "path does not exist"
    if p.is_file():
        return [{"name": p.name, "path": display_path(p), "bytes": p.stat().st_size, "dir": False}], kind, detail
    rows = []
    try:
        entries = sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
    except Exception as e:
        return None, "error", str(e)
    for e in entries[:max_entries]:
        if e.name.startswith(".") and e.name not in (".", ".."):
            continue
        rows.append({
            "name": e.name + ("/" if e.is_dir() else ""),
            "path": display_path(e),
            "rel": tree_rel_or_abs(e),
            "bytes": e.stat().st_size if e.is_file() else None,
            "dir": e.is_dir(),
        })
    return rows, kind, detail


def read_text_file(spec, harness=None, max_bytes=200_000, head=None, tail=None):
    """Read a text file via logical path. Returns (text|None, kind, detail)."""
    p, kind, detail = resolve_spec(spec, harness=harness, must_exist=True)
    if kind == "error" or p is None:
        return None, kind, detail
    if kind == "host-absolute":
        return None, kind, "host absolute outside tree/stores — use @store or tree-relative"
    if p.is_dir():
        return None, "error", "is a directory (use path.py ls)"
    try:
        data = p.read_bytes()
    except Exception as e:
        return None, "error", str(e)
    if len(data) > max_bytes:
        return None, "error", f"file too large ({len(data)}B > {max_bytes}B cap); raise with --max-bytes or read a slice"
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = data.decode("utf-8-sig")
        except Exception:
            return None, "error", "not utf-8 text"
    if head is not None and tail is not None:
        return None, "error", "use only one of head/tail"
    lines = text.splitlines(keepends=True)
    if head is not None:
        text = "".join(lines[: max(0, int(head))])
    elif tail is not None:
        text = "".join(lines[-max(0, int(tail)):])
    return text, kind, detail


def display_path(p):
    """Stable string for tool output: forward slashes, absolute."""
    return str(pathlib.Path(p).resolve()).replace("\\", "/")


def tree_rel_or_abs(p):
    """Prefer tree-relative forward-slash form; else absolute forward-slash."""
    p = pathlib.Path(p).resolve()
    try:
        return str(p.relative_to(ROOT.resolve())).replace("\\", "/")
    except ValueError:
        return display_path(p)


def home_dir():
    return pathlib.Path(os.path.expanduser("~")).resolve()


def stray_probe_roots():
    """Directories under the user home that look like mistaken tree mirrors.

    Hermes write_file on some Windows profiles resolves relative paths against
    $HOME instead of the session workdir. Loops write system/... and land in
    ~/system/.... These probes are the known wrong roots — never create them.
    """
    h = home_dir()
    names = (
        "system", "inbox", "momentum", "workspaces", "foundations",
        "life", "relationships", "exports", "NOW.md", "AGENTS.md",
    )
    return [h / n for n in names]


def scan_strays(max_files=200):
    """Return list of {path, rel_home, bytes} for files under stray probe roots."""
    h = home_dir()
    found = []
    for root in stray_probe_roots():
        if not root.exists():
            continue
        if root.is_file():
            try:
                found.append({
                    "path": display_path(root),
                    "rel_home": str(root.relative_to(h)).replace("\\", "/"),
                    "bytes": root.stat().st_size,
                })
            except Exception:
                pass
            continue
        try:
            for p in root.rglob("*"):
                if not p.is_file():
                    continue
                if SKIP_DIRS & set(p.parts):
                    continue
                try:
                    found.append({
                        "path": display_path(p),
                        "rel_home": str(p.relative_to(h)).replace("\\", "/"),
                        "bytes": p.stat().st_size,
                    })
                except Exception:
                    continue
                if len(found) >= max_files:
                    return found
        except Exception:
            continue
    return found


def load_state(name):
    f = STATE / f"{name}.json"
    if f.exists():
        try:
            return json.loads(f.read_text())
        except Exception:
            pass
    return {}


def save_state(name, data):
    STATE.mkdir(parents=True, exist_ok=True)
    (STATE / f"{name}.json").write_text(json.dumps(data, indent=2, sort_keys=True))


def report(title, rows, ok_msg="clean"):
    """Uniform output. Exit code is the caller's job; this only prints."""
    print(f"== {title}")
    if not rows:
        print(f"   {ok_msg}")
        return 0
    for r in rows:
        print(f"   {r}")
    print(f"   {len(rows)} item(s)")
    return len(rows)
