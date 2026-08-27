#!/usr/bin/env python3
"""Build _data/courses/*.yml from editable schedule CSVs.

One CSV per course-semester, one row per class meeting, in the format documented in
teaching-src/schedule-format.md. For each course registered in teaching-src/courses.json
the CSV is looked up in two places, in order:

  1. ~/teaching/<source_csv>          — the teaching library's copy, if it exists.
     This is the one the instructor edits during the semester; it always wins.
  2. teaching-src/schedules/<csv>     — the copy kept in this repo, used until the
     teaching library has one.

Blank topic / reading cells for a numbered lecture are filled from the typed lecture
notes, so the CSV only has to carry the calendar.

A course whose meta carries `topics_as_taught` publishes a lecture's topic and reading
only once that class has been taught; until then the row shows the lecture number alone.
Its output therefore depends on the day it is generated — SCHEDULE_TODAY overrides that.

    ./teaching-src/gen_courses.py            # rebuild every course
    ./teaching-src/gen_courses.py stat400-2026-fall
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import os
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
HERE = REPO / "teaching-src"
TEACHING = pathlib.Path(os.environ.get("TEACHING_ROOT", pathlib.Path.home() / "teaching"))
TYPED = TEACHING / "courses/STAT400/lectures/typed/lectures"
OUT = REPO / "_data/courses"

KINDS = {"lecture", "review", "exam", "final", "holiday"}


def today() -> dt.date:
    """Today, or SCHEDULE_TODAY — a course may publish topics only as it teaches them,
    which makes the output depend on the day it was generated."""
    override = os.environ.get("SCHEDULE_TODAY")
    return dt.date.fromisoformat(override) if override else dt.date.today()


def typed_lectures() -> dict[int, tuple[str, str]]:
    """lecture number -> (title, Devore sections), read from the typed notes."""
    found = {}
    for tex in sorted(TYPED.glob("lec*.tex")):
        m = re.search(r"\\lecture\{(\d+)\}\{(.+?)\}\{(.+?)\}", tex.read_text(encoding="utf-8")[:400], re.S)
        if m:
            found[int(m.group(1))] = (m.group(2), m.group(3).replace("\\ ", " ").replace("--", "\u2013"))
    return found


def q(s: str) -> str:
    return '"' + str(s).replace("\\", "").replace('"', '\\"').strip() + '"'


def week_span(first: dt.date) -> str:
    mon = first - dt.timedelta(days=first.weekday())
    return f"{mon.strftime('%b %-d')} \u2013 {(mon + dt.timedelta(days=6)).strftime('%b %-d')}"


def read_rows(path: pathlib.Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if (r.get("date") or "").strip()]
    for i, r in enumerate(rows, 2):
        for k, v in list(r.items()):
            r[k] = (v or "").strip()
        try:
            dt.date.fromisoformat(r["date"])
        except ValueError:
            raise SystemExit(f"{path}:{i}: date must be YYYY-MM-DD, got {r['date']!r}")
        if r["kind"] not in KINDS:
            raise SystemExit(f"{path}:{i}: kind must be one of {sorted(KINDS)}, got {r['kind']!r}")
        if not r["week"].isdigit():
            raise SystemExit(f"{path}:{i}: week must be a number, got {r['week']!r}")

    # Rows render in file order, so file order has to be the calendar order. Catching a
    # shuffled row here beats publishing a schedule that reads out of sequence.
    for (i, prev), (j, cur) in zip(enumerate(rows, 2), enumerate(rows[1:], 3)):
        if dt.date.fromisoformat(cur["date"]) <= dt.date.fromisoformat(prev["date"]):
            raise SystemExit(f"{path}:{j}: dates must increase down the file "
                             f"({cur['date']} follows {prev['date']})")
        if int(cur["week"]) < int(prev["week"]):
            raise SystemExit(f"{path}:{j}: week numbers must not go backwards "
                             f"(week {cur['week']} follows week {prev['week']})")
    return rows


def build(key: str, spec: dict, lectures: dict[int, tuple[str, str]]) -> pathlib.Path:
    src = TEACHING / spec["source_csv"]
    origin = "the teaching library"
    if not src.exists():
        src = HERE / "schedules" / spec["csv"]
        origin = "this repo (the teaching library has no schedule.csv yet)"
    rows = read_rows(src)

    # Consecutive rows carrying the same week number form one week block.
    weeks: list[tuple[int, list[dict]]] = []
    for r in rows:
        w = int(r["week"])
        if not weeks or weeks[-1][0] != w:
            weeks.append((w, []))
        weeks[-1][1].append(r)

    meta = spec["meta"]
    # Topics as taught: a lecture still to come is published without its title or
    # reading, whatever the CSV and the typed notes say. Regenerating on a later day
    # is what puts them up, so this output is only as current as the last sync.
    as_taught, now = bool(meta.get("topics_as_taught")), today()
    out = [
        f"# {meta['code']} \u2014 {meta['term']}",
        "#",
        f"# GENERATED by teaching-src/gen_courses.py from {src.name} in {origin}.",
        "# Edit the CSV, not this file. Titles and readings left blank in the CSV are",
        "# filled from the typed lecture notes.",
        *(["# A lecture still to come carries no topic (topics_as_taught), so this file",
           "# also has to be regenerated as the semester runs."] if as_taught else []),
        "",
    ]
    for k, v in meta.items():
        if isinstance(v, bool):
            out.append(f"{k}: {'true' if v else 'false'}")
        elif isinstance(v, (int, float)):
            out.append(f"{k}: {v}")
        elif len(str(v)) > 90:
            out.append(f"{k}: >-")
            out.append("  " + str(v))
        else:
            out.append(f"{k}: {q(v)}")
    out.append("schedule:")

    for week, group in weeks:
        first_date = dt.date.fromisoformat(group[0]["date"])
        out.append(f"  - week: {week}")
        out.append(f"    span: {q(week_span(first_date))}")
        out.append("    meetings:")
        for r in group:
            date = dt.date.fromisoformat(r["date"])
            out.append(f"      - date: {r['date']}")
            out.append(f"        day: {q(date.strftime('%a'))}")
            out.append(f"        kind: {r['kind']}")
            title, reading = r["topic"], r["reading"]
            # A lecture that has not happened yet: nothing to say about it beyond its
            # number. Exams, breaks and review sessions are calendar facts and are
            # announced ahead of time, so they keep their titles.
            pending = as_taught and r["kind"] == "lecture" and date > now
            if r["lecture"].isdigit():
                n = int(r["lecture"])
                # Only courses that follow the typed notes' own lecture numbering may
                # borrow titles and readings from them; other terms numbered differently.
                fallback = lectures.get(n) if spec.get("notes_numbering") else None
                if fallback:
                    title = title or fallback[0]
                    reading = reading or fallback[1]
                out.append(f"        lecture: {n}")
                if spec.get("link_notes") and (REPO / f"files/stat400/notes/lec{n:02d}.pdf").exists():
                    out.append(f"        notes: /files/stat400/notes/lec{n:02d}.pdf")
                hand = spec.get("handwritten_dir")
                if hand and (REPO / hand.lstrip("/") / f"lec{n:02d}.pdf").exists():
                    out.append(f"        handwritten: {hand}/lec{n:02d}.pdf")
            if pending:
                out.append("        pending: true")
            else:
                out.append(f"        title: {q(title or r['kind'].title())}")
                if reading:
                    out.append(f"        reading: {q('Devore ' + reading)}")
            # A note on a row that carries no homework is about the meeting itself.
            if r["note"] and not r["hw"]:
                out.append(f"        note: {q(r['note'])}")

        # Homework and quizzes belong to the week: take the first row that carries them.
        hw = next((r for r in group if r["hw"]), None)
        if hw:
            out.append("    hw:")
            out.append(f"      id: {hw['hw']}")
            if hw["hw_posted"]:
                out.append(f"      posted: {hw['hw_posted']}")
            if hw["hw_due"]:
                out.append(f"      due: {hw['hw_due']}")
            if hw["note"]:
                out.append(f"      note: {q(hw['note'])}")
        quiz = next((r["quiz"] for r in group if r["quiz"]), None)
        if quiz:
            out.append(f"    quiz: {q(quiz)}")

    dest = OUT / f"{key}.yml"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n".join(out) + "\n", encoding="utf-8")
    return dest


def main() -> int:
    registry = json.loads((HERE / "courses.json").read_text(encoding="utf-8"))
    wanted = sys.argv[1:] or list(registry)
    lectures = typed_lectures()
    for key in wanted:
        if key not in registry:
            raise SystemExit(f"unknown course {key!r}; known: {', '.join(registry)}")
        dest = build(key, registry[key], lectures)
        print(f"wrote {dest.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
