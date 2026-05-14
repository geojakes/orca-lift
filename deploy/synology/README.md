# Running orca-lift on Synology

Target setup:

- Synology DSM 7.x with **Container Manager** installed
- x86_64 (amd64) Synology model
- LAN-only access (no TLS / reverse proxy)
- SQLite DB persisted under `/volume1/docker/orca-lift/data`
- Image built on a workstation with SSH agent forwarding (so the build can
  fetch the private `orca` package), then loaded onto the NAS

The runtime image is small: Python 3.13 + the project venv. The Claude Agent
SDK ships a bundled native `claude` binary inside its wheel, so no Node.js or
separate `claude` install is required inside the container. Auth at runtime
is via env var (see "Authentication" below).

## One-time NAS prep

1. SSH into the NAS as an admin user (enable SSH in `Control Panel → Terminal & SNMP`).
2. Create the data directory:
   ```sh
   sudo mkdir -p /volume1/docker/orca-lift/data
   sudo chmod 777 /volume1/docker/orca-lift/data   # simplest cross-DSM-version option
   ```
3. Copy `compose.yaml` and `.env.example` from this repo into `/volume1/docker/orca-lift/`:
   ```sh
   scp compose.yaml admin@nas.local:/volume1/docker/orca-lift/
   scp .env.example admin@nas.local:/volume1/docker/orca-lift/.env
   ```
4. Edit `/volume1/docker/orca-lift/.env` on the NAS and fill in either
   `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN` (see below).

## Authentication

The orca framework calls Claude via the Claude Agent SDK. Two options:

### Option A — Pay-as-you-go API key (simplest)

Set in `.env`:
```
ANTHROPIC_API_KEY=sk-ant-...
```
Billed against your Anthropic Console account.

### Option B — Claude Code OAuth (use your Claude subscription)

Run on your workstation (where you're already logged in to Claude Code):

```sh
claude setup-token
```

This prints a long-lived token. Set in `.env` on the NAS:

```
CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-...
```

Usage is then billed via your Claude subscription instead of API credits. The
token is long-lived but tied to your account — rotate it if a NAS is shared.

## Build and ship the image

From the repo root on your workstation:

```sh
ssh-add                              # make sure your GitHub SSH key is loaded
NAS_HOST=admin@nas.local ./deploy/synology/build-and-ship.sh
```

The script:

1. Runs `docker buildx build --platform linux/amd64 --ssh default …` so the
   build can clone the private `orca` repo using your SSH agent.
2. `docker save | gzip | ssh nas "gunzip | sudo docker load"` to transfer the
   image to the NAS without needing a registry.

If your NAS uses a different docker socket path, set `NAS_DOCKER`:

```sh
NAS_HOST=admin@nas.local NAS_DOCKER="sudo docker" ./deploy/synology/build-and-ship.sh
```

## Start the service

Two equivalent options.

### From the SSH shell:

```sh
cd /volume1/docker/orca-lift
sudo docker compose up -d
sudo docker compose logs -f
```

### From DSM Container Manager UI:

1. Open **Container Manager → Project → Create**.
2. Set source to "Use existing docker-compose.yml" and point at
   `/volume1/docker/orca-lift/compose.yaml`.
3. Container Manager picks up the `.env` next to it automatically.
4. Start the project.

## Verify

```sh
curl http://nas.local:8000/health
# {"status":"healthy","version":"0.2.0"}
```

Then point the Android app's `API_BASE_URL` at `http://nas.local:8000`.

## Operational notes

- The entrypoint runs `orcafit init` on every boot. It is idempotent (`CREATE
  TABLE IF NOT EXISTS` + `INSERT OR IGNORE`), so schema migrations and
  exercise-library updates are picked up automatically when you ship a new
  image.
- The SQLite DB lives at `/volume1/docker/orca-lift/data/orca_lift.db`. Back
  it up via Hyper Backup like any other folder.
- To inspect or run a CLI command inside the container:
  ```sh
  sudo docker exec -it orca-lift orcafit programs list
  ```
- Logs are JSON-rotated at 10 MB × 3 files (see `compose.yaml`).
- To upgrade: rerun `build-and-ship.sh` then `sudo docker compose up -d` —
  Container Manager pulls the new image and recreates the container; the
  bind-mounted DB is preserved.
