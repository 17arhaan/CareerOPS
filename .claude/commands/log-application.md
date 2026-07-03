---
description: Manually log a portal application that has no Gmail confirmation.
argument-hint: "<company> <role> <location> <url> [YYYY-MM-DD]"
allowed-tools: Read, Edit, Bash
---

Log a manual application.

Parse `$ARGUMENTS` into company, role, location, url, and optional date
(default today via `date +%F`). Derive `jobId` from the URL if one is present
(Indeed `jk`, Greenhouse/Lever/Ashby id, Workday id). Infer `source` from the
URL host (Workday / Greenhouse / Lever / Ashby / LinkedIn / Indeed / Portal).

Append to `tracker/state.json` `applied_companies`:
`{ "id": "manual-{slug}-{date}", "company", "role", "location", "jobId", "url",
"source", "applied_date", "stage": "Applied" }`. Bump `as_of`, then run
`python3 scripts/render_dashboard.py`. Confirm the entry you added in one line.
