---
description: Draft a follow-up email for an application that has gone silent.
argument-hint: "<company> [role]"
allowed-tools: Read, Write
---

Draft a follow-up email for the company/role in `$ARGUMENTS`.

1. Read `tracker/state.json` to find the application (company, role,
   applied_date, stage), plus `profile/profile.md` and `resume/current.md`
   for context.
2. Write a short, polite follow-up (90 to 130 words, honoring the profile's
   style rules): reference the specific role and roughly when the user applied,
   restate one concrete reason they fit (tie a flagship story to the company's
   work), and ask about next steps or timeline. No groveling, no recruiter-bait
   words. Sign per the profile.
3. If the application is less than 7 days old, say so and suggest waiting
   unless there is a reason to reach out now.
4. Print the email and save it to `coverletters/followup-{company}-{today}.md`.
