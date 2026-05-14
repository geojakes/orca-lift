#!/usr/bin/env bash
#
# Build the orca-lift backend image on this workstation (using the local SSH
# agent to fetch the private `orca` package) and ship it to a Synology NAS.
#
# Required env vars:
#   NAS_HOST      SSH host of the NAS (e.g. user@synology.local)
#
# Optional:
#   IMAGE_TAG     Defaults to orca-lift:latest
#   NAS_DOCKER    Docker socket path on the NAS. Defaults to `sudo /usr/local/bin/docker`
#                 which works on stock DSM with Container Manager.
#
# Usage:
#   NAS_HOST=admin@nas.local ./deploy/synology/build-and-ship.sh

set -euo pipefail

cd "$(dirname "$0")/../.."

: "${NAS_HOST:?Set NAS_HOST=user@host}"
: "${IMAGE_TAG:=orca-lift:latest}"
: "${NAS_DOCKER:=sudo /usr/local/bin/docker}"

# Make sure SSH agent is loaded — buildkit's `--ssh default` reads from $SSH_AUTH_SOCK.
if [ -z "${SSH_AUTH_SOCK:-}" ] || ! ssh-add -l >/dev/null 2>&1; then
    echo "ERROR: no SSH identities loaded. Run \`ssh-add\` first so buildkit can fetch the private orca repo." >&2
    exit 1
fi

echo "==> Building $IMAGE_TAG (linux/amd64) with SSH agent forwarding"
docker buildx build \
    --platform linux/amd64 \
    --ssh default \
    -f backend/Dockerfile \
    -t "$IMAGE_TAG" \
    --load \
    .

echo "==> Shipping image to $NAS_HOST"
docker save "$IMAGE_TAG" | gzip | ssh "$NAS_HOST" "gunzip | $NAS_DOCKER load"

echo "==> Done. On the NAS:"
echo "    cd /volume1/docker/orca-lift && $NAS_DOCKER compose up -d"
