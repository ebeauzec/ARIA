"""
Guard against customer or other sensitive data reaching git or GitHub.

It looks for two kinds of thing in what is about to be committed or pushed:

  1. Generic patterns: access tokens and keys, private keys, e-mail addresses, private IP addresses, Windows user paths, 12-digit serial numbers
     next to the words serial/system, and ARIA's own secret files.
  2. Your own data: every customer, site, system, cluster and contact name, serial number, e-mail address, domain and token that ARIA has
     harvested on this machine. That list is built from the local cache and configuration into `.aria_guard_terms.json` (git-ignored; it never
     leaves this machine) with `python tools/guard_sensitive.py --refresh`. ARIA refreshes it after every sync.

Modes:
  --staged            what is staged for the next commit (the pre-commit hook)
  --push              every commit about to be pushed, files and commit messages (the pre-push hook; reads the hook's stdin)
  --tree [REV]        every tracked file at REV (default HEAD)
  --history           every file and message in every commit reachable from any ref
  --refresh           rebuild the list of your own terms from the local cache
  --file PATH ...     named files (also usable before sending a file by other means)

A finding is shown as file:line, the kind of match and a masked excerpt; the full value is never printed. The exit status is 1 when anything is found.
Standard library only.
"""
import json
import os
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TERMS_PATH = ROOT / ".aria_guard_terms.json"
FICTIONAL_PATH = ROOT / "tools" / "guard_fictional.txt"   # committed: fictional demo values that may appear in the repository
ALLOW_PATH = ROOT / ".aria_guard_allow.txt"      # optional, git-ignored: one term per line that must never count (for example your own company name)

# Values that are fine to appear in public (documentation, fictional demo data, licences)
SAFE_EMAIL_DOMAINS = ("openssh.com", "example.com", "example.org", "example.net", "users.noreply.github.com", "noreply.anthropic.com", "noreply.github.com", "localhost")
SAFE_EMAIL_PREFIXES = ("noreply", "no-reply")
PUBLIC_DOMAINS = {"netapp.com", "gmail.com", "outlook.com", "hotmail.com", "yahoo.com", "microsoft.com", "github.com", "anthropic.com", "apple.com", "google.com", "icloud.com", "live.com"}
GENERIC_TERMS = {"unnamed", "netapp", "default", "unknown", "none", "null", "true", "false", "customer", "system", "cluster", "site", "node", "watchlist", "all", "test",
                 "demo", "admin", "root", "data", "example", "active", "not reported", "n/a", "ontap", "storagegrid", "santricity", "e-series", "aff", "fas", "asa"}

