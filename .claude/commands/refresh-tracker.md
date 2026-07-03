---
description: Pull Gmail confirmations + status emails, classify them, update the tracker.
allowed-tools: Read, Write, Edit, Bash
---

Refresh the tracker from Gmail.

1. Search Gmail (last 30 days) for application confirmations and status emails.
   Use the connected Gmail MCP tools (`search_threads`, `get_thread`) if
   available in this session; otherwise tell the user Gmail is not connected
   (claude.ai / Claude settings -> Connectors -> Gmail) and stop.
2. Apply tight noise filtering: skip newsletters, job-board digest emails,
   "guaranteed offer" spam, and any sender that is not a real ATS / recruiter
   domain. A status email (interview / rejection / offer) only counts if its
   company matches one already in `applied_companies`.
3. For each new confirmation, append to `applied_companies` with
   `{id, company, role, location, jobId, url, source, applied_date, stage:"Applied"}`.
   For each status email, update the matching company's `stage` (Screening /
   Online Assessment / Phone Screen / Interviewing / Onsite / Offered /
   Rejected / Withdrawn).
4. Save `tracker/state.json`, bump `as_of`, then run
   `python3 scripts/render_dashboard.py`.
5. Print what changed: new confirmations, stage moves, anything ambiguous you
   skipped.
