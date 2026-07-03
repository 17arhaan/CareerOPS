---
description: Update the pipeline stage of a tracked application.
argument-hint: "<application id> <stage>"
allowed-tools: Read, Edit, Bash
---

Update an application's stage from `$ARGUMENTS` (first token is the id, rest is
the stage).

Valid stages: Applied, Screening, Online Assessment, Phone Screen,
Interviewing, Onsite, Offered, Rejected, Withdrawn.

1. In `tracker/state.json` `applied_companies`, find the entry whose `id`
   matches, set its `stage`. If no id matches, try to match by company name and
   confirm which one.
2. Bump `as_of`, then run `python3 scripts/render_dashboard.py`.
3. Confirm the change in one line. (The dashboard stage dropdown calls this
   when opened as a file; in server mode the dropdown writes directly.)
