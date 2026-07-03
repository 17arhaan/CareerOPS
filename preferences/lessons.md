# Lessons Learned — sourcing and verification

The daily-packet workflow MUST read this file and apply every rule. Each entry came from
a real failure observed while running the system (the first entries date from an
entry-level search in India; the rules generalize). Add to it whenever a role turns out
wrong after the fact, so the system keeps improving for you.

## L1. Job titles lie about seniority (2026-06-10)

On 2026-06-10, 5 of 10 Indeed-sourced roles had entry-level titles but mid/senior JDs:
- HPE "Software Engineer" → JD required 2-4 years.
- eBay "MTS 1, Software Engineer" → JD required 6+ years, body said "Staff Software Engineer".
- Experian "Software Engineer, Associate" → JD required 3-5 years.
- Equifax "Software Engineer" → JD required 2+ years.
- Branch "Data Platform Engineer" → actually a Senior role, 4-7 years.

**Rule:** never trust the title alone. For every candidate, call
`mcp__claude_ai_Indeed__get_job_details` (or fetch the JD) and parse the
years-of-experience requirement. Reject if the JD asks for more than 1 year, even if the
title says Associate / Engineer 1 / MTS 1 / new grad. Words like "Associate" and "MTS 1"
do not guarantee entry level.

## L2. Indeed blocks direct URL verification (2026-06-10)

`to.indeed.com` and `indeed.com` links return HTTP 403 to the local verifier and to
WebFetch. Do not treat that as a dead link. Indeed links are validated at source by the
Indeed MCP. `scripts/verify_urls.py` now returns TRUSTED for them. Use `get_job_details`
to confirm liveness and read the JD, not a raw fetch.

## L3. Confirm before queueing (2026-06-10)

Every role placed in the packet and the queue must carry a confirmation verdict:
- `applyable: true` only when the link is live AND the JD fits the 0-1 year filter.
- `applyable: false` with a one-line reason otherwise (years required, wrong stack,
  posting closed, wrong link). The dashboard renders this so nothing untested ships.

## L4. Stack mismatch is a soft no (2026-06-10)

Shops whose stack is entirely off the user's core skills (see `profile/profile.md` and
the resume) are not an automatic reject, but deprioritize them versus on-stack roles
when filling the daily quota.

## L5. Indeed India alone is too thin for entry roles (2026-06-10)

After JD-verification, a full day of Indeed India searches yielded only ~6 genuine 0-1 year
roles. The rest were senior roles with junior titles, Accenture 7.5-year "Custom Software
Engineer" postings, QA/support, internships, or non-tech. The curated GitHub list
`samiranghosh04/new-grad-tech-roles--india` is stale (last real entries 2023).

**Rule:** do not pad the queue to hit 10 with off-filter roles. Ship the verified set and
state the shortfall. To reliably reach 10/day, broaden sourcing beyond Indeed:
- **JobSpy MCP** for Naukri + LinkedIn + Glassdoor (the India-entry volume lives on Naukri).
- **LinkedIn MCP** `search_jobs` (read-only) for new-grad postings.
- Unstop and direct ATS boards (Greenhouse/Lever/Ashby) for company grad programs.
Both MCPs are wired in `.mcp.json`; run `scripts/setup-mcp.sh` and launch Claude Code so
they are available to `/daily-packet`.
