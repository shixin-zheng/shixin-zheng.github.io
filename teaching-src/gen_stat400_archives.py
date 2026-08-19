"""Emit the two archive course data files.

Spring 2026 comes from the as-taught snapshot
  ~/teaching/courses/STAT400/syllabus/2026-spring/schedule-as-taught.csv
which the teaching library flags as authoritative over the syllabus PDF.

Fall 2025 is transcribed from the syllabus PDF's tentative schedule, with the one
known deviation (HW7) recorded in a note.
"""
import csv
import datetime as dt
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parent.parent / "_data/courses"
REPO.mkdir(parents=True, exist_ok=True)


def esc(s):
    return '"' + s.replace('\\', '').replace('"', '\\"').strip() + '"'


def week_span(first_iso):
    d = dt.date.fromisoformat(first_iso)
    mon = d - dt.timedelta(days=d.weekday())
    return f"{mon.strftime('%b %-d')} – {(mon + dt.timedelta(days=6)).strftime('%b %-d')}"


def emit(header_lines, weeks, path):
    out = list(header_lines)
    out.append("schedule:")
    for week, meetings, hw, quiz in weeks:
        out.append(f"  - week: {week}")
        out.append(f"    span: {esc(week_span(meetings[0][0]))}")
        out.append("    meetings:")
        for date, kind, num, title in meetings:
            d = dt.date.fromisoformat(date)
            out.append(f"      - date: {date}")
            out.append(f"        day: {d.strftime('%a')}")
            out.append(f"        kind: {kind}")
            if num:
                out.append(f"        lecture: {num}")
            out.append(f"        title: {esc(title)}")
        if hw:
            out.append("    hw:")
            out.append(f"      id: {hw[0]}")
            out.append(f"      posted: {hw[1]}")
            out.append(f"      due: {hw[2]}")
            if len(hw) > 3 and hw[3]:
                out.append(f"      note: {esc(hw[3])}")
        if quiz:
            out.append(f"    quiz: {esc(quiz)}")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {path.name}: {len(weeks)} weeks")


# ----------------------------------------------------------------- Spring 2026
CSV = pathlib.Path.home() / "teaching/courses/STAT400/syllabus/2026-spring/schedule-as-taught.csv"
rows = list(csv.reader(CSV.open(encoding="utf-8")))[1:]

weeks, cur = [], None
for r in rows:
    if not any(c.strip() for c in r):
        continue
    wk, date, lec, topic, hw, posted, due, quiz = (r + [""] * 8)[:8]
    date = "2026-" + date.strip().replace("/", "-")
    topic = re.sub(r"\s+", " ", topic).strip().rstrip(",")
    # Spelling slips in the source spreadsheet; the page is student-facing.
    for wrong, right in [("Betrand", "Bertrand"), ("Mordern", "Modern"),
                         ("funtions", "functions"), ("corelation", "correlation"),
                         ("statisctics", "statistics"), ("Possion", "Poisson"),
                         ("rv", "RV"), ("RVs", "RVs")]:
        topic = re.sub(rf"\b{wrong}\b", right, topic)
    lec = lec.strip()

    if topic.upper() in ("NA", "NO CLASS"):
        kind, num, title = "holiday", None, "No class"
    elif topic.lower().startswith("final exam"):
        kind, num, title = "final", None, "Final Exam · 10:30 am – 12:30 pm"
    elif re.match(r"midterm \d", topic, re.I):
        kind, num, title = "exam", None, topic
    elif lec.isdigit():
        kind, num, title = "lecture", int(lec), topic
    else:
        kind, num, title = "review", None, topic

    if wk.strip():
        hwv = None
        if hw.strip() and hw.strip() != "No HW":
            hwv = (hw.strip(), "2026-" + posted.strip().replace("/", "-"),
                   "2026-" + due.strip().replace("/", "-"))
        qv = quiz.strip() if quiz.strip() and quiz.strip() != "No Quiz" else None
        cur = (int(wk), [], hwv, qv)
        weeks.append(cur)
    cur[1].append((date, kind, num, title))

emit([
    "# STAT 400 / DATA 400 — Spring 2026 (archive)",
    "#",
    "# Transcribed from the as-taught schedule snapshot kept in the teaching library",
    "# (syllabus/2026-spring/schedule-as-taught.csv). That table records what was actually",
    "# covered and supersedes the plan in the syllabus PDF.",
    "",
    "code: STAT 400 / DATA 400",
    "name: Applied Probability and Statistics I",
    "term: Spring 2026",
    "status: past",
    "institution: University of Maryland",
    "instructor: Shixin Zheng",
    "meetings: TuTh 2:00–3:15 pm, ARM 0126",
    "sections: 411/412/421/422/431/432",
    "discussion: Wednesdays",
    "ta: Scott Fullenbaum, Minghan Yu",
    "lectures_taught: 24",
    "textbook: >-",
    "  Lecture notes by J. F. Fernandes and M. D. Gunatilleka; reference text",
    "  Devore, <em>Probability and Statistics for Engineering and the Sciences</em>, 9th ed.",
    "",
], weeks, REPO / "stat400-2026-spring.yml")


