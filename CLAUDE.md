# Academic website — maintenance notes

Personal academic site of Shixin Zheng (郑仕欣), Postdoctoral Associate, Department of
Mathematics, University of Maryland, College Park.

- Live: <https://shixin-zheng.github.io>
- Repo: `shixin-zheng/shixin-zheng.github.io` (branch `master`)
- Engine: Jekyll (academicpages template), deployed by `.github/workflows/jekyll.yml`
  on every push to `master`. Nothing to build or deploy by hand.

## Source of truth

Content comes from `~/research`, **not** from memory or the web:

| Site content | Authoritative source |
| --- | --- |
| The CV PDF at `/files/CV_Shixin_Zheng.pdf` | `cv-src/CV_Shixin_Zheng.tex` **in this repo** — edit it, then run `./cv-src/build.sh` (needs `tectonic`) |
| CV facts (education, appointments, publications, funding, service, honors, talks) | `~/research/NIW/CV/CV_Shixin_Zheng_NIW.tex` — the longest CV variant; **read-only from here** (see below) |
| Older CV variant | `~/research/AMSTravelFund/CV_Shixin_Zheng.tex` |
| Paper titles, abstracts, arXiv numbers | the project's `overleaf/` directory under `~/research/<project>/` |
| Ongoing / unpublished work | `~/research/<project>/{topics,wiki,meetings}` — treat as private until it is on arXiv |

Active project directories follow the layout `ideas/ meetings/ overleaf/ topics/ wiki/
workspace/` (e.g. `Riemannian-GPE`, `bm-stratified-opt`, `curse-of-dim`, `imuon-prior`,
`imuon-followup`, `Daytrader-RL`). Numbered `projectN(...)` directories are older work.

**Never invent a publication, talk, award, or service item.** If it is not in the CV tex or
in a paper under `~/research`, ask before putting it on the site.

**`~/research/NIW/` is off limits for writes.** It holds the user's NIW petition materials
and is maintained by a different agent, which decides for itself what belongs in that CV
based on what helps the petition. Read from it, never edit it. An item present on the
website but absent from the NIW CV (e.g. the Numerical Analysis Seminar co-organizer role)
is an intentional editorial difference, not a gap to close — do not "sync" the two.

## Teaching: downstream of `~/teaching`

The teaching section is generated, not hand-written. `~/teaching` is the raw material —
a separate library with its own agent — and, like `~/research/NIW/`, it is **read-only from
here**. Lecture notes are revised through the semester, so the website has to follow it:

```
./teaching-src/sync.py                  # what changed at the source?
./teaching-src/sync.py --apply          # rebuild whatever those sources feed
./teaching-src/sync.py --apply --push   # ... and publish
```

The `/teaching-sync` skill (`.claude/skills/teaching-sync/`) is the full routine, including
the cases the script deliberately leaves to a human (a changed syllabus, a new term, a new
course). Syncs are **run on request, not on a timer** — the user revises notes in place and
does not want a background job publishing drafts. `teaching-src/com.shixin.teaching-sync.plist`
would run the same script daily via launchd; it is deliberately **not installed**.

| piece | role |
| --- | --- |
| `~/teaching/courses/<C>/syllabus/<term>/schedule.csv` | **the calendar the instructor edits.** Format: `teaching-src/schedule-format.md`. Wins over anything in this repo |
| `teaching-src/schedules/*.csv` | this repo's copy of the same table, used only until the teaching library has one for that term |
| `teaching-src/courses.json` | per-term facts (meeting time, room, sections, TAs, ELMS…) — they change once a semester, so they live here rather than in the CSV |
| `_data/courses/*.yml` | one file per course-semester, consumed by the templates. Generated — never hand-edit |
| `teaching-src/gen_courses.py` | CSV + courses.json + typed notes → those YAMLs |
| `teaching-src/build-stat400-notes.sh` | 26 per-lecture PDFs + combined volume → `files/stat400/notes/` |
| `teaching-src/copy-handwritten.py` | the instructor's handwritten scans → `files/stat400/<term>/handwritten/`, which is what the Fall 2026 schedule links |
| `_includes/course-schedule.html` | renders any course YAML; the progress/today/due-soon logic is client-side JS so it stays right between builds |
| `_layouts/course.html`, `_sass/layout/_course.scss` | page shell and styling |
| `_teaching/<term>-<course>.md` | thin stub: `layout: course` + `course:` key into `_data/courses/` |

