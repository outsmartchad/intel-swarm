# 🐝 Intel Swarm

> Autonomous AI intelligence research across 19 domains — War, Crypto, Macro, AI Agents, Communist States, Health, Religion, Commodities & more. Signal over noise.

**Live:** [intel-swarm.vercel.app](https://intel-swarm.vercel.app) · **[繁體中文](https://intel-swarm.vercel.app/?lang=zh)**

---

## What is this?

Intel Swarm is an autonomous intelligence research team. A swarm of specialized AI researcher agents scrape, analyze, and synthesize the web daily — delivering high-signal briefings across 19 domains in English and Traditional Chinese.

Each morning:
1. **19 researcher agents** run in parallel across domains (06:00–07:45 HKT)
2. **Synthesis agent** connects the dots across all findings
3. **Chief analyst** delivers the final actionable briefing
4. Everything is **translated to Traditional Chinese** automatically
5. Published to the web at **08:00 HKT** via automated git push + Vercel deploy
6. **Breaking intel** is continuously monitored and pushed to Telegram every 2 hours

---

## Domains

| Domain | Focus |
|--------|-------|
| ⚔️ War | Active conflicts, geopolitical flashpoints, military movements |
| 🛢️ Commodities | Gold, oil, copper, rare earths, supply chains, chokepoints |
| 🔴 Communist States | Russia 🇷🇺 · China 🇨🇳 · North Korea 🇰🇵 |
| ✝️ Religion | Religious nationalism, Vatican, faith & geopolitics |
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

## Features

### 🗞️ Daily Intelligence Feed
- Hero banner with top signal of the day
- Card grid with OG images, scores, and domain tags
- Grid / Feed toggle view
- Full bilingual support — EN + Traditional Chinese (繁體中文)
- Date selector to browse historical intel

### 📊 Polymarket Overlay
- Hover any finding to see live Polymarket prediction market odds
- Corner overlay with real-time probability chart
- Domain-aware matching — only causal, relevant markets shown
- Click to pin; "View on Polymarket ↗" direct link
- Toggle on/off via the **P** button in the header

### 🌍 Conflict Heat Map (`/conflict`)
- Interactive Leaflet map with intel findings as live pins
- GDELT event data as background heat layer
- Filter by domain: War · Politics · Intel · Culture
- Fully bilingual (EN/ZH labels, finding titles, domain names)

### ⚡ Bloomberg Terminal (`/terminal`)
- Bloomberg-style dark feed of all findings across all domains
- Domain filter panel (left) + findings feed (right)
- Ticker tags: `$BTC` `$ETH` `$SOL` `OIL` `GOLD` `DXY` `BONDS` `SPX` `NVDA` `TSLA` `DEFENSE` + more
- Signal strength pips, real-time search
- Built-in API docs modal

### 🔌 Public API v1
Free, no auth required. Base URL: `https://intel-swarm.vercel.app`

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/domains` | List all research domains |
| `GET /api/v1/findings` | All findings (filter by `date`, `domain`, `lang`, `limit`, `ticker`) |
| `GET /api/v1/feed` | Score-sorted feed across all domains |
| `GET /api/v1/brief` | Latest chief analyst brief |
| `GET /api/v1/search?q=` | Full-text search across findings |

### 📡 RSS Feeds
- `GET /rss` — Global feed (all domains, 50 items)
- `GET /rss/<domain>` — Domain-specific feed

### 📲 Breaking Intel Push
- Scans for new findings every 2 hours
- Formats Telegram messages with ticker tags and source links
- Requires `TG_PUSH_BOT_TOKEN` + `TG_PUSH_CHANNEL_ID` env vars

### 🌙 Light / Dark Mode
- Toggle via ☀️/🌙 button in the header
- Persists across sessions via `localStorage`

---

## Stack

- **Agents:** [OpenClaw](https://openclaw.ai) — AI agent platform running cron jobs
- **Models:** Claude Opus 4.6 (synthesis & chief), Claude Sonnet 4.6 (domain research), Claude Haiku (translation)
- **Web:** Python / Flask, deployed on Vercel
- **Map:** Leaflet.js + GDELT 2.0 CSV feed
- **Prediction Markets:** Polymarket Gamma API + CLOB API
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
# Edit .env — see .env.example for all required variables
```

### 3. Create all researcher crons
```bash
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
vercel deploy --prod --yes
```

> ⚠️ This project uses a legacy `builds` config in `vercel.json`. GitHub pushes alone do **not** trigger Vercel redeploys — always use `vercel deploy --prod --yes`.

---

## Daily Pipeline

```
06:00 HKT  →  19 researchers run in parallel across domains
07:00 HKT  →  Synthesis + Chief briefing generated
07:45 HKT  →  Chief delivers Telegram briefing
08:00 HKT  →  Autopush: copy → translate → scrape images → git push → vercel deploy
Every 2h   →  Breaking intel scan → Telegram push
```

---

## Project Structure

```
intel-swarm/
├── researchers/            # Per-domain researcher agents
│   └── {domain}/
│       ├── findings/       # Daily MD files (EN + ZH)
│       └── memory/         # Persistent threads & sources
├── synthesis/              # Synthesis agent
├── chief/                  # Chief analyst agent
├── web/
│   ├── server.py           # Flask app — all routes, API, RSS, Terminal, Conflict
│   ├── templates/
│   │   ├── base.html       # Masthead, nav, theme, Polymarket overlay
│   │   ├── index.html      # Homepage — hero, grid, feed toggle
│   │   ├── domain.html     # Domain page with sub-tabs + findings
│   │   ├── conflict.html   # Leaflet conflict heat map
│   │   └── terminal.html   # Bloomberg-style terminal
│   ├── static/
│   │   ├── conflict-events.json   # GDELT heat layer data
│   │   └── push-state.json        # Breaking intel push state
│   ├── translate.py         # EN → Traditional Chinese translation
│   ├── scrape-images.py     # OG image scraper
│   ├── prefetch-polymarket.py    # Polymarket market prefetch pipeline
│   ├── prefetch-conflict.py      # GDELT CSV fetch + parse pipeline
│   ├── push-breaking.py          # Breaking intel Telegram push
│   ├── translate-all.sh          # Batch translate all domains
│   └── scrape-all-images.sh      # Batch image scrape all domains
├── docs/
│   ├── worldmonitor-api-intelligence.md     # API source catalogue (EN)
│   └── worldmonitor-api-intelligence.zh.md  # API source catalogue (ZH)
├── create-crons.py          # Spin up all OpenClaw crons
├── .env.example             # Config template
├── CONTRIBUTING.md
└── CONTRIBUTING.zh.md
```

---

## API Reference

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BRAVE_API_KEY` | ✅ | Brave Search API key for researchers |
| `TELEGRAM_USER_ID` | ✅ | Your Telegram user ID for briefings |
| `TG_PUSH_BOT_TOKEN` | Optional | Bot token for breaking intel channel push |
| `TG_PUSH_CHANNEL_ID` | Optional | Channel ID for breaking intel push |

See `.env.example` for full list.

---

## Contributing

Intel Swarm is designed to be extended. You can:
- **Add new research domains** — new topic, new researcher, automatic pipeline integration
- **Refine researcher prompts** — tune search queries, source preferences, output format
- **Modify synthesis/chief logic** — change how findings are connected and delivered
- **Add sub-domain tabs** — group related topics (e.g. Russia / China / North Korea under Communist States)
- **Integrate new data APIs** — see [`docs/worldmonitor-api-intelligence.md`](./docs/worldmonitor-api-intelligence.md) for 31 catalogued free APIs

Full guide: **[CONTRIBUTING.md](./CONTRIBUTING.md)** · **[中文說明 CONTRIBUTING.zh.md](./CONTRIBUTING.zh.md)**

---

## License

MIT — fork it, build on it, run your own swarm.

---

*Built with [OpenClaw](https://openclaw.ai) · Last updated: 2026-03-05*