PATTERNS = [
    ("access token", re.compile(r"\b(?:eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,})\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{30,}\b")),
    ("cloud key", re.compile(r"\bAKIA[0-9A-Z]{16}\b|\bAIza[0-9A-Za-z_-]{30,}\b")),
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----")),
    ("secret assignment", re.compile(r"""(?i)\b(?:refresh_?token|access_?token|api_?key|client_?secret|password|passwd|secret|authorization(?:Token)?)\b["']?\s*[:=]\s*["'][A-Za-z0-9+/_\-=.]{24,}["']""")),
    ("bearer value", re.compile(r"(?i)\bBearer\s+[A-Za-z0-9_\-.=]{30,}")),
    ("private address", re.compile(r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b")),
    ("Windows user path", re.compile(r"(?i)\b[A-Z]:\\Users\\(?!Public\b|Default\b|<|%|\{|username\b|name\b|you\b)[A-Za-z0-9._-]+")),
    ("serial number", re.compile(r"(?i)\b(?:serial(?:\s*number)?|system id|sysid)\b[^\n]{0,24}?\b(\d{12})\b")),
]
EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+)\b")
FORBIDDEN_PATHS = re.compile(r"(^|/)(aiq_config\.json|aiq_cache\.db(?:-\w+)?|aria_users\.json|aria_session\.key|\.aria_guard_terms\.json|\.env|CLAUDE\.md)$|^data/(?!README\.md$)|^dist/|^\.claude/|\.(?:db|sqlite3?|pem|key|pfx|p12)$")
BINARY_EXT = (".png", ".jpg", ".jpeg", ".gif", ".ico", ".zip", ".7z", ".exe", ".dll", ".pyd", ".woff", ".woff2", ".ttf", ".pdf", ".docx", ".xlsx", ".pptx")


# ---------------------------------------------------------------------------------------------------------------------------------------
# The list of your own terms
# ---------------------------------------------------------------------------------------------------------------------------------------
_FIELDS = {"customerName", "siteName", "systemName", "hostName", "clusterName", "serialNumber", "nagpName", "csmName", "csmEmail", "samName", "samEmail",
           "salesRepName", "salesRepEmail", "contactName", "contactEmail", "contactPhone", "aspName", "incumbentResellerCompany", "watchlistName",
           "managementIPAddress", "serviceProcessorIPAddress", "emailAddress", "accountLabel", "customer_name", "site_name"}
_OWNERS = {"customer", "site", "nagp", "contactPerson", "csm", "sam", "salesRepresentative", "authorizedSupportPartner", "domesticParent", "system", "reporterContact"}
_OWNED = {"name", "firstName", "lastName", "emailAddress", "phone", "email"}


def _walk_strings(o, out, depth=0, owner=None):
    """Collect the values that identify a customer, site, system or person from a harvested record."""
    if depth > 14:
        return
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, str):
                if k in _FIELDS or (owner in _OWNERS and k in _OWNED):
                    out.append((k, v))
            else:
                _walk_strings(v, out, depth + 1, k)
    elif isinstance(o, list):
        for v in o:
            _walk_strings(v, out, depth + 1, owner)


