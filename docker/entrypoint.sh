#!/bin/sh
# Everything ARIA writes (Active IQ tokens, cache, user accounts, reference data) lives on the volume at $ARIA_DATA_DIR.
# /app/data is a link to /var/lib/aria/data made when the image is built; if you change ARIA_DATA_DIR, mount the volume at the new path
# and keep it a directory that contains a "data" folder.
set -e
DATA="${ARIA_DATA_DIR:-/var/lib/aria}"
mkdir -p "$DATA/data"
if [ "$DATA" != "/var/lib/aria" ]; then
  ln -sfn "$DATA/data" /app/data 2>/dev/null || echo "[entrypoint] could not link /app/data to $DATA/data (read-only root filesystem?)"
fi
exec python /app/server.py "$@"
