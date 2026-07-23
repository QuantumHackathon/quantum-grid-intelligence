#!/usr/bin/env bash
# Regenerates WHITEPAPER.pdf and WHITEPAPER_ES.pdf from their markdown sources.
# Usage: ./whitepaper/build.sh   (from anywhere; cds to repo root)
# Requires: pandoc, typst (brew install typst)
set -euo pipefail
cd "$(dirname "$0")/.."

for suffix in "" "_ES"; do
  echo "Building WHITEPAPER${suffix}.pdf ..."
  pandoc "WHITEPAPER${suffix}.md" -o "WHITEPAPER${suffix}.pdf" \
    --pdf-engine=typst \
    --template=whitepaper/template.typ \
    --toc --toc-depth=2 \
    --resource-path=.:results:docs/diagrams/output/vertical:nexus
done

echo "Done: WHITEPAPER.pdf, WHITEPAPER_ES.pdf"
