# Running ARIA for a team (Docker and Kubernetes)

By default ARIA is a single-user tool: it listens on `127.0.0.1` and has no sign-in. For a team it can run in a container with sign-in, roles and persistent storage. Nothing about the application changes; only how it is hosted and who may use it.

## What you get

- **Sign-in** with ARIA's own accounts (`ARIA_AUTH=local`), or single sign-on through a reverse proxy you already run (`ARIA_AUTH=header`).
- **A default administrator** so there is always a way in on the first start (`admin` / `Changeme1!`), which has to choose a new password at the first sign-in before anything else works.
- **User administration in Settings** (Settings > Users & Access): add and remove people, set roles, reset passwords, change your own password.
- **Two roles.** `admin` can do everything. `viewer` can read dashboards, the Action Planner, reports and exports from the data already synced.
- **Hardened by default.** Non-root user, read-only root filesystem, no capabilities, host-name check, same-origin check, signed session cookies, login throttling, security headers, an audit line for every state-changing call.
- **One volume** for everything ARIA writes: Active IQ tokens, the cache database, user accounts, reference data.
- **A refusal to start open.** ARIA will not listen on a non-loopback address without sign-in unless you set `ARIA_INSECURE_NO_AUTH=1`.

Important points before you start:

- **One instance only.** The cache is a SQLite file and one sync runs at a time. Run a single replica.
- **Everyone who signs in sees all the data that was synced.** There is no per-customer restriction. If different people may only see different customers, run separate instances with separate Active IQ tokens.
- **Check your Active IQ terms** before giving other people access to data pulled with one person's token.
- **Use HTTPS** in front of ARIA. Passwords and session cookies are sent on every request.
- **The volume holds Active IQ refresh tokens.** Use encrypted storage and restrict who can read it.

## Settings

| Variable | Default | Meaning |
|---|---|---|
| `ARIA_BIND` | `127.0.0.1` (`0.0.0.0` in the image) | Address to listen on |
| `ARIA_PORT` | `8080` | Port |
| `ARIA_DATA_DIR` | program folder (`/var/lib/aria` in the image) | Where tokens, cache and accounts live |
| `ARIA_AUTH` | `none` (`local` in the image) | `none`, `local` or `header` |
| `ARIA_ALLOWED_HOSTS` | *(only localhost)* | Comma-separated host names people use to reach ARIA. `*` accepts any (use only with sign-in on) |
| `ARIA_ADMIN_USER`, `ARIA_ADMIN_PASSWORD` | | Creates the first administrator, with a password you choose, when there are no users yet (instead of the default one). Remove the password afterwards |
| `ARIA_ADMIN_MUST_CHANGE` | off | `1` makes that administrator choose a new password at the first sign-in too |
| `ARIA_DEFAULT_ADMIN_USER`, `ARIA_DEFAULT_ADMIN_PASSWORD` | `admin`, `Changeme1!` | The starting administrator used when `ARIA_ADMIN_*` is not set. Always has to be changed at the first sign-in |
| `ARIA_SESSION_HOURS` | `12` | Sign-in lifetime |
| `ARIA_SESSION_SECRET` | generated, stored on the volume | Key that signs session cookies |
| `ARIA_COOKIE_SECURE` | off | Set to `1` when ARIA is served over HTTPS (it is also set automatically when `X-Forwarded-Proto: https` arrives) |
| `ARIA_CA_BUNDLE` | | Path to extra trusted CA certificates (for example a TLS inspection CA) |
| `ARIA_HEADER_USER`, `ARIA_HEADER_GROUPS` | `X-Forwarded-User`, `X-Forwarded-Groups` | Header mode: where the proxy puts the user name and groups |
| `ARIA_ADMIN_USERS`, `ARIA_ADMIN_GROUPS` | | Header mode: who is an administrator (user names / group names). Everyone else is a viewer |
| `ARIA_VIEWER_GROUPS` | | Header mode: if set, only people in these groups (or an admin group) may sign in |
| `ARIA_TRUSTED_PROXIES` | | Header mode: only accept the user header from these addresses (CIDR, comma-separated) |

