#!/usr/bin/env bash
# Build the public STAT400 lecture-note PDFs served under /files/stat400/notes/.
#
# Source of truth is the typed-notes LaTeX project in the teaching library:
#   ~/teaching/courses/STAT400/lectures/typed/
# That directory belongs to a different agent — this script never writes to it.
# It copies the project to a temp dir, compiles one PDF per lecture plus the
# combined volume, and drops the results into files/stat400/notes/.
#
# Usage: ./teaching-src/build-stat400-notes.sh
# Requires: tectonic (brew install tectonic)
set -euo pipefail

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
for tex in lectures/lec*.tex; do
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

# Combined volume, straight from main.tex.
tectonic -X compile main.tex --outdir . >/dev/null 2>&1
mv main.pdf "$out/stat400-lecture-notes.pdf"

echo "Wrote $(ls "$out"/*.pdf | wc -l | tr -d ' ') PDFs to files/stat400/notes/"
