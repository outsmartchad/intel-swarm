# 🐝 Intel Swarm

> Daily intelligence briefings across 15+ domains — AI, Crypto, War, Macro, Geopolitics, Health, Religion, Commodities & more. Signal over noise.

**Live:** [intel-swarm.vercel.app](https://intel-swarm.vercel.app)

---

## What is this?

Intel Swarm is an autonomous AI-powered intelligence network. A swarm of specialized researcher agents scrape, analyze, and synthesize the web daily — delivering high-signal briefings that 99% of people miss.

Each morning:
1. **15+ researcher agents** run in parallel across domains
2. **Synthesis agent** connects the dots across all findings
3. **Chief analyst** delivers the final actionable briefing
4. Everything is **translated to Traditional Chinese** automatically
5. Published to the web and delivered via Telegram

---

## Domains

| Domain | Focus |
|--------|-------|
| ⚔️ War | Active conflicts, geopolitical flashpoints, military movements |
| 🛢️ Commodities | Gold, oil, copper, rare earths, supply chains |
| 🔴 Communist States | Russia 🇷🇺 · China 🇨🇳 · North Korea 🇰🇵 |
| ✝️ Religion | Religious nationalism, Vatican, AI & faith |
| 🧬 Health | Biotech, longevity, pandemics, AI diagnostics |
| 🎭 Culture | Gen Z, virality, social movements |
| 🌍 Emerging | Southeast Asia, Africa, LatAm opportunities |
| 🤖 AI Agents | Autonomous AI, frameworks, agentic products |
| 🪙 Crypto | DeFi, Solana, on-chain signals |
| 📊 Macro | Fed, BRICS, debt, currency wars |
| 🧠 Singularity | AGI timelines, compute wars |
| 📈 Quant | Market signals, volatility |
| 🌏 West-East | China/HK signals the West misses |
| 🖤 Black Budget | DARPA, CIA, UAP disclosure |
| 🕳️ Conspiracy | Mainstream-bound narratives |
| 📁 Epstein | Files, court docs, elite networks |
| 🏆 Sports | Business side of sports |

---

## Stack

- **Agents:** [OpenClaw](https://openclaw.ai) — AI agent platform running cron jobs
- **Models:** Claude Sonnet 4.6 for research, Claude Haiku for translation
- **Web:** Python / Flask, deployed on Vercel
- **Images:** OG image scraping from source URLs
- **Languages:** English + Traditional Chinese (繁體中文)

---

## Setup

### Prerequisites
- [OpenClaw](https://openclaw.ai) installed and configured
- Vercel account + CLI (`npm i -g vercel`)
- Claude API access via OpenClaw

### 1. Clone & install
```bash
git clone https://github.com/outsmartchad/intel-swarm
cd intel-swarm
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env with your Telegram user ID and paths
```

### 3. Create all researcher crons
```bash
# Set your Telegram user ID
export TELEGRAM_USER_ID=your_telegram_id

python3 create-crons.py
```

### 4. Run locally
```bash
cd web && python3 server.py
# Open http://localhost:5757
```

### 5. Deploy to Vercel
```bash
vercel deploy --prod
```

---

## Daily Pipeline

```
06:00 HKT  →  15+ researchers run in parallel
07:00 HKT  →  Synthesis + Chief briefing
07:45 HKT  →  Chief delivers Telegram briefing
08:00 HKT  →  Autopush: copy → translate → scrape images → git push → vercel deploy
```

---

## Project Structure

```
intel-swarm/
├── researchers/          # Per-domain researcher agents
│   ├── {domain}/
│   │   ├── findings/     # Daily MD files (EN + ZH)
│   │   └── memory/       # Persistent threads & sources
├── synthesis/            # Synthesis agent
├── chief/                # Chief analyst agent
├── web/                  # Flask web server
│   ├── server.py
│   ├── templates/
│   ├── static/
│   ├── translate.py      # EN → ZH translation
│   ├── scrape-images.py  # OG image scraper
│   └── translate-all.sh  # Batch translation
├── create-crons.py       # Spin up all OpenClaw crons
└── .env.example          # Config template
```

---

## Contributing

Intel Swarm is designed to be extended. You can:
- **Add new research domains** — new topic, new researcher, automatic pipeline integration
- **Refine researcher prompts** — tune search queries, source preferences, output format
- **Modify synthesis/chief logic** — change how findings are connected and delivered
- **Add sub-domain tabs** — group related topics (e.g. Russia / China / North Korea under Communist States)

Full guide: **[CONTRIBUTING.md](./CONTRIBUTING.md)** · **[中文說明 CONTRIBUTING.zh.md](./CONTRIBUTING.zh.md)**

---

## License

MIT — fork it, build on it, run your own swarm.

---

*Built with [OpenClaw](https://openclaw.ai)*
