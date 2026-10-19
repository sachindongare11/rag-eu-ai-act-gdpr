#!/bin/sh
# Make a clean copy of the project that is safe to publish: no git history, no secrets, no PDFs,
# no generated indexes, no personal notes. Review the result, then `git init` there and push.
#
#   scripts/export_public.sh ../rag-eu-law-public
set -eu

target="${1:?usage: scripts/export_public.sh <empty-target-directory>}"
here="$(cd "$(dirname "$0")/.." && pwd)"

if [ -d "$target" ] && [ -n "$(ls -A "$target" 2>/dev/null)" ]; then
    echo "error: $target exists and is not empty" >&2
    exit 1
fi

mkdir -p "$target"
rsync -a --prune-empty-dirs --filter="merge $here/scripts/public_excludes.txt" "$here"/ "$target"/
mkdir -p "$target/data/raw" "$target/data/processed"
touch "$target/data/raw/.gitkeep" "$target/data/processed/.gitkeep"

echo "Exported to $target"
echo "Check before publishing:"
echo "  grep -rEI 'sk-[A-Za-z0-9_-]{12,}|eyJ[A-Za-z0-9_-]{20,}' '$target' | head"
echo "  find '$target' -name '*.pdf' -o -name '.env'"
echo "Note: the Streamlit Cloud entrypoint needs the PDFs in data/raw/ to build its index."
