#!/usr/bin/env python3
"""Intel Swarm — Intelligence Dashboard Server"""

import os, glob, re, json, time
from flask import Flask, render_template, abort, request, jsonify as flask_jsonify
import markdown as md_lib
import requests as http_requests

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── RESEARCHER REGISTRY ──────────────────────────────────────────────────────
# To add a researcher: append a dict here. No other code changes needed.
RESEARCHERS = [
    {"id": "war",           "emoji": "⚔️",  "name": "War",                "zh": "戰爭",     "colors": "#7f1d1d,#ef4444"},
    {"id": "commodities",  "emoji": "🛢️",  "name": "Commodities",         "zh": "大宗商品", "colors": "#78350f,#d97706"},
    {"id": "communist",    "emoji": "🔴",  "name": "Communist States","zh": "共產國家", "colors": "#3b0000,#dc2626",
     "subs": [
         {"id": "china",       "emoji": "🇨🇳", "name": "China",       "zh": "中國"},
         {"id": "russia",      "emoji": "🇷🇺", "name": "Russia",      "zh": "俄羅斯"},
         {"id": "north-korea", "emoji": "🇰🇵", "name": "North Korea", "zh": "北韓"},
     ]},
    {"id": "religion",    "emoji": "✝️", "name": "Religion",     "zh": "宗教",     "colors": "#1c1917,#a8a29e"},
    {"id": "health",      "emoji": "🧬", "name": "Health",        "zh": "健康",     "colors": "#064e3b,#10b981"},
    {"id": "culture",     "emoji": "🎭", "name": "Culture",      "zh": "文化",     "colors": "#7c3aed,#a855f7"},
    {"id": "emerging",    "emoji": "🌍", "name": "Emerging",     "zh": "新興市場", "colors": "#065f46,#10b981"},
    {"id": "ai-agents",   "emoji": "🤖", "name": "AI Agents",    "zh": "AI 代理",  "colors": "#1e40af,#3b82f6"},
    {"id": "crypto",      "emoji": "🪙", "name": "Crypto",       "zh": "加密貨幣", "colors": "#92400e,#f59e0b"},
    {"id": "macro",       "emoji": "📊", "name": "Macro",        "zh": "宏觀",     "colors": "#164e63,#06b6d4"},
    {"id": "singularity", "emoji": "🧠", "name": "Singularity",  "zh": "奇點",     "colors": "#4c1d95,#8b5cf6"},
    {"id": "quant",       "emoji": "📈", "name": "Quant",        "zh": "量化",     "colors": "#713f12,#eab308"},
    {"id": "westeast",    "emoji": "🌏", "name": "West-East",    "zh": "東西方",   "colors": "#134e4a,#14b8a6"},

    {"id": "blackbudget", "emoji": "🖤", "name": "Black Budget", "zh": "黑色預算", "colors": "#0c0a09,#44403c"},
    {"id": "conspiracy",  "emoji": "🕳️", "name": "Conspiracy",  "zh": "陰謀",     "colors": "#14532d,#4ade80"},
    {"id": "sports",      "emoji": "🏆", "name": "Sports",       "zh": "體育",     "colors": "#1a3a1a,#22c55e"},
    # {"id": "epstein",   "emoji": "📁", "name": "Epstein",      "zh": "愛潑斯坦", "colors": "#1c1917,#78716c"},
]

RESEARCHER_INDEX = {r["id"]: r for r in RESEARCHERS}  # fast lookup by id

# ── KNOWN SITE LABELS ─────────────────────────────────────────────────────────
KNOWN_SITES = {
    "theguardian.com": "The Guardian", "nytimes.com": "NY Times",
    "wsj.com": "WSJ", "ft.com": "FT", "bloomberg.com": "Bloomberg",
    "reuters.com": "Reuters", "bbc.com": "BBC", "bbc.co.uk": "BBC",
    "washingtonpost.com": "WashPost", "cnbc.com": "CNBC",
    "techcrunch.com": "TechCrunch", "wired.com": "Wired",
    "fortune.com": "Fortune", "forbes.com": "Forbes",
    "economist.com": "The Economist", "apnews.com": "AP News",
    "axios.com": "Axios", "politico.com": "Politico",
    "coindesk.com": "CoinDesk", "cointelegraph.com": "CoinTelegraph",
    "theblock.co": "The Block", "decrypt.co": "Decrypt",
    "nature.com": "Nature", "arxiv.org": "arXiv",
    "understandingwar.org": "ISW", "defenseone.com": "Defense One",
    "theintercept.com": "The Intercept", "propublica.org": "ProPublica",
    "bellingcat.com": "Bellingcat",
}

