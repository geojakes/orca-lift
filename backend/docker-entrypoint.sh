#!/usr/bin/env sh
set -e

# DATA_DIR is where the SQLite DB lives; created on a bind-mounted volume
# in production (see compose.yaml).
: "${ORCA_LIFT_DATA_DIR:=/data}"
mkdir -p "$ORCA_LIFT_DATA_DIR"

# `orcafit init` is idempotent: CREATE TABLE IF NOT EXISTS + INSERT OR IGNORE.
# Running on every boot ensures schema migrations + exercise library are
# applied to whatever DB is in the volume.
if [ "$1" = "serve" ] || [ -z "$1" ]; then
    orcafit init
    shift 2>/dev/null || true
    exec orcafit serve --host 0.0.0.0 --port "${PORT:-8000}" ${VERBOSE:+--verbose}
fi

# Pass anything else through (e.g. `docker exec orca-lift orcafit generate ...`)
exec orcafit "$@"
