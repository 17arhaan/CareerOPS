---
description: Critique the resume and write a revised version.
argument-hint: "[focus area, optional]"
allowed-tools: Read, Write, Bash
---

Review and improve the user's resume.

1. Read `resume/current.md` and `profile/profile.md` (target roles + style
   rules). Optional focus: `$ARGUMENTS`.
2. Give a concise critique (bullets, no fluff) covering impact wording,
   quantification, ordering, tailoring to the profile's target roles, and
   anything ATS-unfriendly (tables, images, unusual headings, missing
   keywords from typical JDs at their level).
3. Write the revised resume to `resume/versions/v{N}.md` where N is the next
   integer after the highest existing `v*.md` (use `ls resume/versions/`).
   Honor the profile's style rules.
4. Print the critique to stdout and state which version file you wrote. Do not
   overwrite `resume/current.md`; the user promotes a version manually when
   they like it.
