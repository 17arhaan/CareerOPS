#!/usr/bin/env bash
# Install / inspect / remove the CareerOPS schedule.
#
#   scripts/setup-automation.sh install                # 07:00 autopilot, Mon 09:00 digest
#   scripts/setup-automation.sh install --autopilot 06:30 --digest 08:00 --digest-day 1
#   scripts/setup-automation.sh status
#   scripts/setup-automation.sh uninstall
#
# macOS: installs launchd agents (better than cron on laptops: a run missed
# while the lid was closed fires on wake). Linux: installs crontab entries
# between marker comments. Both call scripts/run-claude.sh, which handles
# PATH, locking, logging, and notifications.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNNER="$ROOT/scripts/run-claude.sh"
ACTION="${1:-status}"; shift || true

AUTOPILOT_TIME="07:00"
DIGEST_TIME="09:00"
DIGEST_DAY="1"   # 0=Sun ... 6=Sat (launchd Weekday and cron agree on 0-6, Sunday=0)

while [ $# -gt 0 ]; do
  case "$1" in
    --autopilot) AUTOPILOT_TIME="$2"; shift 2 ;;
    --digest)    DIGEST_TIME="$2"; shift 2 ;;
    --digest-day) DIGEST_DAY="$2"; shift 2 ;;
    *) echo "unknown flag: $1" >&2; exit 2 ;;
  esac
done

hh() { echo "${1%%:*}" | sed 's/^0//'; }
mm() { echo "${1##*:}" | sed 's/^0//'; }
AP_H="$(hh "$AUTOPILOT_TIME")"; AP_M="$(mm "$AUTOPILOT_TIME")"; AP_M="${AP_M:-0}"
DG_H="$(hh "$DIGEST_TIME")";   DG_M="$(mm "$DIGEST_TIME")";   DG_M="${DG_M:-0}"

IS_MAC=false; [ "$(uname)" = "Darwin" ] && IS_MAC=true
AGENTS_DIR="$HOME/Library/LaunchAgents"
AP_LABEL="com.careerops.autopilot"
DG_LABEL="com.careerops.digest"
CRON_BEGIN="# >>> careerops automation >>>"
CRON_END="# <<< careerops automation <<<"

write_plist() { # $1 label, $2 command, $3 hour, $4 minute, $5 extra-cal-keys
  cat >"$AGENTS_DIR/$1.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$1</string>
  <key>ProgramArguments</key>
  <array><string>/bin/bash</string><string>$RUNNER</string><string>$2</string></array>
  <key>StartCalendarInterval</key>
  <dict><key>Hour</key><integer>$3</integer><key>Minute</key><integer>$4</integer>$5</dict>
  <key>StandardOutPath</key><string>$ROOT/logs/launchd.log</string>
  <key>StandardErrorPath</key><string>$ROOT/logs/launchd.log</string>
</dict></plist>
EOF
}

install_mac() {
  mkdir -p "$AGENTS_DIR" "$ROOT/logs"
  write_plist "$AP_LABEL" "/autopilot" "$AP_H" "$AP_M" ""
  write_plist "$DG_LABEL" "/weekly-digest" "$DG_H" "$DG_M" "<key>Weekday</key><integer>$DIGEST_DAY</integer>"
  for l in "$AP_LABEL" "$DG_LABEL"; do
    launchctl unload "$AGENTS_DIR/$l.plist" 2>/dev/null || true
    launchctl load "$AGENTS_DIR/$l.plist"
  done
  echo "Installed launchd agents:"
  echo "  $AP_LABEL      daily $AUTOPILOT_TIME  -> /autopilot"
  echo "  $DG_LABEL      weekday $DIGEST_DAY $DIGEST_TIME -> /weekly-digest"
  echo "Logs land in $ROOT/logs/. Test now with:  scripts/run-claude.sh \"/status\""
}

install_cron() {
  local tmp; tmp="$(mktemp)"
  (crontab -l 2>/dev/null || true) | sed "/^$CRON_BEGIN\$/,/^$CRON_END\$/d" >"$tmp"
  {
    echo "$CRON_BEGIN"
    echo "$AP_M $AP_H * * *  cd $ROOT && scripts/run-claude.sh \"/autopilot\" >> logs/cron.log 2>&1"
    echo "$DG_M $DG_H * * $DIGEST_DAY  cd $ROOT && scripts/run-claude.sh \"/weekly-digest\" >> logs/cron.log 2>&1"
    echo "$CRON_END"
  } >>"$tmp"
  crontab "$tmp"; rm -f "$tmp"
  echo "Installed crontab entries (crontab -l to inspect):"
  echo "  daily $AUTOPILOT_TIME -> /autopilot ; weekday $DIGEST_DAY $DIGEST_TIME -> /weekly-digest"
}

uninstall_all() {
  if $IS_MAC; then
    for l in "$AP_LABEL" "$DG_LABEL"; do
      launchctl unload "$AGENTS_DIR/$l.plist" 2>/dev/null || true
      rm -f "$AGENTS_DIR/$l.plist"
    done
    echo "Removed launchd agents."
  fi
  if command -v crontab >/dev/null 2>&1; then
    local tmp; tmp="$(mktemp)"
    (crontab -l 2>/dev/null || true) | sed "/^$CRON_BEGIN\$/,/^$CRON_END\$/d" >"$tmp"
    crontab "$tmp" 2>/dev/null || true; rm -f "$tmp"
    echo "Removed crontab entries (if any)."
  fi
}

status_all() {
  if $IS_MAC; then
    echo "launchd:"
    launchctl list 2>/dev/null | grep careerops || echo "  (not installed)"
  fi
  echo "crontab:"
  (crontab -l 2>/dev/null | sed -n "/^$CRON_BEGIN\$/,/^$CRON_END\$/p") | grep -v "^#" || echo "  (not installed)"
  echo "recent runs:"
  ls -1t "$ROOT"/logs/*.log 2>/dev/null | head -5 || echo "  (no logs yet)"
}

case "$ACTION" in
  install)   if $IS_MAC; then install_mac; else install_cron; fi ;;
  uninstall) uninstall_all ;;
  status)    status_all ;;
  *) echo "usage: setup-automation.sh install|status|uninstall [--autopilot HH:MM] [--digest HH:MM] [--digest-day 0-6]" >&2; exit 2 ;;
esac
