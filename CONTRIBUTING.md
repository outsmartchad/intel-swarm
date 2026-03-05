# Contributing to Intel Swarm

Intel Swarm is designed to be fully extensible. You can add new research domains, refine existing researcher prompts, and tune the synthesis/chief logic — no code changes required for most customizations.

---

## 🌐 Adding a New Domain

### Step 1 — Create the researcher folder

```bash
mkdir -p researchers/{your-domain}/{findings,memory}
echo "# Your Domain — Active Threads" > researchers/{your-domain}/memory/threads.md
echo "# Your Domain — Sources" > researchers/{your-domain}/memory/sources.md
```

### Step 2 — Add it to the web server

Open `web/server.py` and add your domain to the `RESEARCHERS` list:

```python
RESEARCHERS = [
    ...
    {"id": "your-domain", "emoji": "🔍", "name": "Your Domain", "zh": "你的領域", "colors": "#1a1a2e,#e94560"},
    ...
]
```

**Color tips:** Use two hex colors (dark → accent) for the card gradient. Pick something visually distinct from existing domains.

### Step 3 — Create the researcher cron

```bash
openclaw cron add \
  --name "intel-your-domain" \
  --description "Your Domain Researcher - daily intel on ..." \
  --cron "X 6 * * *" \
  --tz "Asia/Hong_Kong" \
  --session "isolated" \
  --model "anthropic/claude-sonnet-4-6" \
  --message "$(cat researchers/your-domain/INSTRUCTIONS.md)" \
  --timeout-seconds 120 \
  --no-deliver
```

Stagger the minute offset (pick an unused minute between 0–59) to avoid all crons running simultaneously.

### Step 4 — Write the researcher prompt

Create `researchers/{your-domain}/INSTRUCTIONS.md`:

```markdown
INTERNAL_TASK - INTEL RESEARCH AGENT

You are the {Your Domain} Researcher on a private intelligence research team.

Your focus: [Describe exactly what signals to track — be specific]

## Steps
1. Run these web_search queries:
   - [query 1]
   - [query 2]
   - [query 3]
   - [query 4]
   - [query 5]

2. For the most interesting results, use web_fetch to read the full article

3. Write to: ~/.openclaw/workspace/intel/$(date +%Y-%m-%d)-{your-domain}.md

## Output Format
# {Your Domain} Researcher - [DATE]

## Top Findings
- **[Title]** — [1-2 sentences, source URL]
- **[Title]** — [1-2 sentences, source URL]
- **[Title]** — [1-2 sentences, source URL]
- **[Title]** — [1-2 sentences, source URL]
- **[Title]** — [1-2 sentences, source URL]

## Edge Signal
[1 sentence: what most people are missing in this domain right now]

## Connects To
[1 sentence: how this connects to other domains]

Do NOT add status labels like CONFIRMED, UNCONFIRMED, or emoji indicators. Write findings directly.
```

### Step 5 — Add to the pipeline scripts

Add your domain to `web/translate-all.sh`:
```bash
"$BASE/researchers/your-domain/findings/$DATE.md"
```

Add your domain to `web/scrape-all-images.sh`:
```python
RESEARCHERS = [
    ...
    "your-domain",
    ...
]
```

Add your domain to the autopush copy step in the `intel-autopush` cron:
```bash
for domain in ... your-domain; do
```

### Step 6 — Run it now (optional)

```bash
# Trigger immediately for today's findings
openclaw cron run <cron-id>

# Copy to researchers folder
cp ~/.openclaw/workspace/intel/$(date +%Y-%m-%d)-your-domain.md \
   researchers/your-domain/findings/$(date +%Y-%m-%d).md

# Translate
python3 web/translate.py researchers/your-domain/findings/$(date +%Y-%m-%d).md

# Scrape images
python3 web/scrape-images.py researchers/your-domain/findings/$(date +%Y-%m-%d).md

# Deploy
git add -A && git commit -m "feat: add your-domain" && git push origin main
vercel deploy --prod
```

---

## ✏️ Refining Researcher Prompts

Each researcher's behavior is controlled entirely by its cron message. To improve a researcher:

```bash
openclaw cron edit <cron-id> --message "$(cat researchers/{domain}/INSTRUCTIONS.md)"
```

**Tips for better research prompts:**
- **Be specific about queries** — vague queries get mainstream news. Narrow queries get signal.
- **Name your sources** — tell the researcher which sites are authoritative (e.g. "prefer Bellingcat, ISW, CoinDesk over general news")
- **Define the edge** — tell it explicitly what "most people miss" means for your domain
- **Add negative instructions** — "skip earnings reports", "ignore press releases", "don't cite Wikipedia"

---

## 🧠 Refining the Synthesis Agent

The synthesis agent reads all daily findings and connects cross-domain threads. Edit `synthesis/INSTRUCTIONS.md` to change:

- Which domains it prioritizes
- The briefing format and length
- The "edge" framing (e.g. crypto × AI × geopolitics)
- The output structure sent to Telegram

To update the live cron:
```bash
openclaw cron edit <synthesis-cron-id> --message "$(cat synthesis/INSTRUCTIONS.md)"
```

---

## 👁️ Refining the Chief Analyst

The chief analyst receives the synthesis output and produces the final actionable briefing. Edit `chief/INSTRUCTIONS.md` to change:

- Tone (more urgent vs. analytical)
- What "actionable" means for your use case
- How it frames investment/strategy implications
- Output format

```bash
openclaw cron edit <chief-cron-id> --message "$(cat chief/INSTRUCTIONS.md)"
```

---

## 🌏 Adding Sub-Domain Tabs (e.g. Communist States)

For domains that need multiple country/topic tabs within one domain:

In `web/server.py`, add `subs` to your researcher entry:

```python
{"id": "your-group", "emoji": "🌐", "name": "Your Group", "zh": "你的群組", "colors": "#111,#333",
 "subs": [
     {"id": "subtopic-1", "emoji": "🔵", "name": "Subtopic 1", "zh": "子主題一"},
     {"id": "subtopic-2", "emoji": "🔴", "name": "Subtopic 2", "zh": "子主題二"},
 ]},
```

Each sub-topic needs its own researcher folder, cron job, and findings files. The parent domain page will automatically render tab navigation.

---

## 🗑️ Removing a Domain

1. Remove from `RESEARCHERS` list in `web/server.py`
2. Kill the cron: `openclaw cron delete <cron-id>`
3. Remove from `web/translate-all.sh` and `web/scrape-all-images.sh`
4. Optionally archive the findings folder

---

## Translation Notes

Translations run automatically via `web/translate.py` using Claude Haiku. If a domain's Chinese translation looks wrong:

```bash
# Force retranslate
touch researchers/{domain}/findings/{date}.md
python3 web/translate.py researchers/{domain}/findings/{date}.md
```

The translator uses a clean, professional prompt — no override language that might trigger refusals.

---

## Deployment

Every change to the repo triggers via the `intel-autopush` cron at 08:00 HKT, or manually:

```bash
git add -A && git commit -m "your message" && git push origin main
vercel deploy --prod
```
