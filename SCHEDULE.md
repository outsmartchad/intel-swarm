# Intel Swarm — Daily Schedule

All times HKT (Asia/Hong_Kong). Runs every morning automatically via OpenClaw cron.

## Researcher Wave (06:00 – 07:10)

| Time HKT | Agent | Model | Timeout |
|----------|-------|-------|---------|
| 06:00 | 🪙 crypto | claude-sonnet-4-6 | 300s |
| 06:05 | 🤖 ai-agents | claude-sonnet-4-6 | 300s |
| 06:10 | 🕳️ conspiracy | claude-sonnet-4-6 | 300s |
| 06:15 | 📁 epstein | claude-sonnet-4-6 | 300s |
| 06:20 | ⚔️ war | claude-sonnet-4-6 | 300s |
| 06:25 | 📊 macro | claude-sonnet-4-6 | 300s |
| 06:30 | 🕴️ power | claude-sonnet-4-6 | 300s |
| 06:35 | 🧠 singularity | claude-sonnet-4-6 | 300s |
| 06:40 | 📡 psyops | claude-sonnet-4-6 | 300s |
| 06:45 | 🖤 blackbudget | claude-sonnet-4-6 | 300s |
| 06:50 | 🌍 emerging | claude-sonnet-4-6 | 300s |
| 06:55 | ⚖️ regulatory | claude-sonnet-4-6 | 300s |
| 07:00 | 🌏 westeast | claude-sonnet-4-6 | 300s |
| 07:05 | 📈 quant | claude-sonnet-4-6 | 300s |
| 07:10 | 🎭 culture | claude-sonnet-4-6 | 300s |

## Leadership (07:15 – 07:45)

| Time HKT | Agent | Model | Timeout |
|----------|-------|-------|---------|
| 07:15 | 🔮 synthesis | claude-opus-4-6 | 900s |
| 07:45 | 🧑‍🔬 chief | claude-opus-4-6 | 600s |

## Notes

- **Memory first:** Every agent reads its memory files before searching/writing
- **Escalation:** Any researcher can send a 🚨 ALERT to Telegram immediately if finding is time-critical (don't wait for 07:45)
- **Anti-sycophancy:** "Nothing significant today" is a valid output — slow days are reported honestly
- **Source tracking:** Researchers log source quality to `memory/sources.md` after each run
- **Thread hygiene:** Max 5 active threads per researcher, stale after 5 days with no movement
- **Git:** All findings committed to repo after each run
- **Delivery:** Synthesis → Telegram (07:15). Chief → Telegram (07:45). Raw findings → git only.