## First sign-in and the default administrator

When ARIA starts with sign-in on (`ARIA_AUTH=local`) and there are no users yet, it creates one administrator:

| User name | Password |
|---|---|
| `admin` | `Changeme1!` |

The first sign-in goes to a "Choose a new password" page. Until the password has been changed, that account can do nothing else: every other page and API call is refused. The new password needs at least 10 characters and must differ from the default one. The startup log says when the default administrator was created (it does not print the password).

Because the default is public, **do not leave a new instance reachable by other people before you have signed in and changed it.** For anything that is reachable from a network, set your own starting password instead with `ARIA_ADMIN_USER` and `ARIA_ADMIN_PASSWORD` (or a different default with `ARIA_DEFAULT_ADMIN_USER` and `ARIA_DEFAULT_ADMIN_PASSWORD`). Unknown user names and wrong passwords are throttled, but a known default is still the weakest point of a fresh install.

## Switching sign-in on or off

- **Settings > Access** has a switch ("Turn on sign-in" / "Turn off sign-in"). The choice is stored and applies the next time ARIA starts. It is hidden from changing when `ARIA_AUTH` is set in the environment (that setting always wins) or when single sign-on is used.
- **The desktop program (ARIA.exe)**: start it once with `ARIA.exe --sign-in` to turn sign-in on (or `--no-sign-in` to turn it off); or use the switch in Settings > Access and restart. Its settings, tokens, cache and user accounts are kept next to `ARIA.exe` (or in `%LOCALAPPDATA%\ARIA` when that folder cannot be written to; set `ARIA_DATA_DIR` to use another folder). On the first start with sign-in on, sign in as `admin` with the default password and choose a new one.
- **Python**: `python server.py --sign-in`, or `ARIA_AUTH=local`.

## Managing users (Settings)

Administrators open **Settings > Access** (the Users & Access card):

- **Add a user** with a user name, a temporary password and a role. The person must choose their own password at the first sign-in.
- **Change a role** (viewer / administrator) from the list. The last administrator cannot be demoted or removed.
- **Reset a password** by giving a new temporary password. Every session of that user ends immediately and they choose a new password at the next sign-in.
- **Remove** a user.

Everyone, including viewers, can **change their own password** on the same card. In header mode the card only shows who is signed in; roles come from the proxy's headers (see below).

The same actions are available from the command line (`python server.py --add-user NAME --role viewer`, `--set-password`, `--remove-user`, `--list-users`; a password set this way is temporary too) and the API (`GET/POST/DELETE /api/auth/users`, `POST /api/auth/password`).

## Docker (one host)

```bash
# 1. optional: choose the first administrator's password yourself (otherwise it is admin / Changeme1!, to be changed at first sign-in)
printf 'ARIA_ADMIN_USER=admin\nARIA_ADMIN_PASSWORD=choose-a-long-password\nARIA_ALLOWED_HOSTS=aria.example.com\n' > .env
# 2. build and start
docker compose up -d --build
# 3. open http://localhost:8080 (put an HTTPS reverse proxy in front for real use), sign in, add the Active IQ refresh token in Settings
# 4. if you set ARIA_ADMIN_PASSWORD, remove it from .env and restart; the account is already created
```

Add people in Settings > Users & Access, or with the command line inside the container:

```bash
docker compose exec aria python server.py --add-user alice --role viewer     # prompts for a password
docker compose exec aria python server.py --list-users
docker compose exec aria python server.py --set-password alice
docker compose exec aria python server.py --remove-user alice
```

The same actions are in the API: `GET/POST/DELETE /api/auth/users` (administrators) and `POST /api/auth/password` (`{"old": "...", "new": "..."}`, anyone signed in). Changing or resetting a password signs that user out everywhere.

