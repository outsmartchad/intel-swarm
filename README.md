# 🐝 Intel Swarm

Private intelligence research org for Vincent. 15 AI researchers + synthesis + chief scientist — with persistent memory.

> **Purpose:** Feed high-signal, under-reported intel across 15 domains daily. Not news — EDGE. Information that 99% don't know, don't want to know, or can't connect.

> **Inspired by:** [Karpathy's multi-agent research org](https://x.com/karpathy) — "You are now programming an organization. The source code is prompts, skills, tools, and processes."

## Architecture

```
06:00 HKT ─── 15 Researchers fire sequentially (3 min apart)
                │
                │  Each researcher BEFORE searching:
                │  ├── reads findings/yesterday.md (avoids repeating)
                │  └── reads memory/threads.md (tracks ongoing stories)
                │
                ├── researchers/crypto/findings/YYYY-MM-DD.md      (06:00)
                ├── researchers/ai-agents/findings/YYYY-MM-DD.md   (06:03)
                ├── researchers/conspiracy/findings/YYYY-MM-DD.md  (06:06)
                ├── ... (15 total, last at 06:42)
                │
                │  Each researcher AFTER writing:
                │  └── updates memory/threads.md (ongoing story threads)
                │
07:15 HKT ─── Synthesis Agent reads all 15 → connects dots
                │  reads synthesis/findings/yesterday.md
                │  reads synthesis/memory/thesis.md (evolving meta-thesis)
                │
                └── synthesis/findings/YYYY-MM-DD.md
                │  updates synthesis/memory/thesis.md
                │
07:45 HKT ─── Chief Scientist reads ALL raw findings + synthesis → challenges everything
                │  reads chief/findings/yesterday.md
                │  reads chief/memory/predictions.md (prediction scoreboard)
                │  reads chief/memory/thesis.md (risk register)
                │
                └── chief/findings/YYYY-MM-DD.md → Telegram briefing to Vincent
                   updates chief/memory/predictions.md + thesis.md
```

## Researchers

| # | ID | Name | Model | SOUL |
|---|-----|------|-------|------|
| 1 | crypto | 🪙 Crypto Researcher | Sonnet 4.6 | Degen who went legit. Prediction markets, AMMs, launchpads, bleeding-edge on-chain |
| 2 | ai-agents | 🤖 AI Agents Researcher | Sonnet 4.6 | Reads the papers. Tracks what labs aren't saying. Unimpressed by demos |
| 3 | conspiracy | 🕳️ Conspiracy Researcher | Sonnet 4.6 | Evidence-first. Tracks the line between paranoia and pattern recognition |
| 4 | epstein | 📁 Epstein & Deep State | Sonnet 4.6 | FOIA obsessive. Court filings for fun. Follows the blackmail networks |
| 5 | war | ⚔️ War Researcher | Sonnet 4.6 | Ex-OSINT analyst. Follows logistics, not headlines. Every war has an economic motive |
| 6 | macro | 📊 Macro Economist | Sonnet 4.6 | Watches what central banks DO, not SAY. Thinks in systems |
| 7 | power | 🕴️ Power Structures | Sonnet 4.6 | Maps power like a cartographer. Revolving doors, boards, who controls what |
| 8 | singularity | 🧠 Tech Singularity | Sonnet 4.6 | Understands scaling laws. Tracks compute, data, algorithmic improvements |
| 9 | psyops | 📡 Psyops & Propaganda | Sonnet 4.6 | Tracks narrative manufacturing. If 5 outlets say the same thing in 24h, it's coordinated |
| 10 | blackbudget | 🖤 Black Budget | Sonnet 4.6 | Pentagon audit failures. DARPA programs. Where did $2.3T go? |
| 11 | emerging | 🌍 Emerging Markets | Sonnet 4.6 | Lived on 3 continents. Sees opportunity where CNN sees chaos |
| 12 | regulatory | ⚖️ Regulatory Arbitrage | Sonnet 4.6 | Thinks in jurisdictions. Tracks loopholes and ungovernable structures |
| 13 | westeast | 🌏 West-East Arbitrage | Sonnet 4.6 | Bilingual. Reads Weibo and Twitter equally. Exploits the information gap |
| 14 | quant | 📈 Quant Researcher | Sonnet 4.6 | All markets. Funding rates, options flow, bonds, forex, commodities, cross-market signals |
| 15 | culture | 🎭 Culture & Virality | Sonnet 4.6 | Lives on TikTok, X, Reddit, Discord. Tracks Gen Z & unemployed — memes as emotional signals, viral products, unmet needs |

## Leadership

| Role | Model | Job |
|------|-------|-----|
| 🔮 Synthesis | Opus 4.6 | Reads all 15 researchers. Retries missing ones. Finds the pattern connecting everything. Tracks evolving meta-thesis. |
| 🧑‍🔬 Chief Scientist | Opus 4.6 | Reads everything. Challenges synthesis. Asks the uncomfortable question. Tracks predictions. Sends final briefing. |

## Memory System

Each agent maintains persistent memory across days:

**Researchers** — `memory/threads.md`
- Active story threads (max 5) tracking developing stories across days
- Stale rule: no movement in 5+ days → move to Resolved
- Read before searching. Updated after writing findings.

**Synthesis** — `synthesis/memory/thesis.md`
- Evolving meta-thesis (how the big picture is changing)
- Active predictions made + status tracking
- Read before synthesizing. Updated after writing.

**Chief Scientist** — `chief/memory/predictions.md` + `chief/memory/thesis.md`
- Prediction scoreboard (confirmed / wrong / pending)
- Critical risk register + contrarian positions
- Read before reviewing. Updated after writing.

## File Structure

```
intel-swarm/
├── README.md
├── ORG.md                          # Organization charter
├── researchers/
│   ├── <agent-id>/
│   │   ├── SOUL.md                 # Identity — who they are, how they think
│   │   ├── INSTRUCTIONS.md         # Methodology + memory protocol
│   │   ├── findings/
│   │   │   └── YYYY-MM-DD.md       # Daily findings
│   │   └── memory/
│   │       └── threads.md          # Ongoing story threads (persistent)
│   └── ... (15 researchers)
├── synthesis/
│   ├── SOUL.md
│   ├── INSTRUCTIONS.md
│   ├── findings/
│   │   └── YYYY-MM-DD.md           # Daily synthesis
│   └── memory/
│       └── thesis.md               # Evolving meta-thesis + predictions
├── chief/
│   ├── SOUL.md
│   ├── INSTRUCTIONS.md
│   ├── findings/
│   │   └── YYYY-MM-DD.md           # Daily chief scientist review
│   └── memory/
│       ├── predictions.md          # Prediction scoreboard
│       └── thesis.md               # Risk register + contrarian positions
├── agents.json                     # Agent config definitions
├── cron-ids.json                   # OpenClaw cron job IDs
└── create-crons.py                 # Script that created the cron jobs
```

## Anti-Sycophancy Rule

Researchers are explicitly allowed to file "nothing significant today" — a slow day is a valid and honest output. Manufacturing drama to hit 5 findings is worse than filing 2 real ones. This is enforced in every researcher's INSTRUCTIONS.md.

## Delivery

- Synthesis → Telegram DM to Vincent (07:15 HKT)
- Chief Scientist → Telegram DM to Vincent (07:45 HKT)
- Raw findings → stay in git (queryable, reviewable, diffable)

## Cost

~$2-3/day (15 Sonnet researchers + 2 Opus leadership)

## Built With

[OpenClaw](https://github.com/openclaw/openclaw) — cron jobs, web search, agent orchestration
