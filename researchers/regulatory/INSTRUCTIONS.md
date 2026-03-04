# Instructions — Regulatory Arbitrage Researcher

## Search Strategy
1. Search for crypto-friendly jurisdiction developments and new frameworks
2. Search for proposed DeFi/crypto regulation in major markets (US, EU, Asia)
3. Search for DAO legal structure developments and case law
4. Search for offshore/special economic zone updates relevant to crypto
5. Search for enforcement actions that signal regulatory direction

## What Counts
- New jurisdictions opening crypto-friendly frameworks
- Proposed legislation that would change DeFi/crypto landscape
- DAO legal precedents being set in courts
- Enforcement actions that signal what regulators are targeting next
- Creative legal structures that projects are using successfully

---

## 🧠 Memory Protocol (run EVERY session)

### STEP 0: Load Memory (BEFORE searching)

1. Read yesterday's findings:
```
YESTERDAY=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d 2>/dev/null)
cat ~/.openclaw/workspace/projects/intel-swarm/researchers/regulatory/findings/${{YESTERDAY}}.md 2>/dev/null | head -60 || echo "No prior findings"
```

2. Read active threads:
```
cat ~/.openclaw/workspace/projects/intel-swarm/researchers/regulatory/memory/threads.md
```

3. Use context to:
   - SKIP already-reported stories (unless major new development)
   - PRIORITIZE thread updates — what happened next?
   - Hunt for GENUINELY NEW signals your threads haven't covered

### STEP LAST: Update Threads (AFTER writing findings)

Update your threads file at: `researchers/regulatory/memory/threads.md`

Format:
```
# Threads — regulatory Researcher
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
