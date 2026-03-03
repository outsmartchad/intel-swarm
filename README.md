# 🐝 Intel Swarm

Private intelligence research org for Vincent. 15 AI researchers + synthesis + chief scientist.

> **Purpose:** Feed high-signal, under-reported intel across 15 domains daily. Not news — EDGE. Information that 99% don't know, don't want to know, or can't connect.

> **Inspired by:** [Karpathy's multi-agent research org](https://x.com/karpathy) — "You are now programming an organization. The source code is prompts, skills, tools, and processes."

## Architecture

```
06:00 HKT ─── 15 Researchers fire sequentially (3 min apart)
                │
                ├── researchers/crypto/findings/YYYY-MM-DD.md      (06:00)
                ├── researchers/ai-agents/findings/YYYY-MM-DD.md   (06:03)
                ├── researchers/conspiracy/findings/YYYY-MM-DD.md  (06:06)
                ├── ... (15 total, last at 06:42)
                │
07:00 HKT ─── Synthesis Agent reads all 15 → connects dots
                │  (retries any missing researchers before synthesizing)
                │
                └── synthesis/YYYY-MM-DD.md
                │
07:30 HKT ─── Chief Scientist reads ALL raw findings + synthesis → challenges everything
                │
                └── chief/YYYY-MM-DD.md → Telegram briefing to Vincent
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
| 🔮 Synthesis | Opus 4.6 | Reads all 15 researchers. Retries missing ones. Finds the pattern connecting everything |
| 🧑‍🔬 Chief Scientist | Opus 4.6 | Reads everything. Challenges synthesis. Asks the uncomfortable question. Sends final briefing |

## File Structure

```
intel-swarm/
├── README.md
├── ORG.md                          # Organization charter
├── researchers/
│   ├── <agent-id>/
│   │   ├── SOUL.md                 # Identity — who they are, how they think
│   │   ├── INSTRUCTIONS.md         # Methodology — what to search, what counts
│   │   ├── AGENT.md                # Branch info
│   │   └── findings/
│   │       └── YYYY-MM-DD.md       # Daily findings
│   └── ... (15 researchers)
├── synthesis/
│   ├── SOUL.md
│   └── YYYY-MM-DD.md               # Daily synthesis
├── chief/
│   ├── SOUL.md
│   └── YYYY-MM-DD.md               # Daily chief scientist review
├── agents.json                     # Agent config definitions
├── cron-ids.json                   # OpenClaw cron job IDs
└── create-crons.py                 # Script that created the cron jobs
```

## Each Researcher Has

- **SOUL.md** — Identity, personality, lens, anti-patterns
- **INSTRUCTIONS.md** — Search strategy, what counts as a finding, what doesn't
- **findings/** — Daily output, one file per day

## Delivery

- Synthesis → Telegram DM to Vincent
- Chief Scientist → Telegram DM to Vincent
- Raw findings → stay in git (queryable, reviewable, diffable)

## Cost

~$2-3/day (15 Sonnet researchers + 2 Opus leadership)

## Built With

[OpenClaw](https://github.com/openclaw/openclaw) — cron jobs, web search, agent orchestration
