# Intel Swarm — Daily Schedule

All times in HKT (Asia/Hong_Kong). Runs every morning.

| Time | Agent | Model | Timeout |
|------|-------|-------|---------|
| 06:00 | crypto | claude-sonnet-4-6 | 300s |
| 07:00 | westeast | claude-sonnet-4-6 | 300s |
| 06:10 | conspiracy | claude-sonnet-4-6 | 300s |
| 07:10 | culture | claude-sonnet-4-6 | 300s |
| 06:15 | epstein | claude-sonnet-4-6 | 300s |
| 07:15 | synthesis | claude-opus-4-6 | 900s |
| 06:20 | war | claude-sonnet-4-6 | 300s |
| 06:25 | macro | claude-sonnet-4-6 | 300s |
| 06:30 | power | claude-sonnet-4-6 | 300s |
| 06:35 | singularity | claude-sonnet-4-6 | 300s |
| 06:40 | psyops | claude-sonnet-4-6 | 300s |
| 06:45 | blackbudget | claude-sonnet-4-6 | 300s |
| 07:45 | chief | claude-opus-4-6 | 180s |
| 06:05 | ai-agents | claude-sonnet-4-6 | 300s |
| 07:05 | quant | claude-sonnet-4-6 | 300s |
| 06:50 | emerging | claude-sonnet-4-6 | 300s |
| 06:55 | regulatory | claude-sonnet-4-6 | 300s |

## Notes
- Researchers run sequentially (5 min apart) to avoid API rate limits
- Synthesis retries any missing researchers before synthesizing
- Chief scientist has 30 min buffer after synthesis
- All agents send findings to Telegram (934847281)
- All agents commit findings to this repo
