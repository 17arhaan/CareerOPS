---
description: Today's DSA practice problem, weighted by companies in the queue/pipeline.
argument-hint: "[topic, optional]"
allowed-tools: Read, WebSearch, WebFetch
---

Give the user one DSA problem to do today.

1. Read `tracker/state.json` for companies in the current queue and active pipeline.
2. Pick one problem likely asked by those companies (use the company tags on
   LeetCode, e.g. `https://leetcode.com/company/{slug}/`, or WebSearch
   "{company} leetcode questions"). Honor an optional `$ARGUMENTS` topic.
   Prefer medium difficulty; rotate topics day to day.
3. Present: problem name + link, the company it maps to, difficulty, a one-line
   "what it tests", and a small hint behind a "try first" note. Do not dump the
   full solution unless asked. Offer to review the user's solution or turn it
   into a /mock-interview dsa round.
