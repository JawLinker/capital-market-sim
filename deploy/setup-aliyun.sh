#!/usr/bin/env bash
set -euo pipefail

# One-time setup for an Alibaba Cloud Lightweight Server (Ubuntu 22.04/24.04).
# Installs Docker, pulls the project, and starts the game on port 8000.
#
# Optional env vars:
#   APP_DIR             default: /opt/capital-market-sim
#   REPO_URL            default: https://github.com/JawLinker/capital-market-sim.git
#   CMS_HOST_PASSWORD   default: a random password printed at the end

APP_DIR="${APP_DIR:-/opt/capital-market-sim}"
REPO_URL="${REPO_URL:-https://github.com/JawLinker/capital-market-sim.git}"
CMS_HOST_PASSWORD="${CMS_HOST_PASSWORD:-}"

if [ -z "$CMS_HOST_PASSWORD" ]; then
  CMS_HOST_PASSWORD="$(openssl rand -hex 16)"
  GENERATED_PASSWORD=1
fi

echo "==> Installing Docker if needed"
if ! command -v docker >/dev/null 2>&1; then
  apt-get update
  apt-get install -y ca-certificates curl openssl
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  chmod a+r /etc/apt/keyrings/docker.asc
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" > /etc/apt/sources.list.d/docker.list
  apt-get update
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
fi

echo "==> Fetching project into $APP_DIR"
mkdir -p "$APP_DIR"
if [ -z "$(ls -A "$APP_DIR" 2>/dev/null)" ]; then
  git clone "$REPO_URL" "$APP_DIR"
else
  git -C "$APP_DIR" pull --ff-only
fi

echo "==> Starting the game"
cd "$APP_DIR"
export CMS_HOST_PASSWORD
docker compose up -d --build

echo ""
echo "Deployment finished."
echo "  Open http://<server-public-ip>:8000"
echo "  Host account: host"
if [ "${GENERATED_PASSWORD:-}" = "1" ]; then
  echo "  Host password: $CMS_HOST_PASSWORD   (save this, it will not be shown again)"
else
  echo "  Host password: from your CMS_HOST_PASSWORD env var"
fi
