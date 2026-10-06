#!/bin/sh
# Smoke test for ARIA_AUTH=local: sign-in, roles, CSRF and host checks. Starts its own server on port 8099 with a temporary data folder.
# Usage: sh tests/auth_smoke.sh   (from the project folder; needs python and curl)
set -u
export MSYS_NO_PATHCONV=1   # keep Git Bash on Windows from rewriting arguments that look like paths
TD="${TMPDIR:-/tmp}/aria_authtest.$$"; mkdir -p "$TD"
ARIA_AUTH=local ARIA_PORT=8099 ARIA_DATA_DIR="$TD" ARIA_ADMIN_USER=admin ARIA_ADMIN_PASSWORD='Correct-Horse-1' python server.py >"$TD/log.txt" 2>&1 &
PID=$!
trap 'kill $PID 2>/dev/null; rm -rf "$TD"' EXIT
B=localhost:8099
for i in 1 2 3 4 5 6 7 8 9 10; do curl -s -o /dev/null $B/healthz && break; sleep 1; done
fail=0
check() { # name expected actual
  if [ "$2" = "$3" ]; then echo "ok    $1"; else echo "FAIL  $1 (expected $2, got $3)"; fail=1; fi
}
code() { curl -s -o /dev/null -w "%{http_code}" "$@"; }
check "health probe needs no sign-in" 200 "$(code $B/healthz)"
check "page redirects to sign-in" 303 "$(code -H 'Accept: text/html' $B/)"
check "API without sign-in" 401 "$(code $B/api/harvest)"
check "wrong password" 401 "$(code -d 'username=admin&password=wrong' $B/login)"
check "admin sign-in" 303 "$(code -c "$TD/jar" -d 'username=admin&password=Correct-Horse-1' $B/login)"
check "admin: /api/auth/me" 200 "$(code -b "$TD/jar" $B/api/auth/me)"
check "admin: user list" 200 "$(code -b "$TD/jar" $B/api/auth/users)"
check "admin creates viewer" 200 "$(code -b "$TD/jar" -H 'Content-Type: application/json' -d '{"name":"viewer1","password":"Viewer-Pass-123","role":"viewer","must_change":false}' $B/api/auth/users)"
check "viewer sign-in" 303 "$(code -c "$TD/jarv" -d 'username=viewer1&password=Viewer-Pass-123' $B/login)"
check "viewer: read data" 200 "$(code -b "$TD/jarv" $B/api/config)"
check "viewer: page file" 200 "$(code -b "$TD/jarv" $B/app.js)"
check "viewer: cannot start a sync" 403 "$(code -b "$TD/jarv" "$B/api/harvest?force=1")"
check "viewer: cannot change settings" 403 "$(code -b "$TD/jarv" -X POST -H 'Content-Type: application/json' -d '{}' $B/api/config)"
check "viewer: cannot use the Active IQ proxy" 403 "$(code -b "$TD/jarv" -X POST -H 'Content-Type: application/json' -d '{}' $B/graphql)"
check "viewer: cannot manage users" 403 "$(code -b "$TD/jarv" $B/api/auth/users)"
check "viewer: report data POST" 200 "$(code -b "$TD/jarv" -X POST -H 'Content-Type: application/json' -d '{}' $B/api/history/trend)"
check "cross-origin POST refused" 403 "$(code -b "$TD/jar" -X POST -H 'Origin: http://evil.example' -d '{}' $B/api/config)"
check "foreign Host refused" 403 "$(code -b "$TD/jar" -H 'Host: evil.example' $B/api/auth/me)"
check "forged cookie refused" 401 "$(code -b 'aria_session=eyJ1IjoiYWRtaW4ifQ.AAAA' $B/api/auth/me)"
check "open redirect after sign-in is ignored" "/" "$(curl -s -o /dev/null -w '%{redirect_url}' -d 'username=admin&password=Correct-Horse-1&next=//evil.example' $B/login | sed 's#http://localhost:8099##')"

# ---- default administrator: must change the password before anything else works ----
TD2="${TMPDIR:-/tmp}/aria_authtest2.$$"; mkdir -p "$TD2"
ARIA_AUTH=local ARIA_PORT=8098 ARIA_DATA_DIR="$TD2" python server.py >"$TD2/log.txt" 2>&1 &
PID2=$!
trap 'kill $PID $PID2 2>/dev/null; rm -rf "$TD" "$TD2"' EXIT
B2=localhost:8098
for i in 1 2 3 4 5 6 7 8 9 10; do curl -s -o /dev/null $B2/healthz && break; sleep 1; done
check "default admin signs in and is sent to change the password" "http://$B2/change-password" "$(curl -s -o /dev/null -c "$TD2/jar" -w '%{redirect_url}' -d 'username=admin&password=Changeme1!' $B2/login)"
check "nothing else works before the change (API)" 403 "$(code -b "$TD2/jar" $B2/api/config)"
check "nothing else works before the change (page)" 303 "$(code -b "$TD2/jar" -H 'Accept: text/html' $B2/)"
check "the change page is reachable" 200 "$(code -b "$TD2/jar" $B2/change-password)"
check "wrong current password" 403 "$(code -b "$TD2/jar" -H 'Content-Type: application/json' -d '{"old":"nope","new":"A-Brand-New-Pass-9"}' $B2/api/auth/password)"
check "the default password is refused as the new one" 400 "$(code -b "$TD2/jar" -H 'Content-Type: application/json' -d '{"old":"Changeme1!","new":"Changeme1!"}' $B2/api/auth/password)"
check "too short" 400 "$(code -b "$TD2/jar" -H 'Content-Type: application/json' -d '{"old":"Changeme1!","new":"short"}' $B2/api/auth/password)"
check "password changed" 200 "$(code -b "$TD2/jar" -c "$TD2/jar2" -H 'Content-Type: application/json' -d '{"old":"Changeme1!","new":"A-Brand-New-Pass-9"}' $B2/api/auth/password)"
check "works after the change" 200 "$(code -b "$TD2/jar2" $B2/api/config)"
check "the old password no longer signs in" 401 "$(code -d 'username=admin&password=Changeme1!' $B2/login)"
check "admin adds a user with a temporary password" 200 "$(code -b "$TD2/jar2" -H 'Content-Type: application/json' -d '{"name":"bob","password":"Temp-Password-1","role":"viewer"}' $B2/api/auth/users)"
check "that user must change it at first sign-in" "http://$B2/change-password" "$(curl -s -o /dev/null -w '%{redirect_url}' -d 'username=bob&password=Temp-Password-1' $B2/login)"
check "role change without a password" 200 "$(code -b "$TD2/jar2" -H 'Content-Type: application/json' -d '{"name":"bob","role":"admin"}' $B2/api/auth/users)"
check "an administrator can be removed while another remains" 200 "$(code -b "$TD2/jar2" -X DELETE "$B2/api/auth/users?name=bob")"
check "the last administrator cannot be removed" 400 "$(code -b "$TD2/jar2" -X DELETE "$B2/api/auth/users?name=admin")"
exit $fail