## Kubernetes

The manifests are in [`deploy/k8s`](../deploy/k8s): namespace, persistent volume claim, deployment (one replica, non-root, read-only root filesystem, probes on `/healthz`), service, ingress with TLS, and a network policy.

```bash
docker build -t registry.example.com/aria:5.6.266 .
docker push registry.example.com/aria:5.6.266
# edit deploy/k8s/deployment.yaml (image, ARIA_ALLOWED_HOSTS), ingress.yaml (host, TLS secret) and networkpolicy.yaml (ingress namespace)
cp deploy/k8s/secret.example.yaml deploy/k8s/secret.yaml        # optional: your own first-administrator password; do not commit it
kubectl apply -f deploy/k8s/secret.yaml
kubectl apply -k deploy/k8s
kubectl -n aria exec deploy/aria -- python server.py --add-user alice --role viewer
```

Keep the strategy at `Recreate` and `replicas: 1`. Use an encrypted storage class for the claim. A long sync and large exports take minutes, so raise the ingress timeouts (the example does).

## Single sign-on through a proxy (header mode)

Run an authenticating proxy in front of ARIA (for example oauth2-proxy with your OIDC provider, or an ingress with external auth) that sets `X-Forwarded-User` and, if you want group-based roles, `X-Forwarded-Groups`. Then:

```yaml
- {name: ARIA_AUTH, value: header}
- {name: ARIA_ADMIN_GROUPS, value: aria-admins}       # or ARIA_ADMIN_USERS: alice,bob
- {name: ARIA_VIEWER_GROUPS, value: aria-viewers,aria-admins}
- {name: ARIA_TRUSTED_PROXIES, value: 10.0.0.0/8}     # the proxy's address range
```

ARIA trusts that header completely, so ARIA must not be reachable except through the proxy. The network policy in `deploy/k8s` is what enforces that; keep it. ARIA has no login page or user store in this mode.

## What each role can do

| | admin | viewer |
|---|---|---|
| Dashboards, Action Planner, reports, Word/Markdown exports | yes | yes |
| Read synced data, tracker, history, reference data | yes | yes |
| Start a sync, change settings, add Active IQ tokens | yes | no |
| Write back to Active IQ (acknowledge risks, Success Plans, CQV) | yes | no |
| Update the remediation tracker, import AutoSupport files | yes | no |
| Use the Active IQ proxy and probes | yes | no |
| Manage users (Settings > Users & Access) | yes | no |
| Change their own password | yes | yes |

A viewer who clicks an administrator-only action gets a "Your role does not allow this" message.

## Corporate TLS inspection

On Windows ARIA reads the machine's certificate store. A Linux container does not have it, so mount your CA certificate (PEM) and set `ARIA_CA_BUNDLE` to its path (the compose file and the deployment have commented examples).

## Backup and upgrade

- **Back up** the volume (`/var/lib/aria`): `aiq_config.json` (tokens), `aiq_cache.db`, `aria_users.json`, `aria_session.key` and `data/`.
- **Upgrade** by building the new image and restarting. The volume is reused; the cache refreshes on the next sync.
- **Lost the only administrator password?** Run `python server.py --set-password NAME` in the container (it needs shell access to the volume, which is the point).

## Known limits

- Sessions are signed cookies, not server-side records. Signing out clears the cookie in that browser; a copied cookie stays valid until it expires or the user's password changes. Keep `ARIA_SESSION_HOURS` short on shared machines.
- Login throttling is per source address and user name, held in memory (a restart clears it).
- No two-factor sign-in in `local` mode. For that, use `header` mode with your identity provider.
- The image was built and run with the read-only, non-root, capability-free settings used in the compose file and the deployment, and sign-in, persistence across a restart and the host check were checked against it. The Kubernetes manifests were not applied to a cluster. The role rules are covered by `tests/auth_smoke.sh`.
