#!/usr/bin/env bash
# Rebuild the CV PDF served at /files/CV_Shixin_Zheng.pdf from its LaTeX source.
# Usage: ./cv-src/build.sh   (from anywhere; paths are resolved relative to this script)
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo="$(dirname "$here")"

tectonic --outdir "$here" "$here/CV_Shixin_Zheng.tex"
mv "$here/CV_Shixin_Zheng.pdf" "$repo/files/CV_Shixin_Zheng.pdf"

echo "Rebuilt files/CV_Shixin_Zheng.pdf"
