#!/usr/bin/env bash
# Build the public STAT400 lecture-note PDFs served under /files/stat400/notes/.
#
# Source of truth is the typed-notes LaTeX project in the teaching library:
#   ~/teaching/courses/STAT400/lectures/typed/
# That directory belongs to a different agent — this script never writes to it.
# It copies the project to a temp dir, compiles one PDF per lecture plus the
# combined volume, and drops the results into files/stat400/notes/.
#
# Usage:
#   ./teaching-src/build-stat400-notes.sh              # every lecture
#   ./teaching-src/build-stat400-notes.sh lec11 lec22  # just these, plus the volume
#
# SOURCE_DATE_EPOCH is pinned so that unchanged content compiles to byte-identical
# PDFs. Without it tectonic stamps each build with the current time and every weekly
# sync would rewrite all 27 files in git for no reason.
#
# Requires: tectonic (brew install tectonic)
set -euo pipefail

export SOURCE_DATE_EPOCH=1767225600   # 2026-01-01T00:00:00Z, arbitrary but fixed

src="${STAT400_TYPED:-$HOME/teaching/courses/STAT400/lectures/typed}"
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo="$(dirname "$here")"
out="$repo/files/stat400/notes"

[ -d "$src" ] || { echo "typed-notes project not found: $src" >&2; exit 1; }
command -v tectonic >/dev/null || { echo "tectonic not installed" >&2; exit 1; }

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
cp -R "$src/" "$tmp/typed"
rm -rf "$tmp/typed/out"
mkdir -p "$out"

cd "$tmp/typed"

if [ "$#" -gt 0 ]; then
  targets=()
  for slug in "$@"; do
    [ -f "lectures/$slug.tex" ] || { echo "no such lecture: $slug" >&2; exit 1; }
    targets+=("lectures/$slug.tex")
  done
else
  targets=(lectures/lec*.tex)
fi

for tex in "${targets[@]}"; do
  slug="$(basename "$tex" .tex)"          # lec07
  num="$((10#${slug#lec}))"               # 7
  cat > "wrap-$slug.tex" <<EOF
\\documentclass[11pt,oneside]{book}
\\usepackage{preamble}
\\begin{document}
\\mainmatter
\\setcounter{chapter}{$((num - 1))}
\\input{lectures/$slug}
\\end{document}
EOF
  tectonic -X compile "wrap-$slug.tex" --outdir . >/dev/null 2>&1
  mv "wrap-$slug.pdf" "$out/$slug.pdf"
  printf '.'
done
echo

# The combined volume always changes when any lecture does.
tectonic -X compile main.tex --outdir . >/dev/null 2>&1
mv main.pdf "$out/stat400-lecture-notes.pdf"

echo "Rebuilt ${#targets[@]} lecture PDF(s) and the combined volume"
