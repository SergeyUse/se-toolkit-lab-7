---
name: get-meeting-report
description: Generate a meeting report for a given lab and iteration
argument-hint: "<lab-number> <iteration-number>"
---

Generate a meeting report for lab N, iteration M.

## Steps

1. Parse `$ARGUMENTS` to extract N (lab number) and M (iteration number). Both are required — if missing, ask the user.
2. Read `instructors/context/conventions/meeting-report.md` for the report format and rules.
3. Read `instructors/meetings/week-N/meeting-M/transcripts/transcript-by-speaker.txt` (substituting actual N and M).
4. Following the rules and structure from the prompt file, write the meeting report to `instructors/meetings/week-N/meeting-M/meeting-report.md`. The report must use the exact section headings from the prompt and follow the subsection structure shown in the example: each distinct item (decision, open question, action point, etc.) must be a numbered Markdown subsection heading with prose beneath it — not a bullet list or bold label. For example:

   ```markdown
   ### 1. Use PostgreSQL for the primary data store

   **Consensus: unanimous.**
   Speaker A proposed PostgreSQL, citing its JSON support for flexible schemas...
   ```
5. Do NOT summarize, analyze, or comment on the report contents. Just confirm the file was written.
