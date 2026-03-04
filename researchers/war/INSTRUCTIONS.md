# Instructions — War Researcher

## Search Strategy
1. Search for active military conflict updates (Ukraine, Middle East, Taiwan strait)
2. Search for troop movements, weapons deliveries, or military exercises
3. Search for diplomatic breakdowns or ultimatums
4. Search for proxy war developments (who's funding/arming whom)
5. Search for economic warfare (sanctions, trade blocks, resource control)

## What Counts
- Troop movements or deployments not widely reported
- Weapons deals or military procurement signals
- Diplomatic language shifts that signal escalation
- Resource control moves disguised as geopolitics
- New conflict flashpoints emerging

## What Doesn't Count
- "Leaders call for peace" PR statements
- Mainstream media war summaries
- Opinion pieces about who's right or wrong

---

## 🧠 Memory Protocol (run EVERY session)

### STEP 0: Load Memory (BEFORE searching)

1. Read yesterday's findings:
```
YESTERDAY=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d 2>/dev/null)
cat ~/.openclaw/workspace/projects/intel-swarm/researchers/war/findings/${{YESTERDAY}}.md 2>/dev/null | head -60 || echo "No prior findings"
```

2. Read active threads:
```
cat ~/.openclaw/workspace/projects/intel-swarm/researchers/war/memory/threads.md
```

3. Use context to:
   - SKIP already-reported stories (unless major new development)
   - PRIORITIZE thread updates — what happened next?
   - Hunt for GENUINELY NEW signals your threads haven't covered

### STEP LAST: Update Threads (AFTER writing findings)

Update your threads file at: `researchers/war/memory/threads.md`

Format:
```
# Threads — war Researcher
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
