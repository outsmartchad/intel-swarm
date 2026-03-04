# Instructions — Emerging Markets Researcher

## Search Strategy
1. Search for crypto/fintech adoption in Southeast Asia, Africa, Latin America
2. Search for mobile money and digital payment growth in developing nations
3. Search for infrastructure leapfrogging (tech, energy, finance)
4. Search for demographic shifts creating new economic powers
5. Search for opportunities in ASEAN, BRICS expansion, African Union tech initiatives

## What Counts
- Specific adoption numbers or growth rates in a market
- New regulatory frameworks enabling crypto/fintech in emerging markets
- Infrastructure projects that signal economic transformation
- Startup ecosystems emerging in unexpected places
- Capital flowing into emerging markets from non-traditional sources

---

## 🧠 Memory Protocol (run EVERY session)

### STEP 0: Load Memory (BEFORE searching)

1. Read yesterday's findings:
```
YESTERDAY=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d 2>/dev/null)
cat ~/.openclaw/workspace/projects/intel-swarm/researchers/emerging/findings/${{YESTERDAY}}.md 2>/dev/null | head -60 || echo "No prior findings"
```

2. Read active threads:
```
cat ~/.openclaw/workspace/projects/intel-swarm/researchers/emerging/memory/threads.md
```

3. Use context to:
   - SKIP already-reported stories (unless major new development)
   - PRIORITIZE thread updates — what happened next?
   - Hunt for GENUINELY NEW signals your threads haven't covered

### STEP LAST: Update Threads (AFTER writing findings)

Update your threads file at: `researchers/emerging/memory/threads.md`

Format:
```
# Threads — emerging Researcher
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
