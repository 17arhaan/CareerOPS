---
description: Run a mock interview (phone screen or technical) as the interviewer.
argument-hint: "<company> [round: phone|dsa|systemdesign|behavioral]"
allowed-tools: Read, WebSearch, WebFetch
---

Run a mock interview for the company in `$ARGUMENTS`. Default round is a phone
screen.

1. Read `profile/profile.md` and `resume/current.md`. If useful, quickly check
   the company's typical interview style (WebSearch).
2. Act as the interviewer for that company and round. Ask ONE question at a
   time and wait for the user's answer before continuing. Stay in role.
   - phone: background, a couple of resume deep-dives, one easy-medium coding prompt.
   - dsa: 1 to 2 LeetCode-style problems at the company's typical difficulty;
     ask for approach before code; probe complexity.
   - systemdesign: one design prompt suited to their stack; drive through
     requirements, API, data model, scale, tradeoffs.
   - behavioral: STAR-style questions; pressure-test ownership and conflict stories.
3. After each answer give brief, honest feedback (what landed, what to tighten)
   then the next question. At the end give a short overall rating and the top 3
   things to improve. Honor the profile's style rules in everything you write.
