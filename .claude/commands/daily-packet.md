---
description: Build today's apply packet (10 fresh verified roles) and update the tracker.
argument-hint: "[YYYY-MM-DD optional, defaults to today]"
allowed-tools: Read, Write, Edit, Bash, WebSearch, WebFetch
---

Build the daily apply packet.

## Steps

1. Read `profile/profile.md` (who the user is + cover letter rules),
   `preferences/job-search-preferences.md` (canonical rules),
   `preferences/lessons.md` (hard-won sourcing lessons, apply every rule), and
   `tracker/state.json` (already-applied companies + the 14-day skip rotation).
   Today's date is `$1` if given, otherwise use `date +%F`.

2. Source 10 to 12 fresh roles using WebSearch (and the JobSpy / LinkedIn /
   Indeed MCPs if connected) across the priority sources in the preferences
   file. Enforce every hard filter from the preferences:
   - Experience level: honor the acceptable-titles and skip lists exactly.
   - Location mix: match the on-site/hybrid vs remote split and city priority.
   - Skip every company in `applied_companies`, the static skip list, and
     `previously_recommended_skip_14d`.

3. **Verify every role before including it (two checks, both required):**
   a. **Link live:** run `python3 scripts/verify_urls.py "<url1>" ...` for
      non-Indeed URLs. For Indeed links the verifier returns TRUSTED (Indeed
      blocks direct fetch; they are validated at source by the MCP). Prefer
      specific ATS / Indeed / LinkedIn `/jobs/view/` URLs over careers-index pages.
   b. **JD fits the experience filter (lesson L1):** for every candidate read
      the actual JD (Indeed `get_job_details` if available, else fetch it) and
      check the years-of-experience requirement. **Reject anything outside the
      filter, even if the title looks right.** Titles lie about seniority.
      Record `applyable` (true/false) and a one-line `applyable_reason` per role.
   Retry up to 3 candidates per slot. Aim for 10 confirmed-applyable roles; if
   you cannot reach 10, ship what is confirmed and say how many short you are.
   Do NOT pad the queue with off-filter roles.

4. Write `packets/apply-packet-{date}.md`. For each role: H2 with company, then
   Location, Apply URL, Why this fits (2 to 3 sentences), and a tailored cover
   letter following the profile's cover-letter rules. Also save each letter to
   `coverletters/{company}-{role}-{date}.md`.

5. Update `tracker/state.json`: set `current_queue` to
   `{ "date": "{date}", "roles": [...] }` with
   `{company, role, location, type, url, applyable, applyable_reason}` per role,
   and append the newly recommended company names to
   `previously_recommended_skip_14d`.

6. Regenerate the dashboard: `python3 scripts/render_dashboard.py`.

7. Print a one-line summary: how many roles, the location mix, and any slots
   where you had to fall back to a careers-index URL because no durable posting
   could be verified.
