# CareerOPS

**A job-search command center that runs inside [Claude Code](https://claude.com/claude-code).**
It sources real, verified job postings every morning, writes tailored cover letters,
tracks your entire pipeline in a local web app, preps you for interviews, and can run
the whole loop on a cron schedule. Your data never leaves your machine.

> Clone it, run `/setup`, and you have a personal job-hunting operations team.

---

## Why this exists

Applying to jobs is a grind with four failure modes: dead links, roles whose JD wants
5 years when the title says "Junior", forgetting to follow up, and generic cover
letters that get ignored. CareerOPS attacks all four:

- **Verified sourcing** — every recommended role passes two checks before you see it:
  the apply link is live (`scripts/verify_urls.py`), and the *actual JD* fits your
  experience filter (titles lie; the JD is read every time).
- **Tailored writing** — cover letters, cold emails, follow-ups, and referral asks are
  generated from *your* profile and resume, citing your real projects with real numbers.
- **A real tracker** — a local web app (pipeline kanban, analytics, networking CRM,
  interview-round logger) backed by one JSON file that both you and the AI write to.
- **Compounding lessons** — every sourcing failure gets recorded in
  `preferences/lessons.md` and applied to every future run. The system gets better the
  longer you use it.

## Quickstart (5 minutes)

Requirements: [Claude Code](https://claude.com/claude-code), Python 3.10+ (stdlib only,
no pip installs needed for the core).

```bash
git clone https://github.com/17arhaan/CareerOPS.git
cd CareerOPS
claude          # launch Claude Code in the folder
```

Then, inside Claude Code:

```
/setup
```

Claude interviews you (who you are, what roles, which cities, your resume) and writes
every personal file: `profile/profile.md`, `preferences/job-search-preferences.md`,
`resume/current.md`, and a fresh tracker. All of them are **gitignored** — the repo
ships only `*.example` templates, so your personal data stays local even if you fork
and push.

Now run your first day:

```
/daily-packet        # 10 fresh roles, links verified, JDs checked, cover letters written
```

and open the app:

```bash
python3 scripts/serve_dashboard.py     # then open http://localhost:8787
```

(macOS: double-click `CareerOPS.command` in Finder to do both.)

## The daily loop

```
 morning                        during the day                    evening
┌─────────────────┐   ┌──────────────────────────────┐   ┌──────────────────────┐
│ /daily-packet   │   │ Apply from the Queue tab      │   │ /refresh-tracker     │
│ /status         │──▶│ (one-click "I applied" logs   │──▶│ (Gmail → pipeline)   │
│                 │   │ it), /cover-letter, /referral │   │ /dsa, /follow-up     │
└─────────────────┘   └──────────────────────────────┘   └──────────────────────┘
                    everything reads + writes tracker/state.json
```

## The app

`python3 scripts/serve_dashboard.py` serves a full local web app from
`tracker/state.json` — every action writes straight back to it. Tabs:

- **Overview** — goal countdown, hero stats, today's focus, pipeline, 30-day heatmap.
- **Queue** — today's packet with green YES / red NO "applyable" badges, apply links,
  one-click "I applied", per-company research links (LeetCode, Levels, Glassdoor,
  your school's alumni, recruiters).
- **Pipeline** — kanban across stages; change any card's stage inline.
- **Applications** — search, inline stage dropdowns, notes, interview-round logging,
  add/delete.
- **Analytics** — 14-day bar chart, source donut, pipeline funnel.
- **Network** — a tiny CRM for referral contacts (`/referral` finds them for you).
- **Prep** — per-company interview-prep quick links; pairs with `/interview-prep`,
  `/mock-interview`, `/dsa`.
- **Settings** — daily goal, target date, your name, school slug, theme.

It auto-refreshes every 30s and reflects anything the slash commands change.
`scripts/render_dashboard.py` also produces a static `dashboard/index.html` snapshot
for offline viewing.

### AI copilot (optional, in-app chatbot)

The floating 💬 button (or press `c`) opens a copilot powered by Claude via the
Anthropic API. It is grounded in your profile, resume, preferences, and live tracker,
and it takes real actions through tool use: *"I applied to Stripe SDE1"* logs it,
*"move Barclays to Interviewing"* moves it, *"write a cover letter for Datadog"*
writes one in your voice.

Enable it once:

```bash
pip install anthropic
cp .env.example .env       # paste your key from console.anthropic.com
python3 scripts/serve_dashboard.py
```

Until a key is set, the copilot replies with setup steps and the rest of the app works
normally.

## Slash commands

| Command | Does |
|---------|------|
| `/setup` | First-run interview; generates all your personal files. **Start here.** |
| `/daily-packet [date]` | Build the day's packet of verified roles + cover letters, update tracker. |
| `/status` | Morning briefing: pace vs goal, queue, follow-ups due, one action. |
| `/suggest-companies [filter]` | 10 fresh verified roles, no state change (browse mode). |
| `/cover-letter <company> [role] [JD url]` | Tailored cover letter in your voice. |
| `/cold-email <company> [role] [recipient]` | Cold email to a recruiter / hiring manager. |
| `/follow-up <company> [role]` | Follow-up email for a silent application. |
| `/referral <company> [role]` | Find alumni / employees + draft a referral ask. |
| `/log-application <company> <role> <location> <url> [date]` | Manually log an application. |
| `/set-stage <id> <stage>` | Move an application through the pipeline. |
| `/refresh-tracker` | Pull Gmail confirmations + status emails into the tracker. |
| `/weekly-digest` | Apps sent, response rate, follow-up candidates, pace check. |
| `/company-research <company>` | One-page company brief with hooks for your letters. |
| `/interview-prep <company>` | DSA + system design + behavioral brief for that company. |
| `/mock-interview <company> [round]` | Live mock interview (phone / dsa / systemdesign / behavioral). |
| `/dsa [topic]` | One daily practice problem, weighted by companies in your pipeline. |
| `/improve-resume [focus]` | Critique + revised resume version (never touches your original). |
| `/feedback approve\|reject <company> [reason]` | Teach the sourcer; auto-tunes the skip list. |

## How personalization works

```
profile/profile.md                    who you are, flagship stories, cover-letter
                                      rules, writing style        (gitignored)
preferences/job-search-preferences.md experience filter, cities, sources,
                                      skip list                   (gitignored)
resume/current.md                     your resume as markdown     (gitignored)
tracker/state.json                    applications + queue + settings (gitignored)
preferences/lessons.md                sourcing lessons, grows over time (committed)
```

Every command reads these files first — nothing about you is hardcoded. `/setup`
writes them; you can also edit them by hand any time (they are plain markdown) and the
whole system changes behavior instantly.

## More data sources (optional MCP servers)

Web search works out of the box. For higher-volume sourcing, `.mcp.json` declares two
local MCP servers that load when Claude Code starts in this folder:

```bash
scripts/setup-mcp.sh    # one-time: clones + builds JobSpy, prepares LinkedIn (uvx)
```

- **JobSpy** — scrapes LinkedIn + Indeed + Glassdoor + Naukri and more. Needs Docker.
- **LinkedIn** — alumni/referral discovery + jobs. One-time browser login.
  **Read-only use only** — never auto-message or auto-connect (account-ban risk).

If you use Claude on the web/desktop, the hosted **Gmail** and **Indeed** connectors
(Settings → Connectors) power `/refresh-tracker` and give `/daily-packet` durable
Indeed links with full JD access.

## Full automation (cron)

```bash
crontab scripts/crontab.example   # 6am packet, 7am Gmail refresh, Monday 9am digest
```

Each entry calls `scripts/run-claude.sh "/command"` headlessly (`claude -p`) and logs
to `logs/`. Wake up to a packet of verified roles with cover letters already written.
Note: headless runs may not have the hosted Gmail/Indeed connectors; the local
JobSpy/LinkedIn MCPs are the headless-safe sources.

## Utility scripts

```bash
python3 scripts/serve_dashboard.py           # the app (http://localhost:8787)
python3 scripts/render_dashboard.py          # rebuild the static dashboard snapshot
python3 scripts/verify_urls.py "<url>" ...   # gate job URLs (OK / REDIRECT / DEAD / CLOSED)
scripts/run-claude.sh "/daily-packet"        # run any slash command headlessly + log it
```

## Design principles

1. **One JSON file is the database.** `tracker/state.json` is human-readable,
   git-diffable (locally), and trivially portable. No DB, no cloud, no login.
2. **Verify before recommending.** A role enters your queue only with a live link and
   a JD that fits your filter, each carrying an explicit `applyable` verdict + reason.
3. **Your data stays yours.** Everything personal is gitignored; the AI copilot is the
   only network call with your data, direct to the Anthropic API with your own key.
4. **The human sends everything.** CareerOPS drafts; you review and hit send. It never
   auto-applies, auto-emails, or auto-messages anyone.

## FAQ

**Do I need to pay for anything?** Claude Code needs a Claude subscription or API
access. The core tool (sourcing, letters, tracker, prep) runs entirely inside Claude
Code. The in-app copilot additionally wants an Anthropic API key; skip it if you like.

**I'm not entry-level / not in India — does it work for me?** Yes. `/setup` builds the
filters around *your* experience bracket, cities, and region's job boards. The example
templates just show an entry-level search as a worked example.

**Is scraping LinkedIn safe?** The optional LinkedIn MCP logs into your real account;
use it read-only and sparingly. CareerOPS's instructions forbid auto-messaging. If in
doubt, don't run `setup-mcp.sh` — WebSearch sourcing works without it.

**Where do I look when something misbehaves?** `tracker/state.json` (the data),
`preferences/lessons.md` (what the sourcer has learned), and `logs/` (cron runs). And
just ask Claude Code in the repo — it knows this codebase.

## License

MIT — see [LICENSE](LICENSE).
