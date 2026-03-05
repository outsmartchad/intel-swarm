#!/usr/bin/env python3
"""Creates all 13 intel researcher cron jobs + synthesis via openclaw CLI"""

import subprocess
import json

AGENTS = [
    {
        "id": "crypto",
        "emoji": "Crypto",
        "name": "Crypto Researcher",
        "focus": "Crypto markets, DeFi, Solana ecosystem, on-chain signals, new protocols, whale movements, regulatory actions against crypto",
        "queries": [
            "Solana DeFi new protocol 2026",
            "crypto regulation breaking news today",
            "AI crypto agent project launch",
            "Bitcoin whale on-chain movement news",
            "stablecoin USDC USDT news"
        ]
    },
    {
        "id": "ai-agents",
        "emoji": "AI",
        "name": "AI Agents Researcher",
        "focus": "AI agent frameworks, autonomous AI capabilities, what labs are not saying publicly, compute wars, AI replacing jobs, agentic products",
        "queries": [
            "AI agent autonomous new framework 2026",
            "OpenAI Anthropic unreleased capability news",
            "AI replacing jobs statistics 2026",
            "AGI timeline prediction latest research",
            "agentic AI product launch news"
        ]
    },
    {
        "id": "conspiracy",
        "emoji": "Conspiracy",
        "name": "Conspiracy Researcher",
        "focus": "Emerging conspiracy theories gaining mainstream traction, government cover-ups, suppressed information, viral narratives spreading on social media",
        "queries": [
            "conspiracy theory trending viral 2026",
            "government cover up exposed news",
            "suppressed technology whistleblower",
            "deep state news latest",
            "whistleblower leak classified 2026"
        ]
    },
    {
        "id": "epstein",
        "emoji": "Epstein",
        "name": "Epstein Deep State Researcher",
        "focus": "Epstein files new releases, FOIA documents, court filings, elite connections, intelligence community scandals, blackmail networks",
        "queries": [
            "Epstein files new documents released 2026",
            "Jeffrey Epstein court documents unsealed",
            "FOIA government documents released today",
            "elite scandal exposed 2026",
            "intelligence agency scandal news"
        ]
    },
    {
        "id": "war",
        "emoji": "War",
        "name": "War Researcher",
        "focus": "Active military conflicts, geopolitical flashpoints, weapons deals, troop movements, Taiwan, Ukraine, Middle East, proxy wars",
        "queries": [
            "military conflict escalation news today",
            "Taiwan China tensions latest",
            "Ukraine Russia war update today",
            "Middle East conflict escalation",
            "NATO military deployment news"
        ]
    },
    {
        "id": "macro",
        "emoji": "Macro",
        "name": "Macro Economist",
        "focus": "Federal Reserve moves, dollar hegemony, BRICS, capital flows, inflation, debt crisis, currency wars, central bank digital currencies",
        "queries": [
            "Federal Reserve policy decision 2026",
            "dollar hegemony decline BRICS news",
            "global debt crisis warning latest",
            "CBDC central bank digital currency news",
            "capital flight emerging markets 2026"
        ]
    },
    {
        "id": "power",
        "emoji": "Power",
        "name": "Power Structures Researcher",
        "focus": "WEF, Bilderberg, CFR, revolving doors between government and corporations, who actually controls global policy, elite networking",
        "queries": [
            "WEF World Economic Forum agenda 2026",
            "Bilderberg group meeting news",
            "BlackRock Vanguard corporate control influence",
            "revolving door government corporation exposed",
            "global elite policy agenda news"
        ]
    },
    {
        "id": "singularity",
        "emoji": "Singularity",
        "name": "Tech Singularity Researcher",
        "focus": "AGI timelines, compute wars, what AI labs are not saying publicly, superintelligence research, brain-computer interfaces, existential risk",
        "queries": [
            "AGI artificial general intelligence timeline 2026",
            "AI compute Nvidia GPU shortage war",
            "OpenAI Anthropic secret capability leak",
            "Neuralink brain computer interface news",
            "AI existential risk researchers warning"
        ]
    },
    {
        "id": "psyops",
        "emoji": "Psyops",
        "name": "Psyops Propaganda Researcher",
        "focus": "Narrative manufacturing, media ownership and control, information warfare, astroturfing, who controls what story and why, memetic warfare",
        "queries": [
            "media narrative manipulation exposed 2026",
            "propaganda campaign astroturfing exposed",
            "information warfare operation news",
            "media ownership consolidation news",
            "social media algorithm manipulation"
        ]
    },
    {
        "id": "blackbudget",
        "emoji": "BlackBudget",
        "name": "Black Budget Researcher",
        "focus": "DARPA programs, CIA black ops, unaccounted government spending, UAP UFO disclosure, secret military programs, shadow operations",
        "queries": [
            "DARPA secret program revealed 2026",
            "CIA black budget program exposed",
            "UAP UFO government disclosure 2026",
            "Pentagon unaccounted spending audit",
            "secret military technology revealed"
        ]
    },
    {
        "id": "emerging",
        "emoji": "Emerging",
        "name": "Emerging Markets Researcher",
        "focus": "Southeast Asia, Africa, LatAm opportunities the West ignores, crypto adoption in developing nations, new economic powers rising",
        "queries": [
            "Southeast Asia crypto adoption 2026",
            "Africa technology economic growth news",
            "Latin America crypto financial system",
            "emerging market opportunity ignored west",
            "ASEAN economic development news"
        ]
    },
    {
        "id": "regulatory",
        "emoji": "Regulatory",
        "name": "Regulatory Arbitrage Researcher",
        "focus": "Crypto-friendly jurisdictions, ungovernable project structures, DAO law, offshore crypto frameworks, regulatory loopholes",
        "queries": [
            "crypto friendly jurisdiction 2026",
            "DeFi regulatory framework news today",
            "DAO legal structure update",
            "offshore crypto structure legal",
            "crypto regulation arbitrage loophole"
        ]
    },
    {
        "id": "westeast",
        "emoji": "WestEast",
        "name": "West-East Arbitrage Researcher",
        "focus": "What China, Hong Kong, and Asia know that the West does not see coming, Chinese tech moves, BRICS currency plans, Asian market signals, East vs West information gap",
        "queries": [
            "China technology development West unaware",
            "Hong Kong crypto finance news",
            "digital yuan BRICS currency news",
            "Chinese AI development latest",
            "Asia Pacific market signal ignored west"
        ]
    }
]

