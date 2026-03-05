#!/usr/bin/env python3
"""
Pre-fetch Polymarket markets for each finding and cache as {date}-polymarket.json.
Run daily after findings are written, before Vercel deploy.
Usage: python3 web/prefetch-polymarket.py [YYYY-MM-DD]
"""
import sys, os, json, re, time
import urllib.request, urllib.parse

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
date = sys.argv[1] if len(sys.argv) > 1 else __import__('datetime').date.today().isoformat()

RESEARCHERS = [
    "war","commodities","religion","health","culture","emerging",
    "ai-agents","crypto","macro","singularity","quant","westeast",
    "blackbudget","conspiracy","epstein","sports",
    "russia","china","north-korea",
]

DOMAIN_TAGS = {
    "war":        [("geopolitics","iran"), ("geopolitics","ukraine")],
    "commodities":[("economics","oil"), ("economics","gold")],
    "russia":     [("geopolitics","russia"), ("geopolitics","ukraine")],
    "china":      [("geopolitics","china"), ("geopolitics","taiwan")],
    "north-korea":[("geopolitics","north korea"), ("geopolitics","nuclear")],
    "macro":      [("economics","fed"), ("economics","recession")],
    "crypto":     [("crypto","bitcoin"), ("crypto","ethereum"), ("crypto","solana")],
    "ai-agents":  [("technology","ai"), ("technology","openai")],
    "health":     [("science","fda"), ("science","health")],
    "religion":   [("politics","israel"), ("politics","trump")],
    "culture":    [("entertainment","oscars"), ("sports","culture")],
    "emerging":   [("economics","emerging"), ("geopolitics","africa")],
    "singularity":[("technology","agi"), ("technology","openai")],
    "quant":      [("economics","stock"), ("economics","inflation")],
    "westeast":   [("geopolitics","china"), ("geopolitics","us")],
    "blackbudget":[("geopolitics","military"), ("politics","pentagon")],
    "conspiracy": [("politics","trump"), ("politics","us")],
    "epstein":    [("politics","trump"), ("politics","justice")],
    "sports":     [("sports","nfl"), ("sports","nba"), ("sports","soccer")],
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
STOP = {"the","a","an","and","or","but","in","on","at","to","for","of","is","are",
        "was","were","has","have","had","with","from","by","as","its","it","this",
        "that","no","not","will","would","could","should","can","do","does","did"}

def fetch_json(url, params=None):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return json.loads(r.read())
    except Exception:
        return None

def extract_findings(path):
    """Parse markdown findings file, return list of {title, body} dicts."""
    try:
        with open(path) as f:
            raw = f.read()
    except Exception:
        return []
    findings = []
    for m in re.finditer(r'-\s+\*\*(.+?)\*\*\s*[—–-]+\s*(.+?)(?=\n-\s+\*\*|\Z)', raw, re.DOTALL):
        title = m.group(1).strip()
        body = re.sub(r'\s+', ' ', m.group(2).strip())[:200]
        if title:
            findings.append({"title": title, "body": body})
    return findings[:5]

def is_active(m):
    prices_raw = m.get("outcomePrices", "[]")
    try:
        prices = json.loads(prices_raw) if isinstance(prices_raw, str) else prices_raw
        yes_p = float(prices[0]) if prices else 0
        return 0.05 < yes_p < 0.95
    except Exception:
        return False

def market_volume(m):
    for key in ("volume1wk", "volume1mo", "volumeNum", "volume"):
        v = m.get(key)
        if v:
            try: return float(v)
            except: pass
    return 0.0

def score(headline, question):
    h = headline.lower()
    q = question.lower()
    h_words = {w for w in re.findall(r'\b\w+\b', h) if len(w) > 3 and w not in STOP}
    q_words = {w for w in re.findall(r'\b\w+\b', q) if len(w) > 3 and w not in STOP}
    overlap = len(h_words & q_words)
    causal = {"attack","strikes","strike","struck","bomb","invade","invaded","sanction",
              "ban","crash","collapse","surge","elect","resign","arrest","kill","hack",
              "approve","reject","deploy","test","default","lose","withdraw","escalate",
              "negotiate","threat","seize","block","tariff","restrict","plunge","soar",
              "deal","peace","ceasefire","military","offensive","invasion","conflict",
              "crisis","nuclear","war","wars"}
    has_causal = any(re.search(r'\b' + re.escape(cw) + r'\b', h) for cw in causal)
    return overlap * 2 + (2 if has_causal and overlap > 0 else 0)

def parse_market(m, chart_tokens=None):
    outcomes_raw = m.get("outcomes", "[]")
    try: outcomes_list = json.loads(outcomes_raw) if isinstance(outcomes_raw, str) else outcomes_raw
    except: outcomes_list = []
    prices_raw = m.get("outcomePrices", "[]")
    try: prices_list = json.loads(prices_raw) if isinstance(prices_raw, str) else prices_raw
    except: prices_list = []
    tokens_raw = m.get("clobTokenIds", "[]")
    try: tokens_list = json.loads(tokens_raw) if isinstance(tokens_raw, str) else tokens_raw
    except: tokens_list = []
    if not outcomes_list:
        return None
    outcomes = []
    for i, name in enumerate(outcomes_list):
        price = float(prices_list[i]) if i < len(prices_list) else 0
        token_id = tokens_list[i] if i < len(tokens_list) else ""
        outcomes.append({"name": name, "price": price, "token_id": token_id})
    return {
        "question": m.get("question", m.get("groupItemTitle", "")),
        "outcomes": outcomes[:3],
        "url": f"https://polymarket.com/event/{m.get('slug', '')}",
        "chart_tokens": chart_tokens or [],
    }

def find_market(title, domain):
    """Find best causally-relevant active Polymarket market for a finding title."""
    tag_seeds = DOMAIN_TAGS.get(domain, [("geopolitics",""), ("politics","")])
    candidates = []
    seen = set()

    for tag, seed in tag_seeds:
        params = {"limit": 50, "order": "volume", "ascending": "false",
                  "tag_slug": tag, "active": "true"}
        data = fetch_json("https://gamma-api.polymarket.com/events", params)
        if not data or not isinstance(data, list):
            continue
        time.sleep(0.2)  # rate limit

        for event in data:
            eid = event.get("id", event.get("slug", ""))
            if eid in seen:
                continue
            seen.add(eid)
            ev_title = event.get("title", "")
            ev_score = score(title, ev_title)

            all_markets = event.get("markets", [])
            sorted_markets = sorted(all_markets, key=market_volume, reverse=True)
            active_markets = [m for m in sorted_markets if is_active(m)]

            best_score = ev_score
            best_market = active_markets[0] if active_markets else None
            for m in active_markets[:8]:
                mq = m.get("question", m.get("groupItemTitle", ev_title))
                ms = max(score(title, mq), ev_score)
                if ms > best_score:
                    best_score = ms
                    best_market = m

            if best_score < 2 or not best_market or not is_active(best_market):
                continue

            chart_tokens = []
            for m in sorted_markets[:5]:
                t_raw = m.get("clobTokenIds", "[]")
                try: tokens = json.loads(t_raw) if isinstance(t_raw, str) else t_raw
                except: tokens = []
                chart_tokens.extend(tokens[:2])

            parsed = parse_market(best_market, chart_tokens=chart_tokens)
            if parsed and parsed["outcomes"]:
                vol = market_volume(best_market)
                vol_bonus = 3 if vol > 10000 else (1 if vol > 1000 else 0)
                total = best_score + 2 + vol_bonus  # +2 confirmed active
                candidates.append((total, parsed))

    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]

def main():
    print(f"🔍 Prefetching Polymarket markets for {date}...")
    total_matched = 0
    total_findings = 0

    for rid in RESEARCHERS:
        findings_path = f"{BASE}/researchers/{rid}/findings/{date}.md"
        if not os.path.exists(findings_path):
            continue

        findings = extract_findings(findings_path)
        if not findings:
            continue

        result = {}
        for i, f in enumerate(findings):
            title = f["title"]
            print(f"  [{rid}] Finding {i+1}: {title[:50]}...")
            market = find_market(title, rid)
            total_findings += 1
            if market:
                result[str(i)] = market
                total_matched += 1
                print(f"    ✅ → {market['question'][:55]} ({market['outcomes'][0]['price']*100:.0f}%)")
            else:
                print(f"    ❌ no match")

        # Save cache file
        out_path = f"{BASE}/researchers/{rid}/findings/{date}-polymarket.json"
        with open(out_path, "w") as f_out:
            json.dump(result, f_out)
        print(f"  💾 Saved {out_path} ({len(result)}/{len(findings)} matched)")

    print(f"\n✅ Done: {total_matched}/{total_findings} findings matched across all domains")

if __name__ == "__main__":
    main()
