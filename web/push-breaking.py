#!/usr/bin/env python3
"""
Breaking intel detector + Telegram push.
Run every 2 hours via cron.
Detects new findings written since last run and pushes to Telegram channel.

Required env vars:
  TG_PUSH_BOT_TOKEN   — Telegram bot token (from @BotFather)
  TG_PUSH_CHANNEL_ID  — Telegram channel ID (e.g. @intelswarm or -1001234567890)

Usage:
  python3 push-breaking.py
"""
import os, json, time, glob, re
from pathlib import Path
from datetime import datetime, timezone

BASE       = Path(__file__).parent.parent
STATE_FILE = BASE / "web" / "static" / "push-state.json"
TG_TOKEN   = os.environ.get("TG_PUSH_BOT_TOKEN", "")
TG_CHANNEL = os.environ.get("TG_PUSH_CHANNEL_ID", "")

DOMAIN_NAMES = {
    "war": "⚔️ War", "commodities": "📦 Commodities", "russia": "🇷🇺 Russia",
    "china": "🇨🇳 China", "north-korea": "🇰🇵 North Korea", "macro": "📈 Macro",
    "crypto": "₿ Crypto", "ai-agents": "🤖 AI Agents", "health": "🏥 Health",
    "religion": "✝️ Religion", "culture": "🎭 Culture", "emerging": "🌍 Emerging",
    "singularity": "🌀 Singularity", "quant": "📊 Quant", "westeast": "🌐 WestEast",
    "blackbudget": "🕵️ Black Budget", "conspiracy": "🔍 Conspiracy",
    "epstein": "📁 Epstein", "sports": "🏆 Sports",
}

TICKER_MAP = {
    "BTC":  ["bitcoin","btc"], "ETH": ["ethereum","eth"], "SOL": ["solana","sol"],
    "OIL":  ["oil","crude","opec","hormuz","barrel"], "GOLD": ["gold","xau"],
    "DXY":  ["dollar","fed ","federal reserve","interest rate"],
    "SPX":  ["stock market","s&p","nasdaq","recession"], "NVDA": ["nvidia","gpu","chip"],
}

def load_state():
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception:
        return {"last_run": 0, "pushed": []}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))

def get_tickers(text):
    t = text.lower()
    tags = [k for k, kws in TICKER_MAP.items() if any(kw in t for kw in kws)]
    return tags[:4]

def get_latest_date():
    files = sorted(glob.glob(str(BASE / "researchers/war/findings/2026-*.md")))
    if files:
        m = re.search(r"(\d{4}-\d{2}-\d{2})", files[-1])
        if m: return m.group(1)
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

def parse_findings(path):
    """Parse findings from a .md file. Returns list of {title, body, url}."""
    try:
        text = Path(path).read_text()
    except Exception:
        return []
    findings = []
    # Split on "### Finding N:" or "## Finding"
    blocks = re.split(r'\n#{2,3} (?:Finding \d+[:.:]?|finding)', text, flags=re.IGNORECASE)
    for block in blocks[1:]:
        lines = block.strip().splitlines()
        title_line = lines[0].strip().lstrip('#').strip() if lines else ""
        body = " ".join(l.strip() for l in lines[1:8] if l.strip())[:200]
        url_match = re.search(r'https?://\S+', block)
        url = url_match.group(0).rstrip(').,') if url_match else ""
        if title_line:
            findings.append({"title": title_line, "body": body, "url": url})
    return findings

def push_to_telegram(message):
    if not TG_TOKEN or not TG_CHANNEL:
        print(f"  [TG] No token/channel configured. Would push:\n{message[:120]}")
        return False
    import urllib.request, urllib.parse
    payload = json.dumps({"chat_id": TG_CHANNEL, "text": message,
                          "parse_mode": "Markdown", "disable_web_page_preview": False})
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
        data=payload.encode(), method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            return result.get("ok", False)
    except Exception as e:
        print(f"  [TG] Push failed: {e}")
        return False

def format_finding(domain, finding, date):
    name = DOMAIN_NAMES.get(domain, domain.upper())
    tickers = get_tickers(finding["title"] + " " + finding["body"])
    ticker_str = " ".join(f"`{t}`" for t in tickers) if tickers else ""
    url = finding.get("url","")
    body_preview = finding["body"][:120] + "…" if len(finding["body"]) > 120 else finding["body"]
    msg = f"⚡ *BREAKING INTEL* — {name}\n\n"
    msg += f"*{finding['title']}*\n"
    if body_preview:
        msg += f"{body_preview}\n"
    if ticker_str:
        msg += f"\n🏷 {ticker_str}\n"
    if url:
        msg += f"\n[Read source]({url})"
    msg += f"\n\n[View on Intel Swarm](https://intel-swarm.vercel.app/domain/{domain}/{date})"
    return msg

def main():
    state = load_state()
    date  = get_latest_date()
    now   = time.time()
    since = state.get("last_run", now - 7200)  # Default: check last 2h
    pushed_ids = set(state.get("pushed", []))
    new_pushes = []

    print(f"[push-breaking] Checking for new findings since {datetime.fromtimestamp(since).strftime('%H:%M')}…")

    # Scan all domain finding files modified since last run
    pattern = str(BASE / f"researchers/*/findings/{date}.md")
    for path in glob.glob(pattern):
        mtime = os.path.getmtime(path)
        if mtime < since:
            continue
        # Extract domain from path
        parts = Path(path).parts
        domain = parts[-3]  # researchers/{domain}/findings/...
        findings = parse_findings(path)
        for i, f in enumerate(findings):
            fid = f"{domain}-{date}-{i}"
            if fid in pushed_ids:
                continue
            # Push to Telegram
            msg = format_finding(domain, f, date)
            ok  = push_to_telegram(msg)
            if ok or not (TG_TOKEN and TG_CHANNEL):
                new_pushes.append(fid)
                pushed_ids.add(fid)
                print(f"  ✅ Pushed: [{domain}] {f['title'][:50]}")
                time.sleep(1.5)  # Rate limit: 1 msg/sec

    if new_pushes:
        print(f"[push-breaking] Pushed {len(new_pushes)} new findings.")
    else:
        print(f"[push-breaking] No new findings to push.")

    state["last_run"] = now
    state["pushed"]   = list(pushed_ids)[-500:]  # Keep last 500 to avoid bloat
    save_state(state)

if __name__ == "__main__":
    main()
