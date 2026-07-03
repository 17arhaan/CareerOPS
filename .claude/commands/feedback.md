---
description: Record approve/reject feedback on a recommended role; auto-tune the skip list.
argument-hint: "approve|reject <company> [role] [reason]"
allowed-tools: Read, Edit, Bash
---

Record feedback from `$ARGUMENTS` (first token is approve or reject, then
company, optional role, optional reason).

1. Append `{ company, role, reason, date }` to the matching array in
   `tracker/feedback.json` and mirror it into `state.json` `feedback_log`.
2. If this is the 3rd+ rejection sharing a clear pattern (same company, or same
   role-type/location signal in the reasons), add that company or pattern to
   the skip list in `preferences/job-search-preferences.md` and say you did so.
3. Print a one-line confirmation and, if a pattern triggered, what you added to
   the skip list.
