---
description: Suggest 10 new roles not already applied to or recently recommended.
argument-hint: "[role-type or city filter, optional]"
allowed-tools: Read, WebSearch, WebFetch, Bash
---

Suggest 10 fresh roles.

1. Read `preferences/job-search-preferences.md`, `preferences/lessons.md`, and
   `tracker/state.json`.
2. Optional filter from `$ARGUMENTS` (e.g. "data analyst", "Berlin only").
3. Find 10 roles passing all hard filters (experience level, locations),
   excluding every company in `applied_companies`, the static skip list, and
   `previously_recommended_skip_14d`. Keep the preferences' on-site/remote mix
   unless the filter says otherwise.
4. Verify URLs with `python3 scripts/verify_urls.py` and prefer durable
   ATS/Indeed/LinkedIn links.
5. Print a numbered list: company, role, location, type, verified URL, one-line
   why. Do not modify state.json (this is suggestion-only; use /daily-packet to
   commit a batch).
