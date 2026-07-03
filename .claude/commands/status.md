---
description: Morning briefing — goal pace, today's queue, follow-ups, one DSA nudge.
allowed-tools: Read, Bash
---

Give the user a tight morning briefing from `tracker/state.json`. Today is
`date +%F`. Read the daily goal from `settings.daily_goal` (default 10).

Cover, in this order, short and scannable:

1. **Goal pace:** days left to `target_offer_date`, total applied, 7-day pace
   vs the daily goal, current streak.
2. **Today's queue:** how many confirmed-applyable roles are waiting, listed by
   company.
3. **Follow-ups due:** applications at stage "Applied" for 7+ days (suggest
   /follow-up).
4. **Pipeline movement:** anything not at "Applied" (screening, interviewing,
   offer, reject).
5. **One nudge:** suggest running /dsa and, if today's count is 0, a push to
   start applying.

Honor the profile's style rules. End with the single most important action for
today.
