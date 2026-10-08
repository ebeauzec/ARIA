"""
ARIA sign-in and access control for team (container / Kubernetes) deployments.

Modes, chosen with the ARIA_AUTH environment variable:

  none    No sign-in. Only for a single user on this machine (the server then only binds to a loopback address).
  local   ARIA's own accounts: a login page, passwords stored as scrypt hashes in aria_users.json, signed session cookies.
  header  A reverse proxy in front of ARIA (oauth2-proxy, an ingress with OIDC/SAML, Azure App Proxy ...) signs people in and passes the
          user name in a header (default X-Forwarded-User). ARIA then only decides the role. Only use it when ARIA cannot be reached except
          through that proxy (a NetworkPolicy, or ARIA_TRUSTED_PROXIES).

Roles:
  admin   everything: settings and Active IQ tokens, syncs, write-back to Active IQ, user management.
  viewer  read-only: dashboards, Action Planner, reports and exports from the data already synced.

Standard library only.
"""
import base64
import hashlib
import hmac
import ipaddress
import json
import os
import re
import secrets
import threading
import time
import urllib.parse
from pathlib import Path

ROLES = ("admin", "viewer")
# The administrator that exists on the very first start when no other one is configured. It can do nothing except change its own password until
# that has been done. Set ARIA_DEFAULT_ADMIN_USER / ARIA_DEFAULT_ADMIN_PASSWORD to use a different starting pair (for example your site standard),
# or ARIA_ADMIN_USER / ARIA_ADMIN_PASSWORD to create the administrator with a password of your choice.
DEFAULT_ADMIN_USER = "admin"
DEFAULT_ADMIN_PASSWORD = "Changeme1!"
MIN_PASSWORD = 10
COOKIE_NAME = "aria_session"

# What a viewer may call. Everything else needs the admin role.
_VIEWER_GET_PREFIXES = (
    "/api/harvest", "/api/sync-status", "/api/config", "/api/watchlists", "/api/resolve-watchlist", "/api/eoa-database", "/api/imt-interop",
    "/api/reference-library/status", "/api/knowledge-base", "/api/enrich", "/api/auto-harvest/status", "/api/bulletins", "/api/history/",
    "/api/asup/imports", "/api/asup/customers", "/api/tracker", "/api/plan-progress", "/api/perf/latest", "/api/perf/snapshots",
    "/api/auth/me", "/api/library/status", "/api/library/search", "/api/library/doc",   # read-only: freshness, search and viewing of the reference library
)
_VIEWER_GET_BLOCKED = ("/api/bulletins/scan", "/api/enrich/scan")
_VIEWER_POSTS = ("/api/history/trend",)


SETTINGS_NAME = "aria_settings.json"


def load_settings(data_root):
    try:
        return json.loads((Path(data_root) / SETTINGS_NAME).read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_auth_setting(data_root, mode):
    """Store whether sign-in is on for the next start (the choice made with the Settings switch or the --sign-in flag)."""
    if mode not in ("none", "local"):
        raise ValueError("mode must be none or local")
    root = Path(data_root)
    root.mkdir(parents=True, exist_ok=True)
    s = load_settings(root)
    s["auth"] = mode
    tmp = root / (SETTINGS_NAME + ".tmp")
    tmp.write_text(json.dumps(s, indent=2), encoding="utf-8")
    os.replace(tmp, root / SETTINGS_NAME)


def apply_cli_flags(data_root, argv):
    """--sign-in turns sign-in on and --no-sign-in turns it off, for this start and the following ones. ARIA_AUTH in the environment still wins."""
    if "--sign-in" in argv:
        save_auth_setting(data_root, "local")
        print("  [AUTH] Sign-in is switched on (stored in " + SETTINGS_NAME + ").", flush=True)
    elif "--no-sign-in" in argv:
        save_auth_setting(data_root, "none")
        print("  [AUTH] Sign-in is switched off (stored in " + SETTINGS_NAME + ").", flush=True)


def _b64(b):
    return base64.urlsafe_b64encode(b).decode("ascii").rstrip("=")


def _unb64(s):
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def hash_password(password, n=2 ** 14, r=8, p=1):
    salt = secrets.token_bytes(16)
    h = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=n, r=r, p=p, dklen=32)
    return f"scrypt${n}${r}${p}${_b64(salt)}${_b64(h)}"


