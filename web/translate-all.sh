#!/bin/bash
# Batch translate all findings for a given date (default: today)
DATE=${1:-$(date +%Y-%m-%d)}
BASE="$(dirname "$0")/.."
TRANSLATE="$(dirname "$0")/translate.py"

echo "🌏 Translating all findings for $DATE..."

FILES=(
  # Core domains
  "$BASE/researchers/war/findings/$DATE.md"
  "$BASE/researchers/commodities/findings/$DATE.md"
  "$BASE/researchers/religion/findings/$DATE.md"
  "$BASE/researchers/health/findings/$DATE.md"
  "$BASE/researchers/crypto/findings/$DATE.md"
  "$BASE/researchers/ai-agents/findings/$DATE.md"
  "$BASE/researchers/macro/findings/$DATE.md"
  "$BASE/researchers/singularity/findings/$DATE.md"
  "$BASE/researchers/quant/findings/$DATE.md"
  "$BASE/researchers/westeast/findings/$DATE.md"
  "$BASE/researchers/blackbudget/findings/$DATE.md"
  "$BASE/researchers/emerging/findings/$DATE.md"
  "$BASE/researchers/conspiracy/findings/$DATE.md"
  "$BASE/researchers/epstein/findings/$DATE.md"
  "$BASE/researchers/culture/findings/$DATE.md"
  "$BASE/researchers/sports/findings/$DATE.md"
  # Communist States sub-researchers
  "$BASE/researchers/russia/findings/$DATE.md"
  "$BASE/researchers/china/findings/$DATE.md"
  "$BASE/researchers/north-korea/findings/$DATE.md"
  # Synthesis + Chief
  "$BASE/synthesis/findings/$DATE.md"
  "$BASE/chief/findings/$DATE.md"
)

# Run translations in parallel (5 at a time to avoid rate limits)
count=0
for f in "${FILES[@]}"; do
  if [ -f "$f" ]; then
    python3 "$TRANSLATE" "$f" &
    ((count++))
    if (( count % 5 == 0 )); then
      wait
    fi
  fi
done

wait
echo "✅ Done translating $DATE"
