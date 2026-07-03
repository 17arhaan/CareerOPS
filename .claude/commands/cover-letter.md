---
description: Generate a tailored cover letter for a company/role.
argument-hint: "<company> [role] [JD URL or pasted text]"
allowed-tools: Read, Write, WebFetch
---

Generate a tailored cover letter.

Arguments: `$ARGUMENTS` — first token is the company, optional role next,
optional JD URL or pasted text after that.

1. Read `profile/profile.md` (cover letter rules + flagship stories) and
   `resume/current.md`.
2. If a JD URL is given, WebFetch it to pull the real stack, team, and product
   so the letter references specifics rather than generic praise.
3. Write the letter following the profile's rules: length, opening line, one
   work story plus one personal project from the flagship stories (paraphrased,
   not copied), the style rules (punctuation, banned words), and the exact
   signature.
4. Save to `coverletters/{company}-{role}-{today}.md` (slugify, role optional)
   and print the letter to stdout.
