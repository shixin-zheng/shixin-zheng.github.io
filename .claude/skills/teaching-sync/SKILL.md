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
group each change belongs to. "teaching sources unchanged" means stop — there is nothing
to publish.

## 2. Rebuild

```bash
./teaching-src/sync.py --apply
```

Mechanical rebuilds, safe to run unattended:

| changed source | what gets rebuilt |
| --- | --- |
| `lectures/typed/**.tex`, `.sty` | the 26 per-lecture PDFs and the combined volume in `files/stat400/notes/`, then the Fall 2026 lecture titles |
| `syllabus/<term>/schedule-as-taught.csv` | the course YAML under `_data/courses/` |

## 3. Handle what the script cannot

Anything the script only *reports* needs a human read before it goes live:

- **A syllabus PDF changed or appeared.** Read it (`pdftotext -layout`) and update the
  facts at the top of `teaching-src/gen_stat400_fall2026.py` — meeting time, room,
  sections, discussion day, office hours, TAs — plus the exam dates in the schedule
  skeleton. Then rerun the generator. Once the real syllabus lands, drop `tentative: true`.
- **A new term directory appeared** (e.g. `syllabus/2027-spring/`). That is a new course
  page: add a generator, a data file, and a `_teaching/<term>-<course>.md` stub, and flip
  the finished term's `status:` from `current` to `past`.
- **A new course** under `~/teaching/courses/`. Same pattern; `_data/courses/*.yml` is the
  contract, `_includes/course-schedule.html` renders whatever it finds.

The Fall 2026 schedule is drafted, not confirmed — the dates for midterms, homework and
quizzes were inferred from the Fall 2025 rhythm. Treat any real syllabus as authoritative
over it.

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
