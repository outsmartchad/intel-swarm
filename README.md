# Intel Swarm — Vincent's Research Org

Private intelligence research team. 15 specialist agents + synthesis + chief scientist.
Purpose: generate banger ideas for next-generation products.

Inspired by Karpathy's multi-agent research org architecture.

## Structure
- Each researcher works in their own git worktree (`worktrees/<agent-id>/`)
- Each worktree has its own branch (`researcher/<agent-id>`)
- Communication via simple markdown files
- Synthesis agent reads all worktrees, merges signals
- Chief scientist challenges synthesis conclusions

## Agents
| ID | Name | Branch |
|----|------|--------|
| crypto | Crypto Researcher | researcher/crypto |
| ai-agents | AI Agents Researcher | researcher/ai-agents |
| conspiracy | Conspiracy Researcher | researcher/conspiracy |
| epstein | Epstein Deep State Researcher | researcher/epstein |
| war | War Researcher | researcher/war |
| macro | Macro Economist | researcher/macro |
| power | Power Structures Researcher | researcher/power |
| singularity | Tech Singularity Researcher | researcher/singularity |
| psyops | Psyops Propaganda Researcher | researcher/psyops |
| blackbudget | Black Budget Researcher | researcher/blackbudget |
| emerging | Emerging Markets Researcher | researcher/emerging |
| regulatory | Regulatory Arbitrage Researcher | researcher/regulatory |
| westeast | West-East Arbitrage Researcher | researcher/westeast |
| onchain | Onchain Researcher | researcher/onchain |
| quant | Quant Researcher | researcher/quant |

## Daily Flow
```
22:00 HKT — 15 researchers write to their worktrees
23:00 HKT — Synthesis reads all worktrees, writes synthesis/YYYY-MM-DD.md
23:30 HKT — Chief Scientist reviews synthesis, sends final briefing to Vincent
```

## Comms Protocol
- Researchers write: `worktrees/<id>/findings/YYYY-MM-DD.md`
- Synthesis writes: `synthesis/YYYY-MM-DD.md`
- Chief Scientist writes: `chief/YYYY-MM-DD.md` + sends Telegram
