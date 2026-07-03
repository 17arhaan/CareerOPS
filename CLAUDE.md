# CareerOPS — Job Search Command Center

This is a Claude Code project that runs the user's job search end to end:
sourcing verified roles, writing cover letters, tracking a pipeline, prepping
interviews, and automating the daily grind. Everything here actually runs:
real file generation, real API calls, real scheduled execution.

**Rule of precedence:** if anything in this file conflicts with a slash command
or runtime input, the slash command / runtime input wins.

---

## Who you are working for

Everything personal lives in gitignored files. **Read them before any
personalized work** (packets, cover letters, outreach, interview prep):

- `profile/profile.md` — identity, goal, flagship stories, cover-letter rules,
  writing style, alumni school. The single source of truth about the user.
- `resume/current.md` — the production resume.
- `preferences/job-search-preferences.md` — canonical search rules (experience
  filter, location mix, sources, skip list). Read before any packet or
  suggestion work.
- `preferences/lessons.md` — hard-won sourcing lessons. Read before every
  packet; append whenever a new failure mode shows up.

If `profile/profile.md` does not exist, this is a fresh clone: tell the user to
run `/setup` and stop. Do not guess an identity.

## File conventions

```
CLAUDE.md                         # this file
profile/profile.md                # who the user is (gitignored; /setup writes it)
preferences/job-search-preferences.md   # canonical search rules (gitignored)
preferences/lessons.md            # sourcing lessons, appended over time
.mcp.json                         # MCP servers: JobSpy + LinkedIn (scripts/setup-mcp.sh)
vendor/                           # cloned third-party MCP servers (gitignored)
resume/current.md                 # production resume (gitignored)
resume/versions/                  # A/B resume variants (gitignored)
tracker/state.json                # source of truth: applied + current queue (gitignored)
tracker/feedback.json             # approve/reject history (gitignored)
packets/apply-packet-YYYY-MM-DD.md  # daily markdown packets (gitignored)
coverletters/{company}-{role}-{date}.md  # generated cover letters (gitignored)
notes/                            # interview prep + company research (gitignored)
scripts/                          # app server, dashboard renderer, URL verifier, cron
dashboard/index.html              # static dashboard snapshot (gitignored, rendered)
.claude/commands/                 # slash commands
```

After any change to `tracker/state.json`, regenerate the dashboard:
`python3 scripts/render_dashboard.py`.

## Hard rules for any generated text

The user's own style rules live in `profile/profile.md` (writing style +
cover letter rules) and override these defaults. Defaults:

- Cover letters: 150 to 220 words, one page max; open with the role + the
  user's current status; cite one work story plus one personal project from
  the profile's flagship stories, paraphrased, never copied from the resume.
- Sign cover letters and emails exactly as the profile specifies.
- No recruiter-bait words (passionate, innovative, thrilled, great fit,
  synergy). Be direct, write like a peer engineer.
- Honor the profile's punctuation rules (e.g. the no-em-dash rule) in every
  generated artifact, including packets and notes.

## URL durability rule (applies to every packet)

URLs MUST point to a specific role posting, not a careers index. Preference order:

1. Indeed `/viewjob?jk=...` (stable for the listing's life)
2. Direct ATS posting: Greenhouse `job-boards.greenhouse.io/{tenant}/jobs/{id}`,
   Lever `jobs.lever.co/{tenant}/{uuid}`, Ashby `jobs.ashbyhq.com/{tenant}/{uuid}`,
   Workday with the job id in the path
3. LinkedIn `linkedin.com/jobs/view/{id}`
4. Avoid marketing careers pages and filter URLs that strip query params.

**Always verify before including.** Run `python3 scripts/verify_urls.py <url>...`
or WebFetch each URL. If it 404s, redirects to a careers index, or shows
"position closed", drop it and find another.

**Verify seniority from the JD, not the title.** Titles lie: roles labeled
"Associate", "MTS 1", "Engineer 1" have shipped with JDs demanding 2 to 7
years. For every candidate, read the JD (Indeed `get_job_details` or fetch it)
and reject anything outside the experience filter in the preferences file.
Mark each queued role `applyable` true/false with a reason. See
`preferences/lessons.md`, which the daily-packet workflow must read and apply
every run. Add to that file whenever a new failure mode shows up so the system
keeps improving.

## Working style

Direct, concise, peer-to-peer. Action first; do not ask three questions when
one will do. Honest when something cannot be done. Default to the simplest
thing that runs.