def _clean_terms(raw):
    allow = set()
    if ALLOW_PATH.exists():
        allow = {l.strip().lower() for l in ALLOW_PATH.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")}
    terms = set()
    for t in raw:
        t = (t or "").strip()
        tl = t.lower()
        if len(t) < 5 or tl in GENERIC_TERMS or tl in PUBLIC_DOMAINS or tl in allow or t.isdigit() and len(t) < 8:
            continue
        if len(t) > 200 or "\n" in t:
            continue
        if any(tl.startswith(p) for p in ("http://", "https://")) and "." not in tl:
            continue
        terms.add(t)
    return sorted(terms, key=lambda x: (-len(x), x))


def refresh(db_path=None, config_path=None, quiet=False):
    """Rebuild .aria_guard_terms.json from the local cache and configuration. Returns the number of terms."""
    base = Path(os.environ.get("ARIA_DATA_DIR") or ROOT)
    db_path = Path(db_path) if db_path else base / "aiq_cache.db"
    cfg_path = Path(config_path) if config_path else db_path.parent / "aiq_config.json"
    raw = []
    if db_path.exists():
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        try:
            queries = [
                "select system_name, cluster_name, customer_name, site_name, serial_number, account_label from reporting_systems",
                "select customer_name, system_name, system_serial from tracked_items",
                "select customer_name, site_name from asup_imports",
                "select customer_name, label, base_url, token from perf_sources",
            ]
            for q in queries:
                try:
                    for row in con.execute(q):
                        raw.extend(str(x) for x in row if x)
                except sqlite3.Error:
                    pass
            try:
                for (js,) in con.execute("select result_json from harvest_cache_accounts"):
                    try:
                        d = json.loads(js)
                    except Exception:
                        continue
                    pairs = []
                    _walk_strings(d, pairs)
                    for k, v in pairs:
                        raw.append(v)
            except sqlite3.Error:
                pass
        finally:
            con.close()
    if cfg_path.exists():
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            pairs = []
            _walk_strings(cfg, pairs)
            for k, v in pairs:
                raw.append(v)
            for key in ("refreshToken", "refresh_token", "accessToken", "nvdApiKey", "githubToken", "webhookUrl"):
                if cfg.get(key):
                    raw.append(str(cfg[key]))
            for a in cfg.get("accounts") or []:
                for key in ("refreshToken", "label", "name"):
                    if isinstance(a, dict) and a.get(key):
                        raw.append(str(a[key]))
        except Exception:
            pass
    # e-mail addresses also contribute their domain and local part
    extra = []
    for t in raw:
        m = EMAIL.search(t)
        if m:
            extra.append(m.group(1))
            extra.append(t.split("@")[0])
    terms = _clean_terms(raw + extra)
    TERMS_PATH.write_text(json.dumps({"terms": terms}, indent=0), encoding="utf-8")
    try:
        os.chmod(TERMS_PATH, 0o600)
    except Exception:
        pass
    if not quiet:
        print(f"guard: {len(terms)} terms from the local cache written to {TERMS_PATH.name} (git-ignored, stays on this machine)")
    return len(terms)


class _Matcher:
    def __init__(self):
        self.terms = []
        if TERMS_PATH.exists():
            try:
                self.terms = json.loads(TERMS_PATH.read_text(encoding="utf-8")).get("terms") or []
            except Exception:
                self.terms = []
        self.lower = {}
        for t in self.terms:
            self.lower.setdefault(t.lower(), t)
        self._auto = None
        try:
            import ahocorasick  # optional speed-up
            a = ahocorasick.Automaton()
            for k in self.lower:
                a.add_word(k, k)
            a.make_automaton()
            self._auto = a
        except Exception:
            self._auto = None
        self._re = None
        if self._auto is None and self.lower:
            # a single alternation, longest first
            self._re = re.compile("|".join(re.escape(k) for k in sorted(self.lower, key=len, reverse=True)))

    def find(self, text_lower):
        if self._auto is not None:
            return {v for _, v in self._auto.iter(text_lower)}
        if self._re is not None:
            return set(self._re.findall(text_lower))
        return set()


def _mask(s):
    s = s.strip()
    if os.environ.get("GUARD_SHOW") == "1":      # local triage only: shows the matched value in your own terminal
        return s
    return (s[:2] + ".." + "*" * min(6, max(0, len(s) - 3)) + s[-1:]) if len(s) > 4 else "****"


def _fictional():
    if FICTIONAL_PATH.exists():
        return {l.strip() for l in FICTIONAL_PATH.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")}
    return set()


_FICTIONAL = None


def scan_text(label, text, matcher):
    global _FICTIONAL
    if _FICTIONAL is None:
        _FICTIONAL = _fictional()
    findings = []
    is_msg = label.startswith("<message")
    lines = text.split("\n")
    low = [l.lower() for l in lines]
    for i, line in enumerate(lines, 1):
        if len(line) > 20000:
            line = line[:20000]
        for kind, rx in PATTERNS:
            m = rx.search(line)
            if m:
                if (kind == "serial number" and m.group(1) in _FICTIONAL) or (kind == "private address" and m.group(0) in _FICTIONAL):
                    continue
                findings.append((label, i, kind, _mask(m.group(0))))
        for m in EMAIL.finditer(line):
            dom = m.group(1).lower()
            local = m.group(0).split("@")[0].lower()
            if dom.endswith(SAFE_EMAIL_DOMAINS) or local.startswith(SAFE_EMAIL_PREFIXES):
                continue
            findings.append((label, i, "e-mail address", _mask(m.group(0))))
        if matcher.terms:
            hit = matcher.find(low[i - 1])
            # a short term only counts as a whole word, so it cannot match inside a longer ordinary word
            hit = {t for t in hit if len(t) >= 8 or re.search(r"(?<![a-z0-9])" + re.escape(t) + r"(?![a-z0-9])", low[i - 1])}
            for t in sorted(hit, key=len, reverse=True)[:3]:
                findings.append((label, i, "your own data (harvested name, serial, contact or token)", _mask(matcher.lower[t])))
    return findings


def scan_path(path):
    if FORBIDDEN_PATHS.search(path):
        return [(path, 0, "file that must stay local", path)]
    return []


# ---------------------------------------------------------------------------------------------------------------------------------------
# git plumbing
# ---------------------------------------------------------------------------------------------------------------------------------------
def git(*args, text=True, check=True):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=text, encoding="utf-8" if text else None, errors="replace" if text else None)
    if check and r.returncode:
        raise SystemExit(f"git {' '.join(args)} failed: {r.stderr}")
    return r.stdout


def blob_text(spec):
    r = subprocess.run(["git", "show", spec], cwd=ROOT, capture_output=True)
    if r.returncode:
        return None
    data = r.stdout
    if b"\x00" in data[:8000]:
        return None
    return data.decode("utf-8", errors="replace")


def report(findings):
    if not findings:
        print("guard: nothing sensitive found")
        return 0
    print(f"guard: {len(findings)} finding(s). Nothing was committed or pushed.", file=sys.stderr)
    seen = 0
    for f, ln, kind, ex in findings:
        print(f"  {f}:{ln}  {kind}  [{ex}]", file=sys.stderr)
        seen += 1
        if seen >= 60:
            print(f"  ... and {len(findings) - seen} more", file=sys.stderr)
            break
    print("Fix or remove the data (use placeholders such as Customer A, host-01, 100000000001) and try again. Never bypass this check.", file=sys.stderr)
    return 1


def scan_blobs(pairs, matcher):
    """pairs: iterable of (label, path, spec)"""
    out = []
    done = set()
    for label, path, spec in pairs:
        out.extend(scan_path(path))
        if path.lower().endswith(BINARY_EXT):
            continue
        key = spec
        if key in done:
            continue
        done.add(key)
        t = blob_text(spec)
        if t is not None:
            out.extend(scan_text(label, t, matcher))
    return out


def staged(matcher):
    names = git("diff", "--cached", "--name-only", "--diff-filter=ACMR").splitlines()
    return scan_blobs([(n, n, f":{n}") for n in names], matcher)


def tree(rev, matcher):
    names = git("ls-tree", "-r", "--name-only", rev).splitlines()
    return scan_blobs([(n, n, f"{rev}:{n}") for n in names], matcher)


def commits_blobs(shas, matcher):
    out = []
    pairs = []
    for sha in shas:
        msg = git("log", "-1", "--format=%an <%ae>%n%cn <%ce>%n%B", sha)
        out.extend(scan_text(f"<message of {sha[:7]}>", msg, matcher))
        for line in git("ls-tree", "-r", sha).splitlines():
            meta, _, path = line.partition("\t")
            _mode, _typ, obj = meta.split()
            pairs.append((f"{path}@{sha[:7]}", path, obj))
    out.extend(scan_blobs(pairs, matcher))
    return out


def push(matcher, stdin):
    findings = []
    for line in stdin.read().splitlines():
        parts = line.split()
        if len(parts) < 4:
            continue
        local_ref, local_sha, remote_ref, remote_sha = parts[:4]
        if set(local_sha) == {"0"}:
            continue                                       # deleting a branch
        if set(remote_sha) == {"0"}:
            shas = git("rev-list", local_sha, "--not", "--remotes").split()
            shas = shas or git("rev-list", local_sha).split()
        else:
            shas = git("rev-list", f"{remote_sha}..{local_sha}", check=False).split() or [local_sha]
        # a force-push replaces history: scan the whole new tip as well
        findings.extend(commits_blobs(shas, matcher))
        findings.extend(tree(local_sha, matcher))
    return findings


def main(argv):
    if "--refresh" in argv:
        refresh()
        return 0
    m = _Matcher()
    if not m.terms:
        print("guard: no list of your own terms yet (run `python tools/guard_sensitive.py --refresh`); only the generic checks are active.", file=sys.stderr)
    if "--staged" in argv:
        return report(staged(m))
    if "--push" in argv:
        return report(push(m, sys.stdin))
    if "--tree" in argv:
        i = argv.index("--tree")
        rev = argv[i + 1] if i + 1 < len(argv) and not argv[i + 1].startswith("--") else "HEAD"
        return report(tree(rev, m))
    if "--history" in argv:
        shas = git("rev-list", "--all").split()
        return report(commits_blobs(shas, m))
    if "--file" in argv:
        i = argv.index("--file")
        out = []
        for p in argv[i + 1:]:
            try:
                out.extend(scan_text(p, Path(p).read_text(encoding="utf-8", errors="replace"), m))
            except Exception as e:
                print(f"guard: cannot read {p}: {e}", file=sys.stderr)
        return report(out)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