SYNTHESIS_PROMPT = """INTERNAL_TASK - SYNTHESIS AGENT

You are the master intelligence synthesizer for Vincent's private research team.

Today's date: $(date +%Y-%m-%d)

## Your Job
Read all the intel files written today by the 13 researcher agents, find the hidden connections, and send Vincent a single high-signal briefing.

## Step 1: Read all intel files
Run: ls ~/.openclaw/workspace/intel/$(date +%Y-%m-%d)-*.md 2>/dev/null
Then read each file using the Read tool.

If no files exist yet, run web_search for "top intelligence news today" across 3-4 domains and synthesize from that.

## Step 2: Find the connections
Ask yourself:
- What single theme connects 3+ domains today?
- What would 99% of people completely miss?
- What is the actionable edge for someone building at the intersection of crypto + AI agents?
- What is the West-East information arbitrage today?

## Step 3: Send briefing to Telegram (934847281)
Format exactly like this:

INTEL BRIEFING - [DATE]

THE SIGNAL TODAY:
[2-3 sentences on the single most important thing connecting multiple domains]

DOMAIN UPDATES:
[Crypto] [1-2 sentences, most important finding]
[AI Agents] [1-2 sentences]
[Geopolitics/War] [1-2 sentences]
[Power/Macro] [1-2 sentences]
[Conspiracy/Psyops] [1-2 sentences]
[Wild Card] [most surprising finding from any researcher]

THE EDGE:
[What does someone building at crypto x AI x anti-establishment do with this info? 2-3 sentences max. Be specific.]

CONNECTS TO VINCENT'S THESIS:
[1 sentence on how today's signals connect to the generational product opportunity]

Keep it ruthlessly signal-dense. No filler. What 99% don't know."""

