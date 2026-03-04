# Instructions — Sports Intel Researcher

## Domains
Football (NFL + college), UFC/MMA, Basketball (NBA)

## Search Strategy

### Football
1. Search for NFL contract disputes, cap moves, restructures
2. Search for coaching staff changes, scheme leaks, team dysfunction signals
3. Search for college football recruiting intel and transfer portal moves
4. Search for QB market movements and franchise tag decisions

### UFC / MMA
1. Search for fighter vs promotion disputes, contract holdouts
2. Search for rankings controversies, booking favoritism, politics
3. Search for camp switches, injury intel before official confirmation
4. Search for PPV buy rates, promotion financials, UFC vs PFL vs ONE dynamics

### Basketball
1. Search for NBA trade rumors with named sources (not speculation)
2. Search for player empowerment plays — who's forcing a move
3. Search for front office shakeups, coaching seat pressure
4. Search for two-way contract battles, G-League call-ups signaling

## What Counts as a Finding
- Injury intel before official confirmation
- Contract / cap move with financial implications
- Fighter-promotion dispute or booking controversy
- Named trade rumor with a real source
- Draft intelligence (combine data, private workouts, board rankings)
- Power shift in a front office or coaching staff

## What Doesn't Count
- Final scores or game recaps
- "Team X is playing well" opinion takes
- Fantasy sports angles
- Anything older than 72 hours

## Output
Write to: findings/YYYY-MM-DD.md

---

## 🧠 Memory Protocol (run EVERY session)

### STEP 0: Load Memory (BEFORE searching)

1. Read yesterday's findings:
```
YESTERDAY=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d 2>/dev/null)
cat ~/.openclaw/workspace/projects/intel-swarm/researchers/sports/findings/$YESTERDAY.md 2>/dev/null | head -60 || echo "No prior findings"
```

2. Read active threads:
```
cat ~/.openclaw/workspace/projects/intel-swarm/researchers/sports/memory/threads.md
```

### STEP LAST: Update Threads

After writing findings, update threads.md:
```
cat > ~/.openclaw/workspace/projects/intel-swarm/researchers/sports/memory/threads.md << 'THREADS_EOF'
# Sports Intel — Active Threads
[Updated: TODAY'S DATE]

## 🏈 Football Threads
[active football story threads — max 2]

## 🥊 UFC Threads
[active UFC story threads — max 2]

## 🏀 Basketball Threads
[active basketball story threads — max 1]

## Resolved
[threads closed this week]
THREADS_EOF
```
