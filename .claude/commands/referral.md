---
description: Find alumni / employees at a company and draft a referral ask.
argument-hint: "<company> [role]"
allowed-tools: Read, Write, WebSearch, WebFetch
---

Find a referral path into the company in `$ARGUMENTS`.

1. Read `profile/profile.md` for the user's school (alumni search) and
   flagship stories.
2. If the LinkedIn MCP is connected this session, use `search_people` /
   `get_company_employees` (READ ONLY, do not send connections or messages) to
   find people at the company, prioritizing alumni of the user's school, then
   recruiters. If it is not connected, say so and fall back to WebSearch for
   "{company} {school} alumni LinkedIn" and the company's LinkedIn people page,
   and point the user at the Alumni/Recruiters links on the dashboard.
3. List up to 5 contacts: name, title, why relevant (alumni / team match / recruiter).
4. Draft one short, specific outreach message (under 90 words, honoring the
   profile's style rules) the user can send manually: who they are, the role,
   one concrete reason they fit, a soft ask for a referral or a quick chat.
   Never auto-send. Sign per the profile.
5. Save to `notes/referral-{company}-{today}.md` and print. Suggest logging
   promising contacts in the dashboard's Network tab.