A schedule row's `topic` may be left blank: it is then filled from the typed notes'
`\lecture{n}{title}{sections}`, so revising a lecture title in `~/teaching` updates the
published schedule too. That fallback is gated per course by `notes_numbering` in
`courses.json` — only Fall 2026 follows the notes' own lecture numbering.

**Devore section numbers are never published** — not in a schedule row, not in a note. The
typed notes' sections drifted out of step with what is actually taught, and a stale reading
beside a correct topic is worse than none; the CSV's `reading` column is read and dropped.
The textbook line naming the book itself is fine.

**Fall 2026 publishes each lecture as it is taught** (`topics_as_taught: true` in that
course's `meta`). A class still to come shows its number and "posted after class" —
no title, no reading — however full the CSV and the typed notes are; exams, breaks and
review sessions are still announced ahead. The per-lecture PDF in that column is the
instructor's **handwritten** scan, published by `copy-handwritten.py` once it lands in
`~/teaching/courses/STAT400/lectures/2026-fall/pdf/`; the typed per-lecture PDFs are not
linked (`link_notes: false`), only the combined typed volume above the table. This makes
the generated YAML depend on the day it was built, so `sync.py --apply` regenerates that
course even when no source moved, and `SCHEDULE_TODAY=YYYY-MM-DD` reproduces any day.

**The schedule of the course in session is live, not a draft.** The CSV in `~/teaching` is
the calendar as actually taught, and publishing it is the reason the user keeps this site
at all — a sync that is late is a page that is wrong. The syllabus on ELMS is the
*tentative* version and does not override it; the page says so. Never re-add
`tentative: true` to a running term (the flag still works, for a term whose dates really
are drafted). `~/teaching/WEBSITE-REQUEST.md` is the standing request to that library's
agent to own the schedule CSV; it is the only file this repo has ever written there.

Exams, solutions and homework PDFs are deliberately **not** published — only the schedule,
topics and lecture notes.

## Layout

- `_pages/about.md` — homepage; also carries the full publication list by hand.
- `_pages/cv.md` — CV page; links to `files/CV_Shixin_Zheng.pdf`.
- `_publications/YYYY-MM-DD-slug.md` — one file per paper. `category:` must be one of the
  keys under `publication_category` in `_config.yml` (`manuscripts`, `preprints`,
  `conferences`, `books`); a category not listed there silently disappears from
  `/publications/`.
- `_pages/teaching.html` — course index, built from the `_teaching` collection.
- `_talks/` — one file per talk.
- `_config.yml` — identity, social links, collection settings.

Adding a paper means touching **both** `_publications/` and the list in `_pages/about.md`,
and usually `files/CV_Shixin_Zheng.pdf`.

## Conventions

- American English throughout (see the user's global preferences).
- Author name is bolded as `**S. Zheng**` in the about-page publication list.
- Publications carry DOI/journal links when published, arXiv links always.
- The public CV (`cv-src/CV_Shixin_Zheng.tex`) is deliberately shorter than the NIW CV in
  `~/research`: it omits research funding, citation metrics, the dissertation entry, and
  technical skills. Keep the facts consistent between the two, not the section lists.
  Originally authored as `~/Jobs/02-resume/cv-academic.tex`; this repo is now the master
  copy for the *website* CV.
- `author.github` in `_config.yml` points to **ZhengShixin**, the user's main GitHub
  account. `shixin-zheng` is a secondary account that exists only to host this site — do
  not "correct" the profile link to it.

## Local preview

The system Ruby (2.6) has no Jekyll installed, so there is no working local preview yet.
Either `bundle install` with a newer Ruby, or use `docker-compose up` (see `Dockerfile`),
before promising a rendered check.
