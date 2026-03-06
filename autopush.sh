#!/bin/bash
# intel-swarm autopush — full daily pipeline
# Runs at 08:00 HKT after all researcher crons finish (last one ends ~07:50)
#
# Pipeline:
#   1. translate.py     — zh translation for every findings file missing one
#   2. fetch-images.py  — OG scrape + Brave fallback for every finding
#   3. git commit -A    — commit all findings + translations + images
#   4. git push         — push to GitHub
#   5. vercel --prod    — deploy to Vercel

set -euo pipefail

REPO="$HOME/.openclaw/workspace/projects/intel-swarm"
FETCH="$REPO/web/fetch-images.py"
TRANSLATE="$REPO/web/translate.py"
DATE=$(date +%Y-%m-%d)
LOG_PREFIX="[$(date '+%Y-%m-%d %H:%M:%S')]"

export BRAVE_API_KEY="BRAVE_API_KEY_REDACTED"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

cd "$REPO"
echo "$LOG_PREFIX ▶ intel-swarm pipeline starting for $DATE"

RESEARCHERS="war commodities religion health culture emerging ai-agents crypto macro singularity quant westeast blackbudget conspiracy sports russia china north-korea"

# ── Step 1: Translate missing zh files (parallel) ─────────────────────────────
echo "$LOG_PREFIX 🌏 Step 1: Translating..."
pids=()
for rid in $RESEARCHERS; do
  en="$REPO/researchers/$rid/findings/$DATE.md"
  zh="$REPO/researchers/$rid/findings/$DATE.zh.md"
  if [ -f "$en" ] && { [ ! -f "$zh" ] || [ "$en" -nt "$zh" ]; }; then
    python3 "$TRANSLATE" "$en" &
    pids+=($!)
  fi
done
for name in synthesis chief; do
  en="$REPO/$name/findings/$DATE.md"
  zh="$REPO/$name/findings/$DATE.zh.md"
  if [ -f "$en" ] && { [ ! -f "$zh" ] || [ "$en" -nt "$zh" ]; }; then
    python3 "$TRANSLATE" "$en" &
    pids+=($!)
  fi
done
for pid in "${pids[@]:-}"; do wait "$pid" 2>/dev/null || true; done
echo "$LOG_PREFIX ✓ Translations done"

# ── Step 2: Fetch images for all researchers (parallel) ───────────────────────
echo "$LOG_PREFIX 📸 Step 2: Fetching images..."
pids=()
for rid in $RESEARCHERS; do
  f="$REPO/researchers/$rid/findings/$DATE.md"
  if [ -f "$f" ]; then
    python3 "$FETCH" "$f" &
    pids+=($!)
  fi
done
for name in synthesis chief; do
  f="$REPO/$name/findings/$DATE.md"
  if [ -f "$f" ]; then
    python3 "$FETCH" "$f" &
    pids+=($!)
  fi
done
for pid in "${pids[@]:-}"; do wait "$pid" 2>/dev/null || true; done
echo "$LOG_PREFIX ✓ Images done"

# ── Step 3: Commit everything ─────────────────────────────────────────────────
echo "$LOG_PREFIX 💾 Step 3: Committing..."
git add -A
if git diff --staged --quiet; then
  echo "$LOG_PREFIX   Nothing to commit — already up to date"
else
  git commit -m "autopush: findings + translations + images $DATE"
  echo "$LOG_PREFIX ✓ Committed"
fi

# ── Step 4: Push to GitHub ────────────────────────────────────────────────────
echo "$LOG_PREFIX 📤 Step 4: Pushing to GitHub..."
git push origin main 2>&1
echo "$LOG_PREFIX ✓ Pushed"

# ── Step 5: Deploy to Vercel ──────────────────────────────────────────────────
echo "$LOG_PREFIX 🚀 Step 5: Deploying to Vercel..."
vercel --prod --yes 2>&1
echo "$LOG_PREFIX ✓ Deployed"

echo "$LOG_PREFIX ✅ Pipeline complete!"
