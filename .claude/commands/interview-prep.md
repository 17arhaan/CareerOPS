---
description: Build an interview prep brief for a company.
argument-hint: "<company>"
allowed-tools: Read, Write, WebSearch, WebFetch, Bash
---

Build an interview brief for the company in `$ARGUMENTS`.

1. Read `profile/profile.md` (experience level, region, flagship stories).
2. Pull company-specific LeetCode questions from
   `https://github.com/snehasishroy/leetcode-companywise-interview-questions/tree/master/{slug}`
   via WebFetch (try common slug forms). If unavailable, use WebSearch for
   "{company} interview questions {experience level} {region}".
3. Build a brief covering: the company's interview process / rounds at the
   user's level and region, top DSA topics + 10 representative problems, one
   system-design prompt appropriate to their stack, behavioral themes, and how
   the user's flagship stories map to the company's domain.
4. Save to `notes/interview-{slug}-{today}.md` and print the brief.
