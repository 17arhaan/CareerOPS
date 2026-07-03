---
description: Full morning run — refresh tracker, build the daily packet, draft follow-ups, write the brief.
argument-hint: "[YYYY-MM-DD optional, defaults to today]"
allowed-tools: Read, Write, Edit, Bash, WebSearch, WebFetch
---

Run the complete morning autopilot. This is the command cron/launchd fires every
day; it must finish without asking the user anything. Date is `$1` or `date +%F`.

## 0. Preflight

If `profile/profile.md` does not exist, write a single line to stdout telling
the user to run `/setup`, and stop. Do not guess.

## 1. Refresh the tracker (best effort)

If the Gmail MCP tools (`search_threads`, `get_thread`) are available in this
session, follow the `/refresh-tracker` workflow exactly (noise-filtered
confirmations + stage updates). If Gmail is not available (typical for headless
runs), skip silently and note "Gmail: not connected" for the brief.

## 2. Build the daily packet

Follow the `/daily-packet` workflow exactly: read profile, preferences,
lessons, and state; source 10-12 roles; verify every link AND every JD against
the experience filter; write the packet + cover letters; update
`current_queue` and the 14-day skip rotation; regenerate the dashboard.
If sourcing tools are limited, ship however many verified roles you found and
record the shortfall; never pad with unverified roles.

## 3. Follow-ups due

From `tracker/state.json`, find applications at stage "Applied" for 7+ days.
For the 3 most promising (biggest company or best role fit), draft follow-up
emails per the `/follow-up` rules and save them to
`coverletters/followup-{company}-{date}.md` (skip any that already have a
followup file from the last 7 days). List the rest by name.

## 4. Write the morning brief

Write `briefs/brief-{date}.md` (create `briefs/` if needed):

- **Packet:** N confirmed-applyable roles (company + role + location list).
- **Follow-ups:** drafted (with file paths) and remaining.
- **Pipeline:** anything that moved since yesterday; days left to the target
  date and 7-day pace vs the daily goal.
- **One action:** the single most important thing to do today.

Honor the profile's style rules throughout.

## 5. Final line

End with exactly one summary line (it becomes the desktop notification), e.g.:
`Autopilot: 9 roles queued, 2 follow-ups drafted, 3 due. Brief: briefs/brief-2026-07-04.md`
