#!/usr/bin/env bash
# Körs en gång när Codespace/devcontainer skapas. Installerar allt kursen behöver.
set -euo pipefail

UV_VERSION="0.13.4"
K6_VERSION="v2.3.0"

echo "==> Installerar uv ${UV_VERSION}"
curl -LsSf "https://astral.sh/uv/${UV_VERSION}/install.sh" | sh
export PATH="$HOME/.local/bin:$PATH"

echo "==> Installerar Python-paketen (låsta versioner i uv.lock)"
uv sync --locked

echo "==> Installerar Chromium för Playwright"
uv run playwright install --with-deps chromium

echo "==> Installerar Chromium för Playwright MCP (lektion 8)"
npx -y @playwright/mcp@0.0.83 install-browser chromium

echo "==> Installerar k6 ${K6_VERSION}"
arch="$(dpkg --print-architecture)"   # amd64 eller arm64
curl -fsSL "https://github.com/grafana/k6/releases/download/${K6_VERSION}/k6-${K6_VERSION}-linux-${arch}.tar.gz" \
  | sudo tar -xz -C /usr/local/bin --strip-components=1 "k6-${K6_VERSION}-linux-${arch}/k6"

echo "==> Klart. Node $(node --version), k6 $(k6 version | awk '{print $2}'), $(uv --version)"