# ── FLASK APP ─────────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder="static", static_url_path="/static")

@app.after_request
def no_cache(response):
    # Only disable caching in local dev — Vercel handles its own cache headers
    if not os.environ.get("VERCEL"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# ── FILE I/O ──────────────────────────────────────────────────────────────────
def read_file(path, lang="en"):
    """Read a markdown file. Falls back to English if zh version missing."""
    if lang == "zh":
        zh = path.replace(".md", ".zh.md")
        try:
            with open(zh) as f: return f.read()
        except FileNotFoundError:
            pass
    try:
        with open(path) as f: return f.read()
    except FileNotFoundError:
        return None

def get_dates():
    """All available dates (from synthesis findings), newest first."""
    dates = []
    for f in glob.glob(f"{BASE}/synthesis/findings/2026-*.md"):
        name = os.path.basename(f)
        if not name.endswith(".zh.md"):
            dates.append(name.replace(".md", ""))
    return sorted(dates, reverse=True)

def get_latest_date():
    dates = get_dates()
    return dates[0] if dates else "2026-03-04"

def get_lang():
    return request.args.get("lang", "en")

# ── MARKDOWN ──────────────────────────────────────────────────────────────────
def url_to_label(url):
    """Map a URL to a human-readable outlet name."""
    try:
        m = re.search(r"https?://(?:www\.)?([^/]+)", url)
        if not m: return "Source"
        domain = m.group(1).lower()
        for key in sorted(KNOWN_SITES, key=len, reverse=True):
            if domain == key or domain.endswith("." + key):
                return KNOWN_SITES[key]
        return domain.split(".")[0].replace("-", " ").title()
    except Exception:
        return "Source"

def render_md(text):
    """Convert markdown to HTML, auto-linking bare and bracket URLs."""
    if not text: return ""
    # [https://url] → [Label](url)
    text = re.sub(
        r'\[(?!.*\]\()(https?://[^\]]+)\]',
        lambda m: f"[{url_to_label(m.group(1))}]({m.group(1)})",
        text,
    )
    # bare https://url → [Label](url)
    text = re.sub(
        r'(?<!\()(?<!\[)https?://\S+',
        lambda m: f"[{url_to_label(m.group(0).rstrip('.,;)'))}]({m.group(0).rstrip('.,;)')})",
        text,
    )
    return md_lib.markdown(text, extensions=["extra", "nl2br", "sane_lists"])

# ── FINDINGS PARSING ──────────────────────────────────────────────────────────
def extract_findings(raw):
    """
    Parse researcher markdown into structured findings.
    Returns list of: {title, body, score, url}
    """
    if not raw: return []
    findings = []
    for m in re.finditer(r'\*\*(.+?)\*\*[:\s—–-]*(.+?)(?=\n[-*]|\n\n|\Z)', raw, re.DOTALL):
        title    = m.group(1).strip()
        body_raw = m.group(2).strip()

        if not (10 < len(title) < 200):
            continue

        # Score: explicit [SCORE:N] tag, or keyword boost, or default 3
        score_m = re.search(r'\[SCORE[:\s]*([1-5])\]', body_raw, re.IGNORECASE)
        if score_m:
            score    = int(score_m.group(1))
            body_raw = body_raw[:score_m.start()].strip()
        elif any(k in title.lower() for k in ["breaking","critical","urgent","war","attack","collapse","ban","crash"]):
            score = 4
        else:
            score = 3

        # First source URL in the body
        url_m  = re.search(r'https?://[^\s\)\]\"\'<>,]+', body_raw)
        url    = url_m.group(0).rstrip(".,;)") if url_m else None

        findings.append({
            "title": title,
            "body":  re.sub(r'\s+', ' ', body_raw)[:240],
            "score": score,
            "url":   url,
            "image": None,  # filled later by attach_images()
        })

    return findings[:5]

def top_score(findings):
    return max((f["score"] for f in findings), default=3)

def extract_headline(raw):
    """First finding title. Prefers Chinese text when available."""
    for f in extract_findings(raw):
        title = f["title"]
        if any("\u4e00" <= c <= "\u9fff" for c in title):
            return title
        zh_m = re.search(r"[\u4e00-\u9fff][^\n]{10,}", f["body"])
        if zh_m:
            return zh_m.group(0)[:120]
        return title
    return None

def extract_edge(raw):
    """Extract Edge Signal section (EN or ZH headers — all translation variants)."""
    if not raw: return None
    m = re.search(
        r"##\s*(?:Edge Signal|邊緣信號|邊際信號|邊界信號|边缘信号|邊緣訊號|邊際訊號|邊界訊號)\s*\n(.+?)(?=\n##|\Z)",
        raw, re.DOTALL,
    )
    return re.sub(r"\s+", " ", m.group(1).strip())[:300] if m else None

def extract_tail_sections(raw):
    """Extract everything from Edge Signal / Connects To onward (all ZH variants)."""
    if not raw: return ""
    m = re.search(
        r"(##\s*(?:Edge Signal|邊緣信號|邊際信號|邊界信號|边缘信号|邊緣訊號"
        r"|Connects To|連接到|連結到|連結至|關聯到|相關聯繫|相關連結|連接至).+)",
        raw, re.DOTALL | re.IGNORECASE,
    )
    return m.group(1).strip() if m else ""

# ── IMAGES ────────────────────────────────────────────────────────────────────
def attach_images(findings, rid, date):
    """
    Load {date}-images.json and attach image paths to findings by index.
    Each finding gets exactly its own image — no cross-borrowing.
    """
    path = f"{BASE}/researchers/{rid}/findings/{date}-images.json"
    try:
        with open(path) as f:
            items = json.load(f)
        image_map = {item["finding_idx"]: item["image_path"] for item in items}
    except (FileNotFoundError, json.JSONDecodeError):
        return  # no images — findings stay with image=None

    for i, finding in enumerate(findings):
        finding["image"] = image_map.get(i)  # None if no image for this finding

# ── LAYOUT ENGINE ─────────────────────────────────────────────────────────────
def assign_layout(domains, date):
    """
    Clean 2-column grid layout. No row-spans, no gaps.
    - #1 scorer → span-12 (full-width featured strip at top of grid)
    - All others → span-6 (2 per row, easy to read)
    Odd remainder: last card gets span-12.
    """
    N = len(domains)
    if N == 0:
        return domains

    by_score = sorted(range(N), key=lambda i: domains[i]["score"], reverse=True)
    feat_i = by_score[0]
    rest   = by_score[1:]

    # Featured card: full-width strip
    domains[feat_i]["cols"]       = 12
    domains[feat_i]["sort_order"] = 0

    # Everyone else: span-6 (2 columns)
    for rank, domain_i in enumerate(rest):
        # If odd number of rest cards, last one gets span-12 to avoid half-row
        if rank == len(rest) - 1 and len(rest) % 2 == 1:
            domains[domain_i]["cols"] = 12
        else:
            domains[domain_i]["cols"] = 6
        domains[domain_i]["sort_order"] = rank + 1

    domains.sort(key=lambda d: d.get("sort_order", 99))
    return domains

# ── RESEARCHER DATA ───────────────────────────────────────────────────────────
def get_researcher_data(rid, date, lang="en"):
    """Load and parse everything for one researcher on one date."""
    raw     = read_file(f"{BASE}/researchers/{rid}/findings/{date}.md", lang)
    threads = read_file(f"{BASE}/researchers/{rid}/memory/threads.md", lang)
    sources = read_file(f"{BASE}/researchers/{rid}/memory/sources.md")

    findings = extract_findings(raw)
    attach_images(findings, rid, date)

    return {
        "raw":          raw,
        "html":         render_md(raw),
        "findings":     findings,
        "tail_html":    render_md(extract_tail_sections(raw)),
        "headline":     extract_headline(raw),
        "edge":         extract_edge(raw),
        "threads":      render_md(threads),
        "sources":      render_md(sources),
        "filed":        raw is not None,
        "cover_image":  next((f["image"] for f in findings if f["image"]), None),
    }

# ── ROUTES ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return home(get_latest_date())

@app.route("/date/<date>")
def home(date):
    lang           = get_lang()
    dates          = get_dates()
    synthesis_raw  = read_file(f"{BASE}/synthesis/findings/{date}.md", lang)
    chief_raw      = read_file(f"{BASE}/chief/findings/{date}.md", lang)

    syn_headline = None
    if synthesis_raw:
        m = re.search(r"##\s*(?:The Connective Thread:|連接線索：?|主線：?)\s*(.+)", synthesis_raw)
        syn_headline = m.group(1).strip() if m else ("情報綜合" if lang == "zh" else "Intelligence Synthesis")

    chief_action = None
    if chief_raw:
        m = re.search(r"##.*?Today.*?\n(.+?)(?=\n##|\Z)", chief_raw, re.DOTALL | re.IGNORECASE)
        if m:
            chief_action = re.sub(r"\s+", " ", m.group(1).strip())[:400]

    domains = []
    for r in RESEARCHERS:
        subs = r.get("subs")
        # For parent domains with sub-researchers (e.g. Communist States),
        # show China's findings on the homepage card
        display_id = "china" if subs else r["id"]
        data = get_researcher_data(display_id, date, lang)
        en_findings = extract_findings(read_file(f"{BASE}/researchers/{display_id}/findings/{date}.md", "en")) if lang != "en" else data["findings"]
        # Link card to first sub by default
        card_url = f"/domain/communist/{date}?sub=china" if subs else None
        domains.append({
            "id":       r["id"],
            "emoji":    r["emoji"],
            "name":     r["zh"] if lang == "zh" else r["name"],
            "colors":   r["colors"],
            "score":    top_score(en_findings),
            "card_url": card_url,
            **data,
        })

    assign_layout(domains, date)

    return render_template("home.html",
        date=date, dates=dates, lang=lang,
        synthesis_html=render_md(synthesis_raw),
        chief_html=render_md(chief_raw),
        syn_headline=syn_headline,
        chief_action=chief_action,
        domains=domains,
        researchers=RESEARCHERS,
    )

@app.route("/domain/<rid>")
def domain(rid):
    return domain_date(rid, get_latest_date())

@app.route("/domain/<rid>/<date>")
def domain_date(rid, date):
    if rid not in RESEARCHER_INDEX:
        abort(404)
    r    = RESEARCHER_INDEX[rid]
    lang = get_lang()
    subs = r.get("subs")

    if subs:
        # Authoritarian-style: load data for each sub-researcher
        active_sub = request.args.get("sub", subs[0]["id"])
        sub_data = {}
        for s in subs:
            sub_data[s["id"]] = get_researcher_data(s["id"], date, lang)
        data = sub_data.get(active_sub) or sub_data[subs[0]["id"]]
        all_dates = sorted({
            os.path.basename(f).replace(".md", "")
            for s in subs
            for f in glob.glob(f"{BASE}/researchers/{s['id']}/findings/2026-*.md")
            if not f.endswith(".zh.md")
        }, reverse=True)
        return render_template("domain.html",
            rid=rid,
            emoji=r["emoji"],
            name=r["zh"] if lang == "zh" else r["name"],
            colors=r["colors"],
            date=date,
            dates=get_dates(),
            lang=lang,
            all_dates=all_dates,
            researchers=RESEARCHERS,
            subs=subs,
            active_sub=active_sub,
            **data,
        )

    data = get_researcher_data(rid, date, lang)
    all_dates = sorted({
        os.path.basename(f).replace(".md", "")
        for f in glob.glob(f"{BASE}/researchers/{rid}/findings/2026-*.md")
        if not f.endswith(".zh.md")
    }, reverse=True)

    return render_template("domain.html",
        rid=rid,
        emoji=r["emoji"],
        name=r["zh"] if lang == "zh" else r["name"],
        colors=r["colors"],
        date=date,
        dates=get_dates(),
        lang=lang,
        all_dates=all_dates,
        researchers=RESEARCHERS,
        subs=None,
        active_sub=None,
        **data,
    )

@app.route("/api/search")
def api_search():
    jsonify = flask_jsonify
    q    = request.args.get("q", "").strip().lower()
    date = request.args.get("date", get_latest_date())
    lang = get_lang()
    if not q or len(q) < 2:
        return jsonify([])

    results = []
    for r in RESEARCHERS:
        subs = r.get("subs")
        ids  = [s["id"] for s in subs] if subs else [r["id"]]
        for rid in ids:
            data = get_researcher_data(rid, date, lang)
            for i, f in enumerate(data.get("findings") or []):
                title = f.get("title", "")
                body  = f.get("body",  "")
                if q in title.lower() or q in body.lower():
                    results.append({
                        "domain_id":    r["id"],
                        "domain_name":  r["zh"] if lang == "zh" else r["name"],
                        "domain_emoji": r["emoji"],
                        "colors":       r["colors"],
                        "title":        title,
                        "snippet":      body[:120],
                        "image":        f.get("image"),
                        "url":          f"/domain/{r['id']}/{date}?lang={lang}",
                        "finding_idx":  i,
                    })
            # Also search headline
            hl = data.get("headline", "") or ""
            if q in hl.lower() and not any(res["domain_id"] == r["id"] for res in results[-5:]):
                results.append({
                    "domain_id":    r["id"],
                    "domain_name":  r["zh"] if lang == "zh" else r["name"],
                    "domain_emoji": r["emoji"],
                    "colors":       r["colors"],
                    "title":        hl,
                    "snippet":      "",
                    "image":        data.get("cover_image"),
                    "url":          f"/domain/{r['id']}/{date}?lang={lang}",
                    "finding_idx":  0,
                })

    return jsonify(results[:12])

@app.route("/brief")
def brief():
    return brief_date(get_latest_date())

@app.route("/brief/<date>")
def brief_date(date):
    lang = get_lang()
    return render_template("brief.html",
        date=date, dates=get_dates(), lang=lang,
        synthesis_html=render_md(read_file(f"{BASE}/synthesis/findings/{date}.md", lang)),
        chief_html=render_md(read_file(f"{BASE}/chief/findings/{date}.md", lang)),
        thesis_html=render_md(read_file(f"{BASE}/synthesis/memory/thesis.md")),
        predictions_html=render_md(read_file(f"{BASE}/chief/memory/predictions.md")),
        researchers=RESEARCHERS,
    )

@app.route("/memory")
def memory():
    threads_data = [
        {
            "id":      r["id"],
            "emoji":   r["emoji"],
            "name":    r["name"],
            "threads": render_md(read_file(f"{BASE}/researchers/{r['id']}/memory/threads.md")),
        }
        for r in RESEARCHERS
    ]
    return render_template("memory.html",
        dates=get_dates(),
        thesis=render_md(read_file(f"{BASE}/synthesis/memory/thesis.md")),
        predictions=render_md(read_file(f"{BASE}/chief/memory/predictions.md")),
        chief_thesis=render_md(read_file(f"{BASE}/chief/memory/thesis.md")),
        threads_data=threads_data,
        researchers=RESEARCHERS,
    )

# ── POLYMARKET ───────────────────────────────────────────────────────────
_pm_cache = {}  # key -> (timestamp, data)
_PM_HEADERS = {"User-Agent": "Mozilla/5.0"}

def _pm_cached(key, ttl):
    entry = _pm_cache.get(key)
    if entry and time.time() - entry[0] < ttl:
        return entry[1]
    return None

def _pm_set(key, data):
    _pm_cache[key] = (time.time(), data)

# Domain → Polymarket tag/keyword mapping for causal market search
_PM_DOMAIN_TAGS = {
    "war":        ["geopolitics", "politics"],
    "commodities":["economics", "crypto"],
    "russia":     ["geopolitics", "politics"],
    "china":      ["geopolitics", "politics"],
    "north-korea":["geopolitics", "politics"],
    "macro":      ["economics", "politics"],
    "crypto":     ["crypto"],
    "ai-agents":  ["technology"],
    "health":     ["science"],
    "religion":   ["politics"],
    "culture":    ["entertainment"],
    "emerging":   ["politics", "economics"],
    "singularity":["technology", "science"],
    "quant":      ["economics"],
    "westeast":   ["geopolitics"],
    "blackbudget":["geopolitics", "politics"],
    "conspiracy": ["politics"],
    "epstein":    ["politics"],
    "sports":     ["sports"],
}

def _pm_parse_market(m):
    """Parse a Gamma market dict into our response format."""
    outcomes_raw = m.get("outcomes", "[]")
    if isinstance(outcomes_raw, str):
        try: outcomes_list = json.loads(outcomes_raw)
        except Exception: outcomes_list = []
    else:
        outcomes_list = outcomes_raw
    prices_raw = m.get("outcomePrices", "[]")
    if isinstance(prices_raw, str):
        try: prices_list = json.loads(prices_raw)
        except Exception: prices_list = []
    else:
        prices_list = prices_raw
    tokens_raw = m.get("clobTokenIds", "[]")
    if isinstance(tokens_raw, str):
        try: tokens_list = json.loads(tokens_raw)
        except Exception: tokens_list = []
    else:
        tokens_list = tokens_raw
    if not outcomes_list:
        return None
    outcomes = []
    for i, name in enumerate(outcomes_list):
        price = float(prices_list[i]) if i < len(prices_list) else 0
        token_id = tokens_list[i] if i < len(tokens_list) else ""
        outcomes.append({"name": name, "price": price, "token_id": token_id})
    return {
        "condition_id": m.get("conditionId", ""),
        "question": m.get("question", m.get("groupItemTitle", "")),
        "outcomes": outcomes[:3],
        "end_date_iso": m.get("endDate", m.get("endDateIso", "")),
        "url": f"https://polymarket.com/event/{m.get('slug', '')}",
    }

def _pm_is_active_market(m):
    """Return True only if this market has live, non-resolved odds (0.05–0.95)."""
    prices_raw = m.get("outcomePrices", "[]")
    try:
        prices = json.loads(prices_raw) if isinstance(prices_raw, str) else prices_raw
        yes_p = float(prices[0]) if prices else 0
        return 0.05 < yes_p < 0.95
    except Exception:
        return False

def _pm_volume(m):
    """Return best available volume number for sorting."""
    for key in ("volume1wk", "volume1mo", "volumeNum", "volume"):
        v = m.get(key)
        if v:
            try: return float(v)
            except: pass
    return 0.0

def _pm_score(headline, question):
    """Score causal relevance between headline and market question (0–10)."""
    h = headline.lower()
    q = question.lower()
    stop = {"the","a","an","and","or","but","in","on","at","to","for","of","is","are",
            "was","were","has","have","had","with","from","by","as","its","it","this",
            "that","no","not","will","would","could","should","can","do","does","did"}
    h_words = {w for w in re.findall(r'\w+', h) if len(w) > 3 and w not in stop}
    q_words = {w for w in re.findall(r'\w+', q) if len(w) > 3 and w not in stop}
    overlap = len(h_words & q_words)
    causal = {"attack","strike","war","bomb","invade","sanction","ban","crash",
              "collapse","surge","elect","resign","arrest","kill","fire","hack",
              "approve","reject","deploy","test","default","fail","win","lose",
              "withdraw","escalat","negoti","threat","seize","block","tariff",
              "restrict","cut","raise","plunge","soar","deal","peace","ceasefire"}
    has_causal = any(cw in h for cw in causal)
    score = overlap * 2 + (3 if has_causal else 0)
    return score

@app.route("/api/polymarket/market")
def pm_market():
    q = request.args.get("q", "").strip()
    domain = request.args.get("domain", "").strip()
    if not q:
        return flask_jsonify({})
    cache_key = f"pm_market3:{domain}:{q}"
    cached = _pm_cached(cache_key, 300)
    if cached is not None:
        return flask_jsonify(cached)
    try:
        tags = _PM_DOMAIN_TAGS.get(domain, ["geopolitics", "politics"])
        best_result = None
        best_score = 1  # Lower threshold — prefer active markets

        for tag in tags:
            resp = http_requests.get(
                "https://gamma-api.polymarket.com/events",
                params={"limit": 30, "order": "volume", "ascending": "false",
                        "tag_slug": tag, "active": "true"},
                headers=_PM_HEADERS,
                timeout=6,
            )
            resp.raise_for_status()
            events = resp.json()
            if not isinstance(events, list):
                continue

            for event in events:
                ev_title = event.get("title", "")
                ev_score = _pm_score(q, ev_title)

                # Prefer active markets with real trading volume (rich chart history)
                all_markets = event.get("markets", [])
                active_markets = [m for m in all_markets if _pm_is_active_market(m)]
                # Sort by volume descending so we get the most-traded / most chart data
                active_markets.sort(key=_pm_volume, reverse=True)
                candidate_markets = active_markets[:10] if active_markets else all_markets[:5]

                for m in candidate_markets:
                    mq = m.get("question", m.get("groupItemTitle", ev_title))
                    ms = max(_pm_score(q, mq), ev_score)
                    if ms >= best_score:
                        parsed = _pm_parse_market(m)
                        if parsed and parsed["outcomes"]:
                            # Heavily boost score for high-volume markets (good chart data)
                            vol = _pm_volume(m)
                            vol_bonus = 4 if vol > 10000 else (2 if vol > 1000 else (1 if vol > 100 else 0))
                            live_bonus = 2 if _pm_is_active_market(m) else 0
                            total = ms + live_bonus + vol_bonus
                            if total > best_score:
                                best_score = total
                                best_result = parsed

        if best_result:
            _pm_set(cache_key, best_result)
            return flask_jsonify(best_result)
        _pm_set(cache_key, {})
        return flask_jsonify({})
    except Exception:
        return flask_jsonify({})

@app.route("/api/polymarket/chart")
def pm_chart():
    # Accept comma-separated token_ids — try each until we get data
    raw_ids = request.args.get("token_id", "").strip()
    if not raw_ids:
        return flask_jsonify({"points": []})
    token_ids = [t.strip() for t in raw_ids.split(",") if t.strip()]
    cache_key = f"pm_chart3:{raw_ids[:80]}"
    cached = _pm_cached(cache_key, 120)
    if cached is not None:
        return flask_jsonify(cached)
    try:
        for token_id in token_ids:
            resp = http_requests.get(
                "https://clob.polymarket.com/prices-history",
                params={"market": token_id, "interval": "max"},
                headers=_PM_HEADERS,
                timeout=5,
            )
            resp.raise_for_status()
            raw = resp.json()
            history = raw.get("history", []) if isinstance(raw, dict) else []
            if len(history) >= 3:
                # Downsample to max 60 points for sparkline
                step = max(1, len(history) // 60)
                points = [{"t": pt["t"], "p": round(float(pt["p"]), 4)}
                          for pt in history[::step]]
                # Always include the last point
                last = history[-1]
                if points[-1]["t"] != last["t"]:
                    points.append({"t": last["t"], "p": round(float(last["p"]), 4)})
                result = {"points": points}
                _pm_set(cache_key, result)
                return flask_jsonify(result)
        result = {"points": []}
        _pm_set(cache_key, result)
        return flask_jsonify(result)
    except Exception:
        return flask_jsonify({"points": []})

# ── ENTRYPOINT ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    local_ip = os.popen(
        "ipconfig getifaddr en0 2>/dev/null || "
        "ifconfig | grep 'inet ' | grep -v 127 | awk '{print $2}' | head -1"
    ).read().strip()
    print(f"\n🐝 Intel Swarm")
    print(f"   Local:   http://localhost:5757")
    print(f"   Network: http://{local_ip}:5757\n")
    app.run(host="0.0.0.0", port=5757, debug=False)
