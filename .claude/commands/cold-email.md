---
description: Draft a cold email to a hiring manager or recruiter at a company.
argument-hint: "<company> [role] [recipient name/title]"
allowed-tools: Read, Write, WebFetch
---

Draft a cold email for `$ARGUMENTS`.

1. Read `profile/profile.md` and `resume/current.md`; if a JD URL is given,
   WebFetch it for specifics.
2. Write a tight cold email (110 to 150 words, honoring the profile's style
   rules): a specific subject line, a one-line hook tied to their product or
   stack, two sentences of concrete proof (one work story plus one project from
   the flagship stories), and a clear low-friction ask (15-minute chat or a
   pointer to the right person). Direct, peer-to-peer, no recruiter-bait.
   Sign per the profile, with phone and links.
3. Print it and save to `coverletters/coldemail-{company}-{today}.md`.
