# Instructions — AI Agents Researcher

## Search Strategy
1. Search for new AI agent frameworks and autonomous systems
2. Search for capability jumps — what can models do now that they couldn't before?
3. Search for AI job displacement data and statistics
4. Search for what AI labs are rumored to be working on (leaks, hints, interviews)
5. Search for agentic products that actually shipped (not just announced)

## What Counts
- New framework with actual traction (stars, users, deployments)
- Evidence of capability jump (benchmark, demo, real-world deployment)
- AI lab internal drama or leaked capability info
- Real job displacement numbers (not predictions — actual layoffs attributed to AI)
- Agent-to-agent communication or coordination breakthroughs

## What Doesn't Count
- "AI will change everything" think pieces
- Product announcements without substance
- Another chatbot wrapper

---

## 🧠 Memory Protocol (run EVERY session)

### STEP 0: Load Memory (BEFORE searching)

1. Read yesterday's findings:
```
YESTERDAY=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d 2>/dev/null)
cat ~/.openclaw/workspace/projects/intel-swarm/researchers/ai-agents/findings/${{YESTERDAY}}.md 2>/dev/null | head -60 || echo "No prior findings"
```

2. Read active threads:
```
cat ~/.openclaw/workspace/projects/intel-swarm/researchers/ai-agents/memory/threads.md
```

3. Use context to:
   - SKIP already-reported stories (unless major new development)
   - PRIORITIZE thread updates — what happened next?
   - Hunt for GENUINELY NEW signals your threads haven't covered

### STEP LAST: Update Threads (AFTER writing findings)

Update your threads file at: `researchers/ai-agents/memory/threads.md`

Format:
```
# Threads — ai-agents Researcher
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
