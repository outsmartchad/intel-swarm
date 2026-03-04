# Instructions — ai-agents blackbudget conspiracy crypto culture emerging epstein macro power psyops quant regulatory singularity war westeast Researcher

## Output
Write to: findings/YYYY-MM-DD.md

---

## 🧠 Memory Protocol (run EVERY session)

### STEP 0: Load Memory (BEFORE searching)

1. Read yesterday's findings (if they exist):
```
YESTERDAY=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d 2>/dev/null)
cat ~/.openclaw/workspace/projects/intel-swarm/researchers/ai-agents blackbudget conspiracy crypto culture emerging epstein macro power psyops quant regulatory singularity war westeast/findings/${YESTERDAY}.md 2>/dev/null | head -60 || echo "No prior findings"
```

2. Read your active threads:
```
cat ~/.openclaw/workspace/projects/intel-swarm/researchers/ai-agents blackbudget conspiracy crypto culture emerging epstein macro power psyops quant regulatory singularity war westeast/memory/threads.md
```

3. Use this context to:
   - SKIP stories already reported yesterday (unless major new development)
   - PRIORITIZE updates on active threads — what happened next?
   - Focus searches on finding GENUINELY NEW signals

### STEP LAST: Update Memory (AFTER writing findings)

After writing findings, update your threads file:

```
cat > ~/.openclaw/workspace/projects/intel-swarm/researchers/ai-agents blackbudget conspiracy crypto culture emerging epstein macro power psyops quant regulatory singularity war westeast/memory/threads.md << 'THREADS_EOF'
# Threads — ai-agents blackbudget conspiracy crypto culture emerging epstein macro power psyops quant regulatory singularity war westeast Researcher
_Last updated: YYYY-MM-DD_

## Active Threads
### [Story Title]
- **First seen:** YYYY-MM-DD
- **Status:** developing | escalating | resolving | stale
- **Summary:** [1-line context]
- **Watch for:** [What signal changes this thread's status]

## Resolved Threads
### [Story Title] — resolved YYYY-MM-DD
- [Brief outcome]
THREADS_EOF
```

**Thread rules:**
- Add any story developing over next 3-7 days
- Update status when new evidence arrives
- Move to Resolved when story concludes
- Max 5 active threads — prune weakest if over limit
