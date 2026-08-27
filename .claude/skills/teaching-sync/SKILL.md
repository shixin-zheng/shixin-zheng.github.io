---
name: teaching-sync
description: Pull teaching updates from ~/teaching into the website and publish them. Use when the user asks to sync/update the teaching pages, refresh lecture notes, update the course schedule, or says the notes/schedule changed. Also the routine to follow for the weekly in-semester update.
---

# Sync the teaching section

The website's teaching pages are downstream of `~/teaching`, which a different agent
maintains. This skill refreshes the website from it. **Never write to `~/teaching`** — read
from it, build into this repo.

## 1. See what moved

```bash
./teaching-src/sync.py
```

It compares every watched source against `teaching-src/sources.lock.json` and prints the
group each change belongs to. "teaching sources unchanged — nothing to do" means stop.

Fall 2026 is the exception: it publishes each lecture's topic only after that class, so
its schedule goes stale with the calendar, not with the sources. When nothing has moved
the script says so and rebuilds that course anyway — running a sync after a class is what
puts the lecture's title, reading and handwritten scan on the page.

## 2. Rebuild

```bash
./teaching-src/sync.py --apply
```

Mechanical rebuilds, safe to run unattended:

| changed source | what gets rebuilt |
| --- | --- |
| `syllabus/<term>/schedule.csv` | the course YAML under `_data/courses/` — this is the calendar the instructor edits |
| `lectures/typed/**.tex`, `.sty` | the 26 per-lecture PDFs and the combined volume in `files/stat400/notes/`, plus the titles and readings the CSV leaves blank |
| `lectures/<term>/pdf/Week*-Lec*.pdf` | the handwritten scans under `files/stat400/<term>/handwritten/` — the PDF the Fall 2026 schedule links per lecture |

The schedule CSV format is specified in `teaching-src/schedule-format.md`. Until a term has
one in the teaching library, the website uses its own copy in `teaching-src/schedules/`;
edits made there are a stopgap, and the teaching library's file wins as soon as it appears.

## 3. Handle what the script cannot

Anything the script only *reports* needs a human read before it goes live:

- **A syllabus PDF changed or appeared.** Read it (`pdftotext -layout`) and update the
  course facts in `teaching-src/courses.json` — meeting time, room, sections, discussion
  day, office hours, TAs — and fold any exam-date changes into the schedule CSV. Once the
  real syllabus lands, drop `tentative: true`.
- **A new term directory appeared** (e.g. `syllabus/2027-spring/`). That is a new course
  page: add an entry to `teaching-src/courses.json` and a `_teaching/<term>-<course>.md`
  stub, and flip the finished term's `status` from `current` to `past`.
- **A new course** under `~/teaching/courses/`. Same pattern; `_data/courses/*.yml` is the
  contract, `_includes/course-schedule.html` renders whatever it finds.

The Fall 2026 schedule is drafted, not confirmed — the dates for midterms, homework and
quizzes were inferred from the Fall 2025 rhythm. Treat any real syllabus as authoritative
over it. Its meeting time, room, section numbers, discussion times and TA come from the
Testudo listing the instructor sent on 2026-08-27 and are confirmed; office hours are not
set yet.

## 4. Publish

```bash
./teaching-src/sync.py --apply --push
```

Pushing to `master` deploys through GitHub Actions in about a minute. Verify before
reporting done:

```bash
gh run list --repo shixin-zheng/shixin-zheng.github.io --limit 1
curl -s -o /dev/null -w '%{http_code}\n' https://shixin-zheng.github.io/teaching/2026-fall-stat400/
```

## Reporting back

Say what changed at the source, what was rebuilt, and what still needs the user's
judgment. If a lecture's notes changed, name the lecture — the user is mid-revision and
wants to know which one landed.