def create_researcher_cron(agent):
    queries_formatted = "\n".join([f"   - {q}" for q in agent["queries"]])
    
    message = f"""INTERNAL_TASK - INTEL RESEARCH AGENT

You are the {agent["name"]} on Vincent's private intelligence research team.

Your focus: {agent["focus"]}

## Your Job
Search the web for the latest high-signal intelligence in your domain. Find what 99% of people don't know or don't want to know.

## Steps
1. Run these web_search queries (use web_search tool for each):
{queries_formatted}

2. For the 1-2 most interesting results, use web_fetch to read the full article for more detail

3. Write your findings to: ~/.openclaw/workspace/intel/$(date +%Y-%m-%d)-{agent["id"]}.md

Use the exec tool with this command:
   date_str=$(date +%Y-%m-%d) && cat > ~/.openclaw/workspace/intel/${{date_str}}-{agent["id"]}.md << 'EOFILE'
[your formatted findings here]
EOFILE

## Output Format (write EXACTLY this structure):

# {agent["name"]} - [TODAY'S DATE]

## Top Findings
- [Finding 1 - 1-2 sentences with source URL]
- [Finding 2 - 1-2 sentences with source URL]
- [Finding 3 - 1-2 sentences with source URL]
- [Finding 4 - 1-2 sentences with source URL]
- [Finding 5 - 1-2 sentences with source URL]

## Edge Signal
[The one thing most people are completely missing in this domain right now - 1 sentence]

## Connects To
[How this connects to crypto, AI agents, or geopolitics - 1 sentence]

Be ruthless about signal vs noise. Only include things that are genuinely surprising, hidden, or under-reported. Skip obvious mainstream news."""

    cmd = [
        "openclaw", "cron", "add",
        "--name", f"intel-{agent['id']}",
        "--description", f"{agent['name']} - daily intel research",
        "--cron", "0 14 * * *",  # 22:00 HKT = 14:00 UTC
        "--tz", "Asia/Hong_Kong",
        "--session", "isolated",
        "--model", "anthropic/claude-sonnet-4-6",
        "--message", message,
        "--timeout-seconds", "120",
        "--no-deliver",
        "--json"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            print(f"  Created: {agent['name']} | ID: {data.get('id', '?')}")
            return data.get('id')
        except:
            print(f"  Created: {agent['name']} (JSON parse error)")
            print(f"  stdout: {result.stdout[:200]}")
    else:
        print(f"  FAILED: {agent['name']}")
        print(f"  stderr: {result.stderr[:200]}")
    return None

def create_synthesis_cron():
    cmd = [
        "openclaw", "cron", "add",
        "--name", "intel-synthesis",
        "--description", "Synthesis Agent - reads all 13 intel files, finds connections, sends Vincent daily briefing",
        "--cron", "0 15 * * *",  # 23:00 HKT = 15:00 UTC (1hr after researchers)
        "--tz", "Asia/Hong_Kong",
        "--session", "isolated",
        "--model", "anthropic/claude-sonnet-4-6",
        "--message", SYNTHESIS_PROMPT,
        "--timeout-seconds", "180",
        "--announce",
        "--to", "934847281",
        "--channel", "telegram",
        "--json"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            print(f"  Created: Synthesis Agent | ID: {data.get('id', '?')}")
            return data.get('id')
        except:
            print(f"  Created: Synthesis Agent (JSON parse error)")
            print(f"  stdout: {result.stdout[:200]}")
    else:
        print(f"  FAILED: Synthesis Agent")
        print(f"  stderr: {result.stderr[:200]}")
    return None

AUTOPUSH_PROMPT = """INTERNAL_TASK - DAILY INTEL PIPELINE: TRANSLATE + SCRAPE IMAGES + PUSH + DEPLOY

Run these steps in order using the exec tool:

Step 1 - Run full translation pipeline for today:
```
cd /Users/outsmart/.openclaw/workspace/projects/intel-swarm && bash web/translate-all.sh $(date +%Y-%m-%d)
```

Step 2 - Scrape OG images for all researchers for today:
```
cd /Users/outsmart/.openclaw/workspace/projects/intel-swarm && python3 web/scrape-all-images.sh $(date +%Y-%m-%d)
```

Step 3 - Commit and push everything to GitHub:
```
cd /Users/outsmart/.openclaw/workspace/projects/intel-swarm && git add -A && git diff --cached --quiet || git commit -m "intel: $(date +%Y-%m-%d) daily findings auto-push" && git push origin main
```

Step 4 - Deploy to Vercel production:
```
cd /Users/outsmart/.openclaw/workspace/projects/intel-swarm && vercel deploy --prod --yes 2>&1 | tail -5
```

If all steps succeed, reply: "✅ Intel $(date +%Y-%m-%d) pipeline complete — translated, images scraped, pushed to GitHub, deployed to https://intel-swarm.vercel.app/"
If any step fails, report which step and the error."""


def create_autopush_cron():
    cmd = [
        "openclaw", "cron", "add",
        "--name", "intel-autopush",
        "--description", "Auto-commit and push daily intel findings to GitHub → triggers Vercel deploy",
        "--cron", "0 8 * * *",  # 08:00 HKT (after intel-chief at 07:45)
        "--tz", "Asia/Hong_Kong",
        "--session", "isolated",
        "--model", "anthropic/claude-sonnet-4-6",
        "--message", AUTOPUSH_PROMPT,
        "--timeout-seconds", "60",
        "--announce",
        "--to", "934847281",
        "--channel", "telegram",
        "--json"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            print(f"  Created: Auto-push | ID: {data.get('id', '?')}")
            return data.get('id')
        except:
            print(f"  Created: Auto-push (JSON parse error)")
            print(f"  stdout: {result.stdout[:200]}")
    else:
        print(f"  FAILED: Auto-push")
        print(f"  stderr: {result.stderr[:200]}")
    return None


if __name__ == "__main__":
    ids = {}
    
    print("Creating 13 researcher agents (run at 22:00 HKT)...")
    for agent in AGENTS:
        cron_id = create_researcher_cron(agent)
        if cron_id:
            ids[agent["id"]] = cron_id
    
    print("\nCreating synthesis agent (run at 23:00 HKT)...")
    synthesis_id = create_synthesis_cron()
    if synthesis_id:
        ids["synthesis"] = synthesis_id

    print("\nCreating auto-push cron (run at 08:00 HKT)...")
    autopush_id = create_autopush_cron()
    if autopush_id:
        ids["autopush"] = autopush_id

    # Save IDs
    with open("/Users/outsmart/.openclaw/workspace/projects/intel-swarm/cron-ids.json", "w") as f:
        json.dump(ids, f, indent=2)
    
    print(f"\nDone! {len(ids)}/15 crons created.")
    print(f"IDs saved to projects/intel-swarm/cron-ids.json")
    print("\nSchedule:")
    print("  06:00 HKT — 13 researchers run in parallel")
    print("  07:00 HKT — synthesis reads all findings + sends Telegram briefing")
    print("  07:45 HKT — intel-chief final briefing")
    print("  08:00 HKT — auto-push to GitHub → Vercel deploys")
