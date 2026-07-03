#!/usr/bin/env bash
# Reproducible setup for the CareerOPS MCP servers configured in .mcp.json.
# Safe to re-run. Requires: git, node/npm, uv/uvx, docker (Docker Desktop running).
#
#   scripts/setup-mcp.sh
#
# After this, launch Claude Code in the repo root and the servers load automatically.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> Checking prerequisites"
for bin in git node npm uvx docker; do
  command -v "$bin" >/dev/null || { echo "MISSING: $bin"; exit 1; }
done

echo "==> JobSpy MCP (LinkedIn + Naukri + Indeed + Glassdoor + more)"
mkdir -p vendor
if [ ! -d vendor/jobspy-mcp-server ]; then
  git clone --depth 1 https://github.com/borgius/jobspy-mcp-server.git vendor/jobspy-mcp-server
fi
( cd vendor/jobspy-mcp-server && npm install --no-audit --no-fund )
echo "    Building the jobspy scraper Docker image (needs Docker Desktop running)..."
if docker info >/dev/null 2>&1; then
  docker build -t jobspy ./vendor/jobspy-mcp-server/jobspy
else
  echo "    Docker daemon not running. Start Docker Desktop, then re-run this script."
fi

echo "==> LinkedIn MCP (uvx self-bootstraps on first launch)"
echo "    No build needed. On first use it opens a browser to log into your LinkedIn"
echo "    account once and saves the session to ~/.linkedin-mcp/."
echo "    SAFETY: use read-only (search_people, get_company_employees, search_jobs)."
echo "    Do NOT auto-send messages or connections. ToS ban risk."

echo "==> Done. MCP servers are declared in .mcp.json:"
python3 -c "import json;print('   ', ', '.join(json.load(open('.mcp.json'))['mcpServers']))"
echo "    Launch Claude Code in this folder to connect them."
