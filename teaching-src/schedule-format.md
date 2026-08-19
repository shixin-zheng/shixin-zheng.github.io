# Course schedule CSV — the format the website reads

One CSV per course-semester, one row per class meeting. This file is the contract between
the teaching library (`~/teaching`, where the file is edited) and the website (which turns
it into the published schedule table).

**Where it goes**

```
~/teaching/courses/<COURSE>/syllabus/<term>/schedule.csv
```

e.g. `~/teaching/courses/STAT400/syllabus/2026-fall/schedule.csv`. When that file exists it
wins; until it does, the website falls back to its own copy in
`teaching-src/schedules/<course>-<term>.csv`, which is the same format and can be used as a
starting point.

**Columns** — the header row must be exactly:

```
week,date,kind,lecture,topic,reading,hw,hw_posted,hw_due,quiz,note
```

| column | required | meaning |
| --- | --- | --- |
| `week` | yes | semester week number. Consecutive rows sharing a number form one week block in the table |
| `date` | yes | `YYYY-MM-DD`, the day of that meeting |
| `kind` | yes | one of `lecture`, `review`, `exam`, `final`, `holiday` |
| `lecture` | for lectures | lecture number. Also picks the notes PDF (`lec07.pdf` for `7`) |
| `topic` | no | lecture title. Blank → taken from the typed notes for that lecture number |
| `reading` | no | Devore sections, e.g. `3.5–3.6`. Blank → taken from the typed notes. Do not write the word "Devore" |
| `hw` | no | assignment name, e.g. `HW3`. Put it on any one row of the week; it renders once for the whole week |
| `hw_posted` | no | `YYYY-MM-DD` |
| `hw_due` | no | `YYYY-MM-DD`. Drives the "due in N days" flag on the live page |
| `quiz` | no | free text, e.g. `Quiz 4 · in discussion` |
| `note` | no | a short caveat shown under the homework, e.g. a moved deadline |

**Rules**

- Every meeting gets a row, including breaks: `7,2026-10-13,holiday,,Fall Break — no class,,,,,,`
- Rows must be in chronological order; the table renders them as given.
- Exams: `kind=exam`, leave `lecture` blank, put the name in `topic` (`Midterm 1`).
  The final exam is `kind=final`.
- A review class is `kind=review`, not `exam` — reviews count as lectures in the progress
  bar, exams do not.
- The topic/reading fallback only applies where the course follows the typed notes' own
  lecture numbering (currently Fall 2026 only; the flag is `notes_numbering` in
  `teaching-src/courses.json`). For any other term, write topics out in the CSV.
- Dates are the only thing the live page needs to compute progress. Editing a date moves
  the "current week" highlight; no other change is required.

**What is *not* in this file**

Course facts — meeting time, room, section numbers, discussion day, office hours, TAs,
textbook, ELMS link, semester start/end — live on the website side in
`teaching-src/courses.json`, since they change once a semester rather than weekly. Tell the
website maintainer when they change, or edit that file directly.

**Example**

```csv
week,date,kind,lecture,topic,reading,hw,hw_posted,hw_due,quiz,note
1,2026-09-01,lecture,1,,,,,,,
1,2026-09-03,lecture,2,,,,,,,
2,2026-09-08,lecture,3,,,HW1,2026-09-11,2026-09-18,Quiz 1 · in discussion,
2,2026-09-10,lecture,4,,,,,,,
6,2026-10-06,review,11,Review for Midterm 1,Ch. 2–3.5,,,,,
6,2026-10-08,exam,,Midterm 1,,,,,,
7,2026-10-13,holiday,,Fall Break — no class,,,,,,
```

Rows 1–4 leave `topic` and `reading` blank on purpose: the website fills them from the
typed lecture notes, so revising a lecture title in the notes updates the schedule too.

**Publishing**

After editing, the website side runs:

```bash
./teaching-src/sync.py --apply --push
```

which regenerates `_data/courses/*.yml`, rebuilds any lecture-note PDFs whose source
changed, commits and pushes. GitHub Pages redeploys in about a minute.

**Validation** — the generator refuses a CSV whose dates do not increase down the file, or
whose week numbers go backwards, naming the offending line. Reorder the rows rather than
working around it.
