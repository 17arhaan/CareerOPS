#!/usr/bin/env bash
# Cron wrapper: invoke a CareerOPS slash command headlessly and log the output.
#
#   scripts/run-claude.sh "/daily-packet"
#   scripts/run-claude.sh "/refresh-tracker"
#   scripts/run-claude.sh "/weekly-digest"
#
# Suggested crontab (see scripts/crontab.example):
#   0 6 * * *  cd ~/Coding/CareerOPS && scripts/run-claude.sh "/daily-packet"
#   0 7 * * *  cd ~/Coding/CareerOPS && scripts/run-claude.sh "/refresh-tracker"
#   0 9 * * 1  cd ~/Coding/CareerOPS && scripts/run-claude.sh "/weekly-digest"
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
mkdir -p logs

CMD="${1:?usage: run-claude.sh \"/slash-command [args]\"}"
STAMP="$(date +%Y-%m-%dT%H%M%S)"
SLUG="$(echo "$CMD" | tr -cd '[:alnum:]-' | cut -c1-40)"
LOG="logs/${STAMP}-${SLUG}.log"

# Requires the Claude Code CLI on PATH. Headless mode runs the command and exits.
claude -p "$CMD" >"$LOG" 2>&1
echo "$(date) :: ran '$CMD' -> $LOG"
