---
description: Weekly recap — apps sent, response rate, follow-up candidates.
allowed-tools: Read, Bash
---

Produce the weekly digest.

1. Read `tracker/state.json`. Today is `date +%F`. Daily goal comes from
   `settings.daily_goal`; the deadline from `target_offer_date`.
2. Compute: applications in the last 7 days, unique companies in the last 30
   days, current pipeline counts by stage, and response rate (companies with
   any non-Applied stage divided by total applied).
3. Identify follow-up candidates: companies applied 7+ days ago still at stage
   "Applied" with no reply.
4. Print a tight recap: counts, response rate, the follow-up list with a
   suggested next action per company, and whether the daily pace is on track
   for the target date. No file writes unless asked.
