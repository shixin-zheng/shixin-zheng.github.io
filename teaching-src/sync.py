#!/usr/bin/env python3
"""Pull teaching updates from ~/teaching into the website.

The teaching library (~/teaching) is maintained separately — lecture notes get revised
during the semester, and the as-taught schedule moves week to week. This script watches
the source files the website depends on, rebuilds whatever they feed, and can commit and
push the result.

    ./teaching-src/sync.py              # report what changed, touch nothing
    ./teaching-src/sync.py --apply      # rebuild the affected outputs
    ./teaching-src/sync.py --apply --push   # ... and commit + push to master

State lives in teaching-src/sources.lock.json: one sha256 per watched source file.
Sources are read-only here; nothing is ever written back into ~/teaching.

Watched sources and what they drive:

  schedule     syllabus/<term>/schedule.csv  ->  _data/courses/*.yml
               The editable calendar. Whatever is in the teaching library wins over the
               copy kept in teaching-src/schedules/.
  handwritten  lectures/<term>/pdf/Week*-Lec*.pdf  ->  files/stat400/<term>/handwritten/
               Only for courses that opt in via handwritten_src in courses.json.
  typed notes  lectures/typed/**.tex,.sty   ->  files/stat400/notes/*.pdf, and the
                                                lecture titles/readings the schedule
                                                leaves blank
  as-taught    syllabus/<term>/schedule-as-taught.csv  ->  reported only; the older
               spreadsheet snapshot format, superseded by schedule.csv
  syllabus     syllabus/<term>/*.pdf        ->  reported only; needs a human read
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
TEACHING = pathlib.Path(os.environ.get("TEACHING_ROOT", pathlib.Path.home() / "teaching"))
STAT400 = TEACHING / "courses/STAT400"
LOCK = REPO / "teaching-src/sources.lock.json"

# group -> list of source files (missing files are simply absent from the scan)
GROUPS = {
    "schedule": sorted(STAT400.glob("syllabus/*/schedule.csv")),
    "handwritten": sorted(STAT400.glob("lectures/*/pdf/*.pdf")),
    "typed-notes": sorted(STAT400.glob("lectures/typed/**/*.tex")) +
                   sorted(STAT400.glob("lectures/typed/**/*.sty")),
    "as-taught": sorted(STAT400.glob("syllabus/*/schedule-as-taught.csv")),
    "syllabus": sorted(STAT400.glob("syllabus/*/*.pdf")),
}


def sha(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def scan() -> dict[str, dict[str, str]]:
    return {
        group: {str(p.relative_to(TEACHING)): sha(p) for p in files}
        for group, files in GROUPS.items()
    }


def load_lock() -> dict[str, dict[str, str]]:
    if not LOCK.exists():
        return {}
    return json.loads(LOCK.read_text())


def diff(now, before):
    """-> {group: {'added': [...], 'changed': [...], 'removed': [...]}} for groups that moved."""
    out = {}
    for group, files in now.items():
        old = before.get(group, {})
        added = sorted(set(files) - set(old))
        removed = sorted(set(old) - set(files))
        changed = sorted(f for f in files if f in old and files[f] != old[f])
        if added or removed or changed:
            out[group] = {"added": added, "changed": changed, "removed": removed}
    return out


def run(cmd, **kw):
    print(f"  $ {' '.join(str(c) for c in cmd)}")
    return subprocess.run(cmd, cwd=REPO, check=True, **kw)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="rebuild the affected outputs")
    ap.add_argument("--push", action="store_true", help="commit and push if anything changed")
    args = ap.parse_args()

    if not STAT400.exists():
        print(f"teaching library not found at {TEACHING}", file=sys.stderr)
        return 1

    now, before = scan(), load_lock()
    changes = diff(now, before)

    if not changes:
        print("teaching sources unchanged — nothing to do")
        return 0

    for group, d in changes.items():
        print(f"\n{group}:")
        for kind in ("added", "changed", "removed"):
            for f in d[kind]:
                print(f"  {kind:<8} {f}")

    if "syllabus" in changes:
        print("\nnote: a syllabus PDF moved. Course facts (meeting times, room, sections,\n"
              "      office hours, grading) are not parsed automatically — read it and update\n"
              "      teaching-src/courses.json by hand.")

    if "as-taught" in changes:
        print("\nnote: a schedule-as-taught.csv moved. That is the older snapshot format;\n"
              "      the website reads syllabus/<term>/schedule.csv. Fold the change into the\n"
              "      schedule.csv for that term, or into teaching-src/schedules/ if there is none.")

    if not args.apply:
        print("\n(dry run; pass --apply to rebuild)")
        return 0

    print()
    if "typed-notes" in changes:
        touched = changes["typed-notes"]["added"] + changes["typed-notes"]["changed"]
        slugs = sorted({pathlib.Path(f).stem for f in touched
                        if pathlib.Path(f).stem.startswith("lec")})
        shared = [f for f in touched if pathlib.Path(f).stem in ("main", "preamble")]
        if shared or not slugs:
            print("rebuilding every lecture-note PDF (shared source changed)")
            run([REPO / "teaching-src/build-stat400-notes.sh"])
        else:
            print(f"rebuilding lecture-note PDFs: {', '.join(slugs)}")
            run([REPO / "teaching-src/build-stat400-notes.sh", *slugs])

    if "handwritten" in changes:
        print("publishing handwritten lecture scans")
        run([sys.executable, REPO / "teaching-src/copy-handwritten.py"])

    if changes.keys() & {"schedule", "typed-notes", "handwritten"}:
        print("regenerating course schedules")
        run([sys.executable, REPO / "teaching-src/gen_courses.py"])

    LOCK.write_text(json.dumps(now, indent=2, sort_keys=True) + "\n")
    print(f"\nupdated {LOCK.relative_to(REPO)}")

    status = subprocess.run(["git", "status", "--porcelain"], cwd=REPO,
                            capture_output=True, text=True).stdout.strip()
    if not status:
        print("no output changed (sources moved but rebuilds are byte-identical)")
        return 0

    print("\nworking tree:")
    print("\n".join("  " + line for line in status.splitlines()))

    if not args.push:
        print("\n(pass --push to commit and push)")
        return 0

    groups = ", ".join(sorted(changes))
    run(["git", "add", "-A"])
    run(["git", "commit", "-q", "-m",
         f"Sync teaching materials from ~/teaching ({groups})"])
    run(["git", "push", "origin", "master"])
    print("\npushed; GitHub Pages will redeploy in about a minute")
    return 0


if __name__ == "__main__":
    sys.exit(main())
