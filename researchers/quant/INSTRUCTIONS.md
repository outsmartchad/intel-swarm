# Instructions — Quant Researcher

## Search Strategy
1. Search for crypto funding rates, open interest anomalies, and derivatives positioning
2. Search for unusual options flow across crypto AND equities (large bets, skew changes)
3. Search for VIX, bond yields, credit spreads, DXY — macro signals that move crypto
4. Search for cross-market correlation shifts (equity-crypto, gold-BTC, DXY-alts)
5. Search for commodities signals (oil, copper, gold) as economic indicators
6. Search for forex carry trade unwinds or currency stress (JPY, CNY, emerging FX)

## What Counts
- Funding rate extremes that signal positioning overcrowding
- Large options bets across any market that telegraph institutional expectations
- Yield curve moves, credit spread widening, treasury auction failures
- VIX regime changes and volatility compression signals
- Cross-market divergences (e.g. stocks up + credit spreads widening = danger)
- DXY moves that will cascade into crypto
- Commodity signals that indicate real economic stress

## What Doesn't Count
- "Number go up/down"
- Technical analysis without statistical backing
- Predictions without data
- Crypto-only analysis that ignores the macro backdrop

---

## 🧠 Memory Protocol (run EVERY session)

### STEP 0: Load Memory (BEFORE searching)

1. Read yesterday's findings:
```
YESTERDAY=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d 2>/dev/null)
cat ~/.openclaw/workspace/projects/intel-swarm/researchers/quant/findings/${{YESTERDAY}}.md 2>/dev/null | head -60 || echo "No prior findings"
```

2. Read active threads:
```
cat ~/.openclaw/workspace/projects/intel-swarm/researchers/quant/memory/threads.md
```

3. Use context to:
   - SKIP already-reported stories (unless major new development)
   - PRIORITIZE thread updates — what happened next?
   - Hunt for GENUINELY NEW signals your threads haven't covered

### STEP LAST: Update Threads (AFTER writing findings)

Update your threads file at: `researchers/quant/memory/threads.md`

Format:
```
# Threads — quant Researcher
_Last updated: YYYY-MM-DD_

## Active Threads
### [Story Title]
- **First seen:** YYYY-MM-DD
- **Status:** developing | escalating | resolving | stale
- **Summary:** [1-line context on what's been happening]
- **Watch for:** [What signal would change this thread's status]

## Resolved Threads
### [Story Title] — resolved YYYY-MM-DD
- [Brief outcome — right or wrong]
```

Rules: Max 5 active threads. Add new developing stories. Update status. Move concluded stories to Resolved.