def verify_password(password, stored):
    try:
        scheme, n, r, p, salt, h = stored.split("$")
        if scheme != "scrypt":
            return False
        calc = hashlib.scrypt(password.encode("utf-8"), salt=_unb64(salt), n=int(n), r=int(r), p=int(p), dklen=32)
        return hmac.compare_digest(calc, _unb64(h))
    except Exception:
        return False


class Auth:
    def __init__(self, data_root, env=None):
        env = os.environ if env is None else env
        self.data_root = Path(data_root)
        self.settings_path = self.data_root / SETTINGS_NAME
        saved = load_settings(self.data_root).get("auth")
        if env.get("ARIA_AUTH"):
            self.mode, self.mode_source = env["ARIA_AUTH"].strip().lower(), "environment"
        elif saved:
            self.mode, self.mode_source = str(saved).strip().lower(), "settings"
        else:
            self.mode, self.mode_source = "none", "default"
        self.saved_mode = (saved or "none")      # what is stored for the next start
        if self.mode not in ("none", "local", "header"):
            raise SystemExit(f"ARIA_AUTH must be none, local or header (got {self.mode!r})")
        self.users_path = self.data_root / "aria_users.json"
        self.session_hours = float(env.get("ARIA_SESSION_HOURS") or 12)
        self.cookie_secure = (env.get("ARIA_COOKIE_SECURE") or "").lower() in ("1", "true", "yes")
        self.default_admin = (env.get("ARIA_DEFAULT_ADMIN_USER") or DEFAULT_ADMIN_USER, env.get("ARIA_DEFAULT_ADMIN_PASSWORD") or DEFAULT_ADMIN_PASSWORD)
        self.header_user = env.get("ARIA_HEADER_USER") or "X-Forwarded-User"
        self.header_groups = env.get("ARIA_HEADER_GROUPS") or "X-Forwarded-Groups"
        self.admin_users = {u.strip().lower() for u in (env.get("ARIA_ADMIN_USERS") or "").split(",") if u.strip()}
        self.admin_groups = {g.strip().lower() for g in (env.get("ARIA_ADMIN_GROUPS") or "").split(",") if g.strip()}
        self.viewer_groups = {g.strip().lower() for g in (env.get("ARIA_VIEWER_GROUPS") or "").split(",") if g.strip()}
        self.trusted_proxies = []
        for c in (env.get("ARIA_TRUSTED_PROXIES") or "").split(","):
            if c.strip():
                self.trusted_proxies.append(ipaddress.ip_network(c.strip(), strict=False))
        self._lock = threading.Lock()
        self._fails = {}          # (ip, user) -> (count, locked_until)
        self._secret = None
        if self.mode == "local":
            self.data_root.mkdir(parents=True, exist_ok=True)
            self._secret = self._load_secret(env)
            self._bootstrap_admin(env)

    # ---- secrets and users --------------------------------------------------------------------------------------------------
    def _load_secret(self, env):
        if env.get("ARIA_SESSION_SECRET"):
            return env["ARIA_SESSION_SECRET"].encode("utf-8")
        p = self.data_root / "aria_session.key"
        if p.exists():
            return p.read_bytes()
        key = secrets.token_bytes(32)
        p.write_bytes(key)
        try:
            os.chmod(p, 0o600)
        except Exception:
            pass
        return key

    def _read_users(self):
        try:
            return json.loads(self.users_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _write_users(self, users):
        tmp = self.users_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(users, indent=2), encoding="utf-8")
        try:
            os.chmod(tmp, 0o600)
        except Exception:
            pass
        os.replace(tmp, self.users_path)

    def _bootstrap_admin(self, env):
        if self._read_users():
            return
        u, pw = env.get("ARIA_ADMIN_USER"), env.get("ARIA_ADMIN_PASSWORD")
        if u and pw:
            force = (env.get("ARIA_ADMIN_MUST_CHANGE") or "").lower() in ("1", "true", "yes")
            self.set_user(u, pw, "admin", must_change=force)
            print(f"  [AUTH] Created the first administrator '{u}' from ARIA_ADMIN_USER / ARIA_ADMIN_PASSWORD. Remove the password variable now.", flush=True)
        else:
            du, dp = self.default_admin
            self.set_user(du, dp, "admin", must_change=True)
            print(f"  [AUTH] No users existed: created the default administrator '{du}' with the default password (see docs/DEPLOY.md). "
                  f"It must be changed at the first sign-in, and nothing else works until it is. Sign in now.", flush=True)

    def get_user(self, name):
        return self._read_users().get((name or "").strip().lower())

    def set_user(self, name, password=None, role=None, must_change=None):
        """Create a user (a password is required) or update one: a new password (which signs the user out everywhere), a new role, or both."""
        name = (name or "").strip()
        if not re.fullmatch(r"[A-Za-z0-9._@-]{1,64}", name):
            raise ValueError("User names may contain letters, digits and . _ @ - (up to 64)")
        if role is not None and role not in ROLES:
            raise ValueError("Role must be admin or viewer")
        if password is not None and len(password) < MIN_PASSWORD:
            raise ValueError(f"Passwords must be at least {MIN_PASSWORD} characters")
        with self._lock:
            users = self._read_users()
            old = users.get(name.lower())
            if old is None and not password:
                raise ValueError("A new user needs a password")
            rec = dict(old or {"name": name, "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "epoch": 0, "role": "viewer", "must_change": False})
            if role is not None:
                rec["role"] = role
            if password:
                rec["hash"] = hash_password(password)
                rec["epoch"] = int(rec.get("epoch", 0)) + 1
                rec["must_change"] = True if must_change is None else bool(must_change)
            elif must_change is not None:
                rec["must_change"] = bool(must_change)
            users[name.lower()] = rec
            if not any(u.get("role") == "admin" for u in users.values()):
                raise ValueError("There must be at least one administrator")
            self._write_users(users)

    def change_password(self, name, old, new):
        """A signed-in user changes their own password. Returns the updated record; raises ValueError with the reason."""
        u = self.get_user(name)
        if not u or not verify_password(old or "", u["hash"]):
            raise PermissionError("The current password is wrong")
        if len(new or "") < MIN_PASSWORD:
            raise ValueError(f"The new password must be at least {MIN_PASSWORD} characters")
        if new == old:
            raise ValueError("The new password must be different from the current one")
        if new in (self.default_admin[1], DEFAULT_ADMIN_PASSWORD):
            raise ValueError("Choose a password other than the default one")
        self.set_user(name, new, None, must_change=False)
        return self.get_user(name)

    def remove_user(self, name):
        with self._lock:
            users = self._read_users()
            if users.pop(name.strip().lower(), None) is None:
                return False
            if not any(u.get("role") == "admin" for u in users.values()):
                raise ValueError("Cannot remove the last administrator")
            self._write_users(users)
            return True

    def list_users(self):
        return [{"name": u["name"], "role": u["role"], "created": u.get("created"), "must_change": bool(u.get("must_change"))} for u in self._read_users().values()]

    # ---- sessions -----------------------------------------------------------------------------------------------------------
    def _sign(self, payload):
        return _b64(hmac.new(self._secret, payload.encode("utf-8"), hashlib.sha256).digest())

    def make_cookie_value(self, user):
        exp = int(time.time() + self.session_hours * 3600)
        payload = _b64(json.dumps({"u": user["name"], "r": user["role"], "e": user.get("epoch", 0), "x": exp}).encode("utf-8"))
        return payload + "." + self._sign(payload)

    def _session_user(self, cookie_header):
        if not cookie_header:
            return None
        for part in cookie_header.split(";"):
            k, _, v = part.strip().partition("=")
            if k == COOKIE_NAME and "." in v:
                payload, sig = v.rsplit(".", 1)
                if not hmac.compare_digest(sig, self._sign(payload)):
                    return None
                try:
                    d = json.loads(_unb64(payload))
                except Exception:
                    return None
                if d.get("x", 0) < time.time():
                    return None
                u = self._read_users().get(str(d.get("u", "")).lower())
                # the account must still exist, with the same password epoch; the role is the current one
                if not u or u.get("epoch", 0) != d.get("e"):
                    return None
                return {"name": u["name"], "role": u["role"], "must_change": bool(u.get("must_change"))}
        return None

    def cookie_header(self, value, secure):
        flags = f"{COOKIE_NAME}={value}; Path=/; HttpOnly; SameSite=Strict; Max-Age={int(self.session_hours * 3600)}"
        return flags + ("; Secure" if (secure or self.cookie_secure) else "")

    def clear_cookie_header(self):
        return f"{COOKIE_NAME}=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0"

    # ---- sign-in ------------------------------------------------------------------------------------------------------------
    def login(self, ip, username, password):
        """Returns (user dict, None) or (None, message). Repeated failures lock the (ip, name) pair for a while."""
        key = (ip, (username or "").lower())
        now = time.time()
        with self._lock:
            n, until = self._fails.get(key, (0, 0))
            if until > now:
                return None, f"Too many failed attempts. Try again in {int(until - now) + 1} seconds."
        users = self._read_users()
        u = users.get((username or "").lower())
        ok = bool(u) and verify_password(password or "", u["hash"])
        if not u:
            verify_password(password or "", hash_password("x" * 12, n=2 ** 10))   # similar cost for unknown names
        with self._lock:
            if ok:
                self._fails.pop(key, None)
                return u, None
            n += 1
            self._fails[key] = (n, now + min(900, 2 ** max(0, n - 3) * 5) if n >= 3 else 0)
        return None, "Wrong user name or password."

    # ---- identify the caller ------------------------------------------------------------------------------------------------
    def _from_trusted_proxy(self, ip):
        if not self.trusted_proxies:
            return True
        try:
            a = ipaddress.ip_address(ip)
        except ValueError:
            return False
        return any(a in n for n in self.trusted_proxies)

    def identify(self, headers, ip):
        if self.mode == "local":
            return self._session_user(headers.get("Cookie"))
        if self.mode == "header":
            if not self._from_trusted_proxy(ip):
                return None
            name = (headers.get(self.header_user) or "").strip()
            if not name:
                return None
            groups = {g.strip().lower() for g in re.split(r"[,;]", headers.get(self.header_groups) or "") if g.strip()}
            if name.lower() in self.admin_users or (groups & self.admin_groups):
                return {"name": name, "role": "admin"}
            if self.viewer_groups and not (groups & self.viewer_groups):
                return None       # a viewer group is required and the person is in none of them
            return {"name": name, "role": "viewer"}
        return {"name": "local", "role": "admin"}

    # ---- what a role may do -------------------------------------------------------------------------------------------------
    @staticmethod
    def allowed(role, method, path, query):
        if role == "admin":
            return True
        if role != "viewer":
            return False
        if method in ("GET", "HEAD"):
            if not path.startswith("/api/") and path not in ("/graphql",):
                return True                                    # the page and its static files
            if path.startswith(_VIEWER_GET_BLOCKED):
                return False
            if path.startswith("/api/harvest") and re.search(r"(^|&)force=", query or ""):
                return False                                   # a viewer cannot start a sync
            return path.startswith(_VIEWER_GET_PREFIXES)
        if method == "POST":
            return path in _VIEWER_POSTS
        return False


LOGIN_PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sign in - ARIA</title>
<style>
:root{--bg:#0f1626;--card:#16203a;--text:#e6ebf5;--muted:#8a96b0;--accent:#38bdf8;--err:#f87171}
@media (prefers-color-scheme: light){:root{--bg:#f3f5fa;--card:#fff;--text:#1a2238;--muted:#5d6a86;--accent:#0369a1;--err:#b91c1c}}
body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:var(--bg);color:var(--text);font:15px system-ui,Segoe UI,sans-serif}
form{background:var(--card);padding:32px;border-radius:10px;width:min(360px,calc(100vw - 32px));box-shadow:0 8px 30px rgba(0,0,0,.25)}
h1{margin:0 0 4px;font-size:1.4rem}p{margin:0 0 20px;color:var(--muted);font-size:.85rem}
label{display:block;font-size:.8rem;margin:12px 0 4px;color:var(--muted)}
input{width:100%;box-sizing:border-box;padding:9px 10px;border-radius:6px;border:1px solid #3a4766;background:transparent;color:var(--text);font-size:1rem}
button{margin-top:20px;width:100%;padding:10px;border:0;border-radius:6px;background:var(--accent);color:#04121f;font-weight:600;font-size:1rem;cursor:pointer}
.err{color:var(--err);font-size:.85rem;margin-top:12px;min-height:1.2em}
</style></head><body>
<form method="post" action="/login" id="f"><h1>ARIA</h1><p>Active IQ Risk Intelligence Advisor</p>
<input type="hidden" name="next" value="__NEXT__">
<label for="u">User name</label><input id="u" name="username" autocomplete="username" autofocus required>
<label for="p">Password</label><input id="p" name="password" type="password" autocomplete="current-password" required>
<button type="submit">Sign in</button><div class="err" role="alert">__ERROR__</div></form></body></html>"""


CHANGE_PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Choose a new password - ARIA</title>
<style>
:root{--bg:#0f1626;--card:#16203a;--text:#e6ebf5;--muted:#8a96b0;--accent:#38bdf8;--err:#f87171}
@media (prefers-color-scheme: light){:root{--bg:#f3f5fa;--card:#fff;--text:#1a2238;--muted:#5d6a86;--accent:#0369a1;--err:#b91c1c}}
body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:var(--bg);color:var(--text);font:15px system-ui,Segoe UI,sans-serif}
form{background:var(--card);padding:32px;border-radius:10px;width:min(380px,calc(100vw - 32px));box-shadow:0 8px 30px rgba(0,0,0,.25)}
h1{margin:0 0 4px;font-size:1.3rem}p{margin:0 0 16px;color:var(--muted);font-size:.85rem}
label{display:block;font-size:.8rem;margin:12px 0 4px;color:var(--muted)}
input{width:100%;box-sizing:border-box;padding:9px 10px;border-radius:6px;border:1px solid #3a4766;background:transparent;color:var(--text);font-size:1rem}
button{margin-top:20px;width:100%;padding:10px;border:0;border-radius:6px;background:var(--accent);color:#04121f;font-weight:600;font-size:1rem;cursor:pointer}
.err{color:var(--err);font-size:.85rem;margin-top:12px;min-height:1.2em}
</style></head><body>
<form id="f"><h1>Choose a new password</h1><p>__WHO__ must set a new password before using ARIA. At least 10 characters, different from the current one.</p>
<label for="o">Current password</label><input id="o" type="password" autocomplete="current-password" required>
<label for="n">New password</label><input id="n" type="password" autocomplete="new-password" minlength="10" required>
<label for="c">New password again</label><input id="c" type="password" autocomplete="new-password" minlength="10" required>
<button type="submit">Change password</button><div class="err" id="e" role="alert"></div></form>
<script>
document.getElementById('f').addEventListener('submit', async ev => {
  ev.preventDefault();
  const e = document.getElementById('e'); e.textContent = '';
  const o = document.getElementById('o').value, n = document.getElementById('n').value, c = document.getElementById('c').value;
  if (n !== c) { e.textContent = 'The two new passwords are different.'; return; }
  try {
    const r = await fetch('/api/auth/password', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ old: o, new: n }) });
    const d = await r.json().catch(() => ({}));
    if (r.ok) { location.href = '/'; } else { e.textContent = d.error || 'Could not change the password.'; }
  } catch (x) { e.textContent = 'Could not reach the server.'; }
});
</script></body></html>"""


def change_page(who="This account"):
    esc = lambda x: (x or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return CHANGE_PAGE.replace("__WHO__", esc(who)).encode("utf-8")


def login_page(next_url="/", error=""):
    esc = lambda s: (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    return LOGIN_PAGE.replace("__NEXT__", esc(next_url)).replace("__ERROR__", esc(error)).encode("utf-8")


def safe_next(url):
    """Only same-site relative paths are followed after sign-in."""
    url = urllib.parse.unquote(url or "/")
    if not url.startswith("/") or url.startswith("//") or "\\" in url or "\r" in url or "\n" in url:
        return "/"
    return url
