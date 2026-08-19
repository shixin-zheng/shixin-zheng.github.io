#!/usr/bin/env python3
"""Publish the handwritten lecture PDFs for each course that declares them.

Source files are the iPad exports kept in the teaching library, named
`Week<W>-Lec<N>.pdf`. They are copied — never moved or rewritten — to
files/stat400/<term>/handwritten/lec<NN>.pdf, which is what the schedule links to.

Courses opt in through `handwritten_src` in teaching-src/courses.json. A course whose
source directory does not exist yet is simply skipped, so this can run all semester while
lectures are still being uploaded.

    ./teaching-src/copy-handwritten.py
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import shutil
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
HERE = REPO / "teaching-src"
TEACHING = pathlib.Path(os.environ.get("TEACHING_ROOT", pathlib.Path.home() / "teaching"))

LEC = re.compile(r"lec[\s_-]*0*(\d+)", re.I)


def main() -> int:
    registry = json.loads((HERE / "courses.json").read_text(encoding="utf-8"))
    total = 0

    for key, spec in registry.items():
        src_rel = spec.get("handwritten_src")
        if not src_rel:
            continue
        src = TEACHING / src_rel
        dest = REPO / spec["handwritten_dir"].lstrip("/")
        if not src.is_dir():
            print(f"{key}: no handwritten notes yet ({src_rel})")
            continue

        dest.mkdir(parents=True, exist_ok=True)
        seen = {}
        for pdf in sorted(src.glob("*.pdf")):
            m = LEC.search(pdf.stem)
            if not m:
                print(f"  skipped {pdf.name}: no lecture number in the filename")
                continue
            n = int(m.group(1))
            if n in seen:
                print(f"  skipped {pdf.name}: lecture {n} already taken by {seen[n]}")
                continue
            seen[n] = pdf.name
            target = dest / f"lec{n:02d}.pdf"
            if not target.exists() or target.read_bytes() != pdf.read_bytes():
                shutil.copy2(pdf, target)
            total += 1

        # Drop copies whose source disappeared, so the site never links a stale scan.
        for stale in dest.glob("lec*.pdf"):
            n = int(stale.stem[3:])
            if n not in seen:
                stale.unlink()
                print(f"  removed {stale.name}: no longer in the teaching library")

        size = sum(p.stat().st_size for p in dest.glob("*.pdf")) / 1e6
        print(f"{key}: {len(seen)} handwritten lectures, {size:.1f} MB")

    print(f"{total} file(s) published")
    return 0


if __name__ == "__main__":
    sys.exit(main())
