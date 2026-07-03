---
description: First-run onboarding — interview the user and personalize CareerOPS end to end.
argument-hint: "(no arguments)"
allowed-tools: Read, Write, Edit, Bash, AskUserQuestion, WebSearch
---

Onboard a new CareerOPS user. Interview them, then generate every personal file.
Be warm but efficient: batch questions, never ask what you can infer, and show a
summary before writing.

## 1. Check state

If `profile/profile.md` already exists, say so and ask whether to update it or
start over. Otherwise proceed.

## 2. Interview (batch into 3-4 rounds, not 20 questions)

Round A — identity: name, email, phone, city/country, LinkedIn + GitHub +
website URLs, current status (student / intern / employed, where), education.

Round B — the goal: target role types (SWE / backend / ML / data / etc.),
years of experience (drives the seniority filter), target deadline date,
daily application goal (suggest 10), location mix (which cities, how many
on-site vs remote per day), sponsorship constraints.

Round C — resume: ask them to paste their resume text, or point to a file
(read PDFs directly if given a path). If they have nothing, offer to draft a
skeleton from the interview answers.

Round D — voice: pull 2-4 flagship stories out of the resume yourself and
confirm them (each needs a number that proves impact); confirm the cover
letter signature; ask their university's LinkedIn slug for alumni search
(look it up with WebSearch if they don't know it); ask if they want the
default style rules (no em dashes, no recruiter-bait words) kept.

## 3. Write the files

Using `profile/profile.example.md` and
`preferences/job-search-preferences.example.md` as structure references:

1. `profile/profile.md` — filled in completely.
2. `preferences/job-search-preferences.md` — real titles/skip rules for their
   experience level, their cities, their sources. Pick the job boards that
   dominate THEIR region (e.g. Naukri for India, Seek for Australia); keep the
   GitHub curated new-grad lists if they are entry level.
3. `resume/current.md` — their resume as clean markdown.
4. `tracker/state.json` — copy `tracker/state.example.json`, then set
   `target_offer_date` and `settings`: `daily_goal`, `user_name` (first name),
   `alumni_school_slug` (LinkedIn school slug). Only create if missing; never
   overwrite an existing state.json without explicit confirmation.
5. `tracker/feedback.json` — copy from `tracker/feedback.example.json` if missing.
6. If `preferences/lessons.md` is missing, create it with just the header
   explaining its purpose (sourcing lessons accumulate there over time).

## 4. Finish

1. Run `python3 scripts/render_dashboard.py` to build the first dashboard.
2. Print a tight "you're live" summary:
   - `python3 scripts/serve_dashboard.py` then http://localhost:8787 (the app)
   - `/daily-packet` to build the first batch of verified roles
   - `/status` for the morning briefing
   - Optional next steps: `.env` with ANTHROPIC_API_KEY for the in-app copilot,
     `scripts/setup-mcp.sh` for JobSpy/LinkedIn sourcing, cron via
     `scripts/crontab.example`.
3. One-line reminder that everything personal lives in gitignored files, so
   their data stays local even if they fork/push the repo.