# ------------------------------------------------------------------- Fall 2025
L = "lecture"
f25 = [
    (1, [("2025-09-02", L, 1, "Introduction to Probability and Statistics, with examples"),
         ("2025-09-04", L, 2, "Basic set theory, experiments and events")], None, None),
    (2, [("2025-09-09", L, 3, "Probability functions, probability space"),
         ("2025-09-11", L, 4, "Combinatorics, counting and probability")],
     ("HW1", "2025-09-12", "2025-09-19"), "Quiz 1"),
    (3, [("2025-09-16", L, 5, "Conditional probability, independence, Bayes' theorem"),
         ("2025-09-18", L, 6, "Random variables")],
     ("HW2", "2025-09-19", "2025-09-26"), "Quiz 2"),
    (4, [("2025-09-23", L, 7, "Cumulative distribution function; discrete and continuous RVs"),
         ("2025-09-25", L, 8, "Parameters of RVs: expected value, variance, standard deviation")],
     ("HW3", "2025-09-26", "2025-10-03"), "Quiz 3"),
    (5, [("2025-09-30", L, 9, "Discrete families: uniform, Bernoulli, binomial, hypergeometric, negative binomial, geometric, Poisson"),
         ("2025-10-02", L, 10, "Continuous families: uniform, normal, gamma, exponential, chi-square, beta")],
     ("HW4", "2025-10-03", "2025-10-10"), "Quiz 4"),
    (6, [("2025-10-07", "review", 11, "Review for Midterm 1"),
         ("2025-10-09", "exam", None, "Midterm 1")], None, None),
    (7, [("2025-10-14", "holiday", None, "No class — Fall Break"),
         ("2025-10-16", L, 12, "Joint distributions: joint pmf/pdf, marginals, conditionals")],
     ("HW5", "2025-10-17", "2025-10-24"), "Quiz 5"),
    (8, [("2025-10-21", L, 13, "Joint distributions, continued"),
         ("2025-10-23", L, 14, "Joint distributions: expected values, covariance, correlation, linear models")],
     ("HW6", "2025-10-24", "2025-10-31"), "Quiz 6"),
    (9, [("2025-10-28", L, 15, "Correlation and linear models"),
         ("2025-10-30", L, 16, "Random samples, linear combinations of RVs, statistics and their sampling distributions")],
     ("HW7", "2025-10-31", "2025-11-14", "Syllabus listed 11/07; the deadline was moved to 11/14."), "Quiz 7"),
    (10, [("2025-11-04", "review", 17, "Review for Midterm 2"),
          ("2025-11-06", "exam", None, "Midterm 2")], None, None),
    (11, [("2025-11-11", L, 18, "Central limit theorem and applications"),
          ("2025-11-13", L, 19, "Point estimation: variance and bias of estimators")],
     ("HW8", "2025-11-14", "2025-11-21"), "Quiz 8"),
    (12, [("2025-11-18", L, 20, "Estimators, continued"),
          ("2025-11-20", L, 21, "Examples of estimators and their properties")],
     ("HW9", "2025-11-21", "2025-11-26"), "Quiz 9"),
    (13, [("2025-11-25", L, 22, "Point estimation, continued"),
          ("2025-11-27", "holiday", None, "No class — Thanksgiving")], None, None),
    (14, [("2025-12-02", L, 23, "Point estimators"),
          ("2025-12-04", L, 24, "Method of moments")],
     ("HW10", "2025-12-05", "2025-12-12"), "Quiz 10"),
    (15, [("2025-12-09", L, 25, "Maximum likelihood estimation"),
          ("2025-12-11", "review", 26, "Review for the final exam")], None, None),
]

emit([
    "# STAT 400 / DATA 400 — Fall 2025 (archive)",
    "#",
    "# Transcribed from the course syllabus (syllabus/2025-fall/). The syllabus table is a",
    "# plan rather than an as-taught record; the one deviation the teaching library documents",
    "# (HW7 moved from 11/07 to 11/14) is noted on that week.",
    "",
    "code: STAT 400 / DATA 400",
    "name: Applied Probability and Statistics I",
    "term: Fall 2025",
    "status: past",
    "institution: University of Maryland",
    "instructor: Shixin Zheng",
    "meetings: TuTh 2:00–3:15 pm, ARM 0126",
    "sections: 511/512/521/522/531/532",
    "discussion: Mondays, MTH 0106",
    "ta: Christian Adams, Minghan Yu",
    "lectures_taught: 26",
    "textbook: >-",
    "  Lecture notes by J. F. Fernandes and M. D. Gunatilleka; reference text",
    "  Devore, <em>Probability and Statistics for Engineering and the Sciences</em>, 9th ed.",
    "",
], f25, REPO / "stat400-2025-fall.yml")
