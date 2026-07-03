#!/usr/bin/env bash
# Headless runner for CareerOPS slash commands. This is the entrypoint that
# cron / launchd fires; it also works by hand:
#
#   scripts/run-claude.sh "/autopilot"
#   scripts/run-claude.sh "/weekly-digest"
#
# What it does beyond `claude -p`:
#   - fixes PATH for cron/launchd's bare environment (finds the claude CLI)
#   - takes a lock so overlapping runs can't corrupt tracker/state.json
#   - logs every run to logs/, keeps the newest 60 logs
#   - sends a desktop notification with the result (macOS)
#   - runs with --permission-mode acceptEdits; the tool allowlist lives in
#     .claude/settings.json, so no --dangerously-skip-permissions needed.
#
# Install the schedule with:  scripts/setup-automation.sh install
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
mkdir -p logs

# cron/launchd start with a minimal PATH; add the usual CLI install locations.
export PATH="$HOME/.claude/local:$HOME/.local/bin:$HOME/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
CLAUDE_BIN="${CLAUDE_BIN:-claude}"

CMD="${1:?usage: run-claude.sh \"/slash-command [args]\"}"
STAMP="$(date +%Y-%m-%dT%H%M%S)"
SLUG="$(echo "$CMD" | tr -cd '[:alnum:]-' | cut -c1-40)"
LOG="logs/${STAMP}-${SLUG}.log"

notify() { # $1 = title, $2 = message
  if [ "$(uname)" = "Darwin" ] && command -v osascript >/dev/null 2>&1; then
    osascript -e "display notification \"${2//\"/}\" with title \"${1//\"/}\"" >/dev/null 2>&1 || true
  fi
}

if ! command -v "$CLAUDE_BIN" >/dev/null 2>&1; then
  echo "$(date) :: claude CLI not found on PATH ($PATH)" | tee "$LOG" >&2
  notify "CareerOPS failed" "claude CLI not found; check PATH in run-claude.sh"
  exit 127
fi

# Single-flight lock (mkdir is atomic). A stale lock older than 3h is removed.
LOCK="logs/.run-claude.lock"
if ! mkdir "$LOCK" 2>/dev/null; then
  if [ -n "$(find "$LOCK" -maxdepth 0 -mmin +180 2>/dev/null)" ]; then
    rm -rf "$LOCK" && mkdir "$LOCK"
  else
    echo "$(date) :: another run is in progress, skipping '$CMD'" >>"logs/cron.log"
    exit 0
  fi
fi
trap 'rm -rf "$LOCK"' EXIT

echo "$(date) :: starting '$CMD'" >"$LOG"
set +e
"$CLAUDE_BIN" -p "$CMD" --permission-mode acceptEdits >>"$LOG" 2>&1
STATUS=$?
set -e

# The command's final line doubles as the notification body.
LAST_LINE="$(tail -n 1 "$LOG" 2>/dev/null | cut -c1-180)"
if [ $STATUS -eq 0 ]; then
  echo "$(date) :: ran '$CMD' -> $LOG"
  notify "CareerOPS" "${LAST_LINE:-$CMD done}"
else
  echo "$(date) :: FAILED ($STATUS) '$CMD' -> $LOG" >&2
  notify "CareerOPS failed" "$CMD exited $STATUS; see $LOG"
fi

# Keep the newest 60 logs.
ls -1t logs/*.log 2>/dev/null | tail -n +61 | xargs rm -f 2>/dev/null || true

exit $STATUS
