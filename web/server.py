#!/usr/bin/env python3
"""Intel Swarm — Intelligence Dashboard Server"""

import os, glob, re, json, time
from flask import Flask, render_template, abort, request, jsonify as flask_jsonify
import markdown as md_lib
import requests as http_requests
import time

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
    {"id": "ai-agents",   "emoji": "🤖", "name": "AI Agents",    "zh": "AI 代理",  "colors": "#1e40af,#3b82f6"},
    {"id": "crypto",      "emoji": "🪙", "name": "Crypto",       "zh": "加密貨幣", "colors": "#92400e,#f59e0b"},
    {"id": "religion",    "emoji": "✝️", "name": "Religion",     "zh": "宗教",     "colors": "#1c1917,#a8a29e"},
    {"id": "health",      "emoji": "🧬", "name": "Health",        "zh": "健康",     "colors": "#064e3b,#10b981"},
    {"id": "culture",     "emoji": "🎭", "name": "Culture",      "zh": "文化",     "colors": "#7c3aed,#a855f7"},
    {"id": "emerging",    "emoji": "🌍", "name": "Emerging",     "zh": "新興市場", "colors": "#065f46,#10b981"},
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
        en_raw = read_file(f"{BASE}/researchers/{display_id}/findings/{date}.md", "en") if lang != "en" else data["raw"]
        en_findings = extract_findings(en_raw) if lang != "en" else data["findings"]
        en_headline = extract_headline(en_raw) if lang != "en" else data["headline"]
        # Link card to first sub by default
        card_url = f"/domain/communist/{date}?sub=china" if subs else None
        domains.append({
            "id":       r["id"],
            "emoji":    r["emoji"],
            "name":     r["zh"] if lang == "zh" else r["name"],
            "colors":   r["colors"],
            "score":    top_score(en_findings),
            "card_url": card_url,
            "en_headline": en_headline,   # always English, for Polymarket matching
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
    # Always fetch English findings for Polymarket matching (even in ZH mode)
    if lang != "en":
        en_raw = read_file(f"{BASE}/researchers/{rid}/findings/{date}.md", "en")
        en_findings = extract_findings(en_raw) if en_raw else data["findings"]
    else:
        en_findings = data["findings"]
    # Attach English title to each finding so template can use it for data-search
    for i, f in enumerate(data["findings"]):
        f["en_title"] = en_findings[i]["title"] if i < len(en_findings) else f["title"]

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
                        "url":          f"/domain/{r['id']}/{date}?lang={lang}#finding-{i}",
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
                    "url":          f"/domain/{r['id']}/{date}?lang={lang}#finding-0",
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
# Format: list of (tag_slug, seed_keyword_for_search) tuples
# seed_keyword biases the event search toward relevant markets first
_PM_DOMAIN_TAGS = {
    "war":        [("geopolitics","iran"), ("world","iran"), ("politics","iran")],
    "commodities":[("economics","oil"), ("finance","commodity"), ("business","gold")],
    "russia":     [("geopolitics","russia"), ("world","russia"), ("politics","russia")],
    "china":      [("geopolitics","china"), ("world","china"), ("politics","china")],
    "north-korea":[("geopolitics","north-korea"), ("world","north-korea"), ("politics","nuclear")],
    "macro":      [("economics","fed"), ("finance","recession"), ("business","inflation")],
    "crypto":     [("crypto","bitcoin"), ("crypto","ethereum"), ("finance","crypto")],
    "ai-agents":  [("technology","openai"), ("technology","nvidia"), ("technology","ai")],
    "health":     [("health","fda"), ("health","drug"), ("science","vaccine")],
    "religion":   [("politics","israel"), ("geopolitics","israel"), ("world","religion")],
    "culture":    [("entertainment","oscar"), ("entertainment","celebrity"), ("sports","culture")],
    "emerging":   [("economics","emerging"), ("world","africa"), ("finance","developing")],
    "singularity":[("technology","agi"), ("technology","openai"), ("science","ai")],
    "quant":      [("finance","stock"), ("economics","recession"), ("business","market")],
    "westeast":   [("geopolitics","china"), ("economics","trade"), ("politics","tariff")],
    "blackbudget":[("geopolitics","military"), ("politics","pentagon"), ("world","defense")],
    "conspiracy": [("politics","trump"), ("world","government"), ("politics","doge")],
    "epstein":    [("politics","trump"), ("politics","justice"), ("world","justice")],
    "sports":     [("sports","nfl"), ("sports","nba"), ("sports","soccer")],
}

def _pm_parse_market(m, chart_tokens=None, event_image=None, event_slug=None):
    """Parse a Gamma market dict into our response format.
    chart_tokens: list of token_ids from high-volume sibling markets for chart data.
    """
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
        "url": f"https://polymarket.com/event/{event_slug or m.get('slug', '')}",
        # chart_tokens: high-volume sibling tokens to use for real price history
        "chart_tokens": chart_tokens or [],
        # Polymarket event image (S3 hosted) for overlay background
        "event_image": event_image or "",
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
    h_words = {w for w in re.findall(r'\b\w+\b', h) if len(w) > 3 and w not in stop}
    q_words = {w for w in re.findall(r'\b\w+\b', q) if len(w) > 3 and w not in stop}
    overlap = len(h_words & q_words)
    causal = {"attack","strikes","strike","struck","wars","bomb","invade","invaded",
              "sanction","ban","crash","collapse","surges","surge","elect","resign",
              "arrest","kill","hack","approve","reject","deploy","deployed","test",
              "default","lose","withdraw","escalate","negotiate","threat","seize",
              "block","tariff","restrict","plunge","soar","deal","peace","ceasefire",
              "military","offensive","invasion","conflict","crisis","nuclear"}
    # Use word-boundary matching — "warfare" must NOT match "war"
    has_causal = any(re.search(r'\b' + re.escape(cw) + r'\b', h) for cw in causal)
    # Causal bonus only counts when there's also keyword overlap (prevents false positives)
    score = overlap * 2 + (2 if has_causal and overlap > 0 else 0)
    return score

@app.route("/api/polymarket/cached")
def pm_cached_batch():
    """Return pre-fetched Polymarket cache for a researcher on a date."""
    rid = request.args.get("rid", "").strip()
    date = request.args.get("date", get_latest_date()).strip()
    if not rid:
        return flask_jsonify({})
    cache_path = f"{BASE}/researchers/{rid}/findings/{date}-polymarket.json"
    try:
        with open(cache_path) as f:
            return flask_jsonify(json.load(f))
    except Exception:
        return flask_jsonify({})

@app.route("/api/polymarket/market")
def pm_market():
    q = request.args.get("q", "").strip()
    domain = request.args.get("domain", "").strip()
    if not q:
        return flask_jsonify({})
    cache_key = f"pm_market9:{domain}:{q}"
    cached = _pm_cached(cache_key, 300)
    if cached is not None:
        return flask_jsonify(cached)
    try:
        tag_seeds = _PM_DOMAIN_TAGS.get(domain, [("geopolitics",""), ("politics","")])
        best_result = None
        best_score = 3  # Raised threshold — require meaningful causal overlap

        seen_event_ids = set()
        # Collect all candidate (score, result) pairs across all tag searches, pick global best
        candidates = []
        for tag, seed in tag_seeds:
            params = {"limit": 50, "order": "volume", "ascending": "false",
                      "tag_slug": tag, "active": "true"}
            try:
                resp = http_requests.get(
                    "https://gamma-api.polymarket.com/events",
                    params=params,
                    headers=_PM_HEADERS,
                    timeout=6,
                )
                resp.raise_for_status()
                events = resp.json()
            except Exception:
                continue
            if not isinstance(events, list):
                continue

            for event in events:
                eid = event.get("id", event.get("slug", ""))
                if eid in seen_event_ids:
                    continue
                seen_event_ids.add(eid)
                ev_title = event.get("title", "")
                ev_score = _pm_score(q, ev_title)

                all_markets = event.get("markets", [])
                all_markets_sorted = sorted(all_markets, key=_pm_volume, reverse=True)
                active_markets = [m for m in all_markets_sorted if _pm_is_active_market(m)]

                # Also score individual active markets vs the headline
                best_market_score = ev_score
                best_candidate_market = active_markets[0] if active_markets else (all_markets_sorted[0] if all_markets_sorted else None)
                for m in active_markets[:8]:
                    mq = m.get("question", m.get("groupItemTitle", ev_title))
                    ms = max(_pm_score(q, mq), ev_score)
                    if ms > best_market_score:
                        best_market_score = ms
                        best_candidate_market = m

                # Skip if no live candidate (never return resolved 0%/100% markets)
                if best_market_score < 2 or not best_candidate_market:
                    continue
                if not _pm_is_active_market(best_candidate_market):
                    best_candidate_market = active_markets[0] if active_markets else None
                    if not best_candidate_market:
                        continue

                # Domain-specific anti-false-positive guard
                # Require at least one domain keyword to appear in event title or market question
                _DOMAIN_REQUIRED = {
                    "health":     ["health","fda","drug","vaccine","medical","disease","cancer","clinical"],
                    "sports":     ["nfl","nba","soccer","football","basketball","baseball","tennis","ufc","sport"],
                    "crypto":     ["bitcoin","btc","ethereum","eth","solana","sol","crypto","token","defi","nft"],
                    "ai-agents":  ["ai","openai","gpt","claude","gemini","nvidia","llm","deepseek","model"],
                    "culture":    ["oscar","emmy","grammy","celebrity","movie","film","music","pop","taylor"],
                    "religion":   ["israel","iran","muslim","christian","pope","church","faith","temple","god","jesus"],
                    "macro":      ["fed","rate","inflation","recession","gdp","treasury","bond","dollar","euro"],
                    "singularity":["agi","openai","gpt","intelligence","robot","automation","llm","deepseek"],
                    "epstein":    ["epstein","maxwell","trial","abuse","sex","victim","court"],
                    "conspiracy": ["trump","government","cia","doge","elon","deep state","fbi","whistleblower"],
                }
                if domain in _DOMAIN_REQUIRED:
                    combined = (ev_title + " " + best_candidate_market.get("question","")).lower()
                    if not any(kw in combined for kw in _DOMAIN_REQUIRED[domain]):
                        continue

                # Collect chart tokens from high-volume siblings (resolved OK for chart data)
                top_chart_tokens = []
                for m in all_markets_sorted[:5]:
                    t_raw = m.get("clobTokenIds", "[]")
                    try: tokens = json.loads(t_raw) if isinstance(t_raw, str) else t_raw
                    except: tokens = []
                    top_chart_tokens.extend(tokens[:2])

                ev_image = event.get("image", "")
                ev_slug = event.get("slug", "")
                parsed = _pm_parse_market(best_candidate_market, chart_tokens=top_chart_tokens, event_image=ev_image, event_slug=ev_slug)
                if parsed and parsed["outcomes"]:
                    vol = _pm_volume(best_candidate_market)
                    vol_bonus = 3 if vol > 10000 else (1 if vol > 1000 else 0)
                    live_bonus = 2  # already confirmed active above
                    total = best_market_score + live_bonus + vol_bonus
                    candidates.append((total, parsed))

        # Pick the globally highest-scoring candidate
        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            best_result = candidates[0][1]

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

# ── CONFLICT MAP ──────────────────────────────────────────────────────────────

# GDELT event type classification keywords
_GDELT_CONFLICT_WORDS  = {"attack","bomb","kill","shoot","clash","explos","fight","strike","missile","rocket","assault","ambush","mortar","idf","war","troops","military","shelling","siege","hostage","gunfir","casualt"}
_GDELT_PROTEST_WORDS   = {"protest","demonstrat","riot","march","rally","strike","blockade","activist","unrest","uprising","crowd","marche"}
_GDELT_POLITICAL_WORDS = {"sanction","diplomat","election","coup","summit","president","minister","parliament","ceasefire","treaty","negotiat","resign","arrest","indict"}

_CONFLICT_CACHE = {}

def _gdelt_event_type(title):
    t = title.lower()
    for w in _GDELT_CONFLICT_WORDS:
        if w in t: return "CONFLICT"
    for w in _GDELT_PROTEST_WORDS:
        if w in t: return "PROTEST"
    for w in _GDELT_POLITICAL_WORDS:
        if w in t: return "POLITICAL"
    return "OTHER"

_CONFLICT_GEO = {
    # Domain → (lat, lng, label)
    "war":        (32.0,  44.0,  "Middle East"),
    "russia":     (48.5,  35.0,  "Ukraine/Russia"),
    "china":      (35.0, 105.0,  "China"),
    "north-korea":(40.0, 127.5,  "Korean Peninsula"),
    "macro":      (40.7, -74.0,  "United States"),
    "crypto":     (37.8, -122.4, "Global Markets"),
    "commodities":(26.0,  50.5,  "Gulf Region"),
    "religion":   (31.8,  35.2,  "Israel/Palestine"),
    "health":     (46.2,   6.1,  "Geneva/WHO"),
    "ai-agents":  (37.4, -122.1, "Silicon Valley"),
    "singularity":(37.4, -122.1, "Silicon Valley"),
    "culture":    (48.9,   2.3,  "Europe"),
    "emerging":   (-1.3,  36.8,  "Africa/EM"),
    "westeast":   (39.9, 116.4,  "Beijing"),
    "blackbudget":(38.9, -77.0,  "Washington DC"),
    "conspiracy": (38.9, -77.0,  "Washington DC"),
    "epstein":    (40.7, -74.0,  "New York"),
    "sports":     (34.0, -118.2, "Los Angeles"),
    "quant":      (40.7, -74.0,  "Wall Street"),
}

# Per-finding keyword → geo override
_FINDING_GEO_KEYWORDS = [
    (["iran","persian","tehran","khamenei","irgc"],      (33.0, 53.7,  "Iran")),
    (["ukraine","kyiv","kyiv","zelensky","kherson"],     (49.0, 32.0,  "Ukraine")),
    (["russia","moscow","putin","kremlin"],              (55.8, 37.6,  "Russia")),
    (["israel","tel aviv","idf","mossad","netanyahu"],   (31.8, 35.2,  "Israel")),
    (["gaza","hamas","rafah","west bank"],               (31.4, 34.3,  "Gaza")),
    (["lebanon","beirut","hezbollah"],                   (33.9, 35.5,  "Lebanon")),
    (["taiwan","taipei","tsmc","strait"],                (23.7, 121.0, "Taiwan")),
    (["north korea","kim jong","pyongyang"],             (39.0, 125.7, "North Korea")),
    (["china","beijing","xi jinping","pla","ccp"],       (39.9, 116.4, "Beijing")),
    (["saudi","aramco","riyadh","opec"],                 (24.7, 46.7,  "Saudi Arabia")),
    (["hormuz","gulf","uae","dubai"],                    (26.0, 56.0,  "Persian Gulf")),
    (["sudan","khartoum","rsf"],                         (15.6, 32.5,  "Sudan")),
    (["myanmar","burma","naypyidaw"],                    (19.7, 96.1,  "Myanmar")),
    (["syria","damascus","aleppo"],                      (34.8, 38.9,  "Syria")),
    (["yemen","houthi","sanaa"],                         (15.4, 44.2,  "Yemen")),
    (["trump","white house","pentagon","cia","fbi"],     (38.9, -77.0, "Washington DC")),
    (["fed","federal reserve","treasury","powell"],      (38.9, -77.0, "Washington DC")),
    (["nvidia","openai","silicon valley","anthropic"],   (37.4, -122.1,"Silicon Valley")),
    (["bitcoin","crypto","defi","solana","ethereum"],    (40.7, -74.0, "New York")),
    (["who","who headquarter","pandemic","virus"],       (46.2,  6.1,  "Geneva")),
    (["nato","brussels","europe","eu "],                 (50.9,  4.4,  "Brussels")),
    (["africa","nairobi","lagos","accra"],               (-1.3, 36.8,  "Africa")),
    (["india","modi","delhi","mumbai"],                  (28.6, 77.2,  "India")),
    (["pakistan","islamabad","karachi"],                 (33.7, 73.0,  "Pakistan")),
    (["japan","tokyo","abe"],                            (35.7, 139.7, "Tokyo")),
]

def _geocode_finding(title, body, domain):
    """Return (lat, lng, geo_label) for a finding."""
    import random
    text = (title + " " + (body or "")).lower()
    for keywords, coords in _FINDING_GEO_KEYWORDS:
        if any(kw in text for kw in keywords):
            lat = coords[0] + random.uniform(-0.3, 0.3)
            lng = coords[1] + random.uniform(-0.3, 0.3)
            return round(lat, 3), round(lng, 3), coords[2]
    # Fall back to domain default
    if domain in _CONFLICT_GEO:
        base = _CONFLICT_GEO[domain]
        lat = base[0] + random.uniform(-0.5, 0.5)
        lng = base[1] + random.uniform(-0.5, 0.5)
        return round(lat, 3), round(lng, 3), base[2]
    return None, None, ""

@app.route("/conflict")
def conflict_page():
    lang    = get_lang()
    date    = get_latest_date()
    # Build intel events from all domain findings
    intel_events = []
    domain_colors = {r["id"]: r["colors"] for r in RESEARCHERS}
    for r in RESEARCHERS:
        subs = r.get("subs")
        ids  = [(s["id"], s) for s in subs] if subs else [(r["id"], r)]
        for rid, meta in ids:
            data_loc = get_researcher_data(rid, date, lang)
            data_en  = get_researcher_data(rid, date, "en") if lang != "en" else data_loc
            findings_loc = data_loc.get("findings") or []
            findings_en  = data_en.get("findings")  or []
            domain_name  = (meta.get("zh") or r.get("zh") or meta.get("name") or r.get("name") or rid) if lang == "zh" \
                           else (meta.get("name") or r.get("name") or rid)
            for i, f in enumerate(findings_loc):
                title    = f.get("title") or ""
                body     = f.get("body")  or ""
                # Always geocode from English text for accuracy
                en_f     = findings_en[i] if i < len(findings_en) else f
                en_title = en_f.get("title") or title
                en_body  = en_f.get("body")  or body
                if not title: continue
                lat, lng, geo = _geocode_finding(en_title, en_body, rid)
                # Translate geo label if zh
                geo_display = geo
                intel_events.append({
                    "title":       title,
                    "geo":         geo_display,
                    "lat":         lat,
                    "lng":         lng,
                    "category":    rid,
                    "domain_name": domain_name,
                    "domain_url":  f"/domain/{r['id']}/{date}?lang={lang}#finding-{i}",
                    "date":        date,
                    "url":         f.get("url") or "",
                    "colors":      r.get("colors","#888,#aaa"),
                })
    # GDELT heat points from static file (lat/lng only for heat layer)
    heat_data = []
    static_path = os.path.join(BASE, "web", "static", "conflict-events.json")
    if os.path.exists(static_path):
        try:
            with open(static_path) as f:
                gd = json.load(f)
            for ev in gd.get("events", []):
                if ev.get("lat") and ev.get("lng"):
                    intensity = 1.0 if ev.get("type") == "CONFLICT" else 0.4
                    heat_data.append([ev["lat"], ev["lng"], intensity])
        except Exception:
            pass
    return render_template("conflict.html",
        lang=lang, researchers=RESEARCHERS,
        intel_events=intel_events,
        heat_data=heat_data[:2000],
        date=date)

_COUNTRY_COORDS = {
    "iran": (32.4, 53.7), "ukraine": (49.0, 32.0), "russia": (61.5, 105.3),
    "israel": (31.0, 35.0), "gaza": (31.4, 34.3), "lebanon": (33.9, 35.5),
    "syria": (34.8, 38.9), "iraq": (33.2, 43.7), "yemen": (15.5, 48.5),
    "china": (35.9, 104.2), "taiwan": (23.7, 121.0), "north korea": (40.3, 127.5),
    "south korea": (36.5, 127.9), "japan": (36.2, 138.3), "india": (20.6, 79.0),
    "pakistan": (30.4, 69.3), "afghanistan": (33.9, 67.7), "myanmar": (19.2, 96.7),
    "sudan": (12.9, 30.2), "ethiopia": (9.1, 40.5), "somalia": (5.2, 46.2),
    "mali": (17.6, -2.0), "nigeria": (9.1, 8.7), "congo": (-4.0, 21.8),
    "libya": (26.3, 17.2), "egypt": (26.8, 30.8), "turkey": (39.0, 35.2),
    "saudi arabia": (24.7, 45.7), "united states": (37.1, -95.7), "usa": (37.1, -95.7),
    "mexico": (23.6, -102.6), "venezuela": (6.4, -66.6), "colombia": (4.6, -74.1),
    "myanmar": (19.2, 96.7), "thailand": (15.9, 100.9), "philippines": (12.9, 121.8),
    "haiti": (18.9, -72.3), "serbia": (44.0, 21.0), "kosovo": (42.6, 20.9),
    "georgia": (42.3, 43.4), "armenia": (40.1, 45.0), "azerbaijan": (40.1, 47.6),
}

def _gdelt_geocode(title):
    t = title.lower()
    for name, coords in _COUNTRY_COORDS.items():
        if name in t:
            # Jitter slightly so dots don't stack exactly
            import random
            lat = coords[0] + random.uniform(-0.8, 0.8)
            lng = coords[1] + random.uniform(-0.8, 0.8)
            return lat, lng, name.title()
    return None, None, ""

@app.route("/api/conflict/events")
def conflict_events():
    # 1. Try pre-fetched static file (written by prefetch-conflict.py cron)
    static_path = os.path.join(BASE, "web", "static", "conflict-events.json")
    if os.path.exists(static_path):
        try:
            with open(static_path) as f:
                return flask_jsonify(json.load(f))
        except Exception:
            pass

    # 2. In-memory cache fallback
    cache_key = "gdelt_events"
    cached = _CONFLICT_CACHE.get(cache_key)
    if cached and (time.time() - cached["ts"] < 900):   # 15 min TTL
        return flask_jsonify(cached["data"])

    events = []
    try:
        # GDELT DOC 2.0 ArticleSearch — conflict/war articles last 24h
        resp = http_requests.get(
            "https://api.gdeltproject.org/api/v2/doc/doc",
            params={
                "query": "(war OR conflict OR attack OR bomb OR strike OR missile OR protest OR sanction OR military OR troops) sourcelang:english",
                "mode": "ArtList",
                "maxrecords": 250,
                "timespan": "1d",
                "format": "json",
            },
            timeout=12,
            headers={"User-Agent": "intel-swarm/1.0"},
        )
        resp.raise_for_status()
        articles = resp.json().get("articles") or []
        seen = set()
        for a in articles:
            title = (a.get("title") or "").strip()
            url   = a.get("url") or ""
            date  = (a.get("seendate") or "")[:8]
            if not title or url in seen:
                continue
            seen.add(url)
            lat, lng, country = _gdelt_geocode(title)
            # Assign rough tone from event type
            evt_type = _gdelt_event_type(title)
            tone = -8.0 if evt_type == "CONFLICT" else (-4.0 if evt_type == "PROTEST" else -2.0)
            if date:
                date = f"{date[:4]}-{date[4:6]}-{date[6:]}"
            events.append({
                "title":   title,
                "url":     url,
                "tone":    tone,
                "date":    date,
                "country": country,
                "geo":     country,
                "lat":     lat,
                "lng":     lng,
                "type":    evt_type,
            })
        # Sort: conflict first, then protest, then political
        type_order = {"CONFLICT": 0, "PROTEST": 1, "POLITICAL": 2, "OTHER": 3}
        events.sort(key=lambda e: type_order.get(e["type"], 3))
    except Exception as ex:
        print(f"[conflict] GDELT fetch error: {ex}")

    result = {"events": events, "count": len(events)}
    _CONFLICT_CACHE[cache_key] = {"ts": time.time(), "data": result}
    return flask_jsonify(result)

# ── PUBLIC API v1 ─────────────────────────────────────────────────────────────

# Ticker → keyword map for cross-domain asset tagging
_TICKER_MAP = {
    "$BTC":  ["bitcoin","btc","crypto","cryptocurrency"],
    "$ETH":  ["ethereum","eth"],
    "$SOL":  ["solana","sol"],
    "$XRP":  ["ripple","xrp"],
    "$DOGE": ["doge","dogecoin","musk","elon"],
    "$PEPE": ["pepe","meme","memecoin"],
    "$WIF":  ["wif","dogwifhat"],
    "$BONK": ["bonk"],
    "OIL":   ["oil","crude","opec","barrel","petroleum","brent","wti","hormuz","iran","strait of hormuz","middle east war","saudi","houthi"],
    "GOLD":  ["gold","xau","bullion","precious metal"],
    "DXY":   ["dollar","dxy","usd","federal reserve","fed ","powell","interest rate"],
    "BONDS": ["treasury","bond","yield","10-year","t-bill","debt"],
    "SPX":   ["stock","s&p","equities","nasdaq","wall street","market crash","recession"],
    "EUR":   ["euro","ecb","europe","eurozone"],
    "JPY":   ["yen","japan","boj"],
    "CNY":   ["yuan","renminbi","pboc","china trade"],
    "$BTC":  ["bitcoin","btc","crypto","cryptocurrency","trump crypto","etf","coinbase","blackrock","sec crypto","crypto regulation"],
    "NVDA":  ["nvidia","cuda","gpu","ai chip","semiconductor","tsmc"],
    "TSLA":  ["tesla","elon","spacex"],
    "DEFENSE":["defense","raytheon","lockheed","northrop","military contract","pentagon budget"],
    "$HYPE": ["hyperliquid","hype","perps","perpetual dex","onchain perps"],
    "$ZEC":  ["zcash","zec","privacy coin","zero-knowledge coin","shielded"],
    "$PUMP": ["pump.fun","pump fun","meme launch","token launch","fair launch","pumpfun"],
}

def _tag_tickers(text):
    """Return list of ticker tags relevant to a text string."""
    t = text.lower()
    tags = []
    for ticker, keywords in _TICKER_MAP.items():
        if any(kw in t for kw in keywords):
            if ticker not in tags:
                tags.append(ticker)
    return tags[:5]

def _is_breaking(date_str, finding_idx):
    """Mark as BREAKING if finding was updated in the last 2 hours (based on file mtime)."""
    import glob as _glob
    # Check if the findings file was modified in the last 2h
    paths = _glob.glob(f"{BASE}/researchers/*/findings/{date_str}.md") + \
            _glob.glob(f"{BASE}/researchers/*/findings/{date_str}.zh.md")
    for p in paths:
        try:
            age = time.time() - os.path.getmtime(p)
            if age < 7200:  # 2 hours
                return True
        except Exception:
            pass
    return False

def _build_api_finding(f, i, rid, r, date, lang="en"):
    title   = f.get("title") or ""
    body    = f.get("body")  or ""
    tickers = _tag_tickers(title + " " + body)
    return {
        "id":          f"{rid}-{date}-{i}",
        "domain":      rid,
        "domain_name": r.get("name",""),
        "domain_emoji":r.get("emoji",""),
        "domain_colors":r.get("colors",""),
        "title":       title,
        "body":        body,
        "url":         f.get("url",""),
        "image":       f.get("image",""),
        "score":       f.get("score",3),
        "tickers":     tickers,
        "date":        date,
        "index":       i,
        "permalink":   f"/domain/{rid}/{date}?lang={lang}#finding-{i}",
    }

@app.route("/api/v1/domains")
def api_v1_domains():
    return flask_jsonify([{
        "id":     r["id"],
        "name":   r["name"],
        "emoji":  r.get("emoji",""),
        "colors": r.get("colors",""),
        "subs":   [{"id":s["id"],"name":s["name"]} for s in r.get("subs",[])] if r.get("subs") else [],
    } for r in RESEARCHERS])

@app.route("/api/v1/findings")
def api_v1_findings():
    date   = request.args.get("date", get_latest_date())
    domain = request.args.get("domain","").strip()
    lang   = get_lang()
    limit  = min(int(request.args.get("limit", 100)), 500)
    ticker = request.args.get("ticker","").upper().lstrip("$")

    results = []
    for r in RESEARCHERS:
        subs = r.get("subs")
        ids  = [s["id"] for s in subs] if subs else [r["id"]]
        for rid in ids:
            if domain and rid != domain:
                continue
            data = get_researcher_data(rid, date, lang)
            for i, f in enumerate(data.get("findings") or []):
                item = _build_api_finding(f, i, rid, r, date, lang)
                if ticker and not any(ticker in t for t in item["tickers"]):
                    continue
                results.append(item)
    return flask_jsonify({"date": date, "count": len(results[:limit]), "findings": results[:limit]})

@app.route("/api/v1/brief")
def api_v1_brief():
    date = request.args.get("date", get_latest_date())
    lang = get_lang()
    syn  = read_file(f"{BASE}/synthesis/findings/{date}.md", lang) or ""
    chief= read_file(f"{BASE}/chief/findings/{date}.md", lang) or ""
    return flask_jsonify({"date": date, "synthesis": syn, "chief_brief": chief})

@app.route("/api/v1/feed")
def api_v1_feed():
    """All findings flat-sorted by score desc, newest first. For programmatic consumption."""
    date   = request.args.get("date", get_latest_date())
    lang   = get_lang()
    results = []
    for r in RESEARCHERS:
        subs = r.get("subs")
        ids  = [s["id"] for s in subs] if subs else [r["id"]]
        for rid in ids:
            data = get_researcher_data(rid, date, lang)
            for i, f in enumerate(data.get("findings") or []):
                item = _build_api_finding(f, i, rid, r, date, lang)
                results.append(item)
    results.sort(key=lambda x: x["score"], reverse=True)
    return flask_jsonify({"date": date, "count": len(results), "findings": results})

@app.route("/api/v1/search")
def api_v1_search():
    q    = request.args.get("q","").strip().lower()
    date = request.args.get("date", get_latest_date())
    lang = get_lang()
    if not q:
        return flask_jsonify({"results": []})
    results = []
    for r in RESEARCHERS:
        subs = r.get("subs")
        ids  = [s["id"] for s in subs] if subs else [r["id"]]
        for rid in ids:
            data = get_researcher_data(rid, date, lang)
            for i, f in enumerate(data.get("findings") or []):
                title = f.get("title","")
                body  = f.get("body","")
                if q in title.lower() or q in body.lower():
                    results.append(_build_api_finding(f, i, rid, r, date, lang))
    return flask_jsonify({"query": q, "count": len(results), "results": results})

# RSS feed per domain (and global)
@app.route("/rss")
@app.route("/rss/<rid>")
def rss_feed(rid=None):
    from markupsafe import escape as xml_escape
    date  = get_latest_date()
    items = []
    for r in RESEARCHERS:
        subs = r.get("subs")
        ids  = [s["id"] for s in subs] if subs else [r["id"]]
        for rdid in ids:
            if rid and rdid != rid:
                continue
            data = get_researcher_data(rdid, date, "en")
            for i, f in enumerate(data.get("findings") or []):
                items.append({
                    "title":  f.get("title",""),
                    "link":   f"https://intel-swarm.vercel.app/domain/{r['id']}/{date}?lang=en#finding-{i}",
                    "desc":   f.get("body","")[:300],
                    "domain": r.get("name",""),
                    "emoji":  r.get("emoji",""),
                })
    feed_title = f"Intel Swarm{' · ' + rid if rid else ''}"
    rss = '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0">\n<channel>\n'
    rss += f'<title>{feed_title}</title>\n'
    rss += f'<link>https://intel-swarm.vercel.app</link>\n'
    rss += f'<description>AI intelligence feed — {date}</description>\n'
    for item in items[:50]:
        rss += '<item>\n'
        rss += f'<title>{item["emoji"]} [{item["domain"]}] {item["title"]}</title>\n'
        rss += f'<link>{item["link"]}</link>\n'
        rss += f'<description>{item["desc"]}</description>\n'
        rss += f'<guid>{item["link"]}</guid>\n'
        rss += '</item>\n'
    rss += '</channel>\n</rss>'
    from flask import Response
    return Response(rss, mimetype='application/rss+xml')

# Telegram push (called by breaking intel cron)
_TG_BOT_TOKEN  = os.environ.get("TG_PUSH_BOT_TOKEN","")
_TG_CHANNEL_ID = os.environ.get("TG_PUSH_CHANNEL_ID","")

@app.route("/api/v1/push/test", methods=["POST"])
def api_push_test():
    """Test Telegram push. POST with JSON {token: <admin_token>}"""
    if not _TG_BOT_TOKEN or not _TG_CHANNEL_ID:
        return flask_jsonify({"ok": False, "error": "TG_PUSH_BOT_TOKEN or TG_PUSH_CHANNEL_ID not set"})
    try:
        msg = "🧪 *Intel Swarm push test* — Telegram integration active."
        r = http_requests.post(
            f"https://api.telegram.org/bot{_TG_BOT_TOKEN}/sendMessage",
            json={"chat_id": _TG_CHANNEL_ID, "text": msg, "parse_mode": "Markdown"},
            timeout=8,
        )
        return flask_jsonify({"ok": r.ok, "status": r.status_code})
    except Exception as e:
        return flask_jsonify({"ok": False, "error": str(e)})

# ── TERMINAL PAGE ──────────────────────────────────────────────────────────────

@app.route("/terminal")
def terminal_page():
    lang  = get_lang()
    date  = get_latest_date()
    all_findings = []
    for r in RESEARCHERS:
        subs = r.get("subs")
        ids  = [s["id"] for s in subs] if subs else [r["id"]]
        for rid in ids:
            data = get_researcher_data(rid, date, lang)
            en_data = get_researcher_data(rid, date, "en") if lang != "en" else data
            en_findings = en_data.get("findings") or []
            for i, f in enumerate(data.get("findings") or []):
                en_f   = en_findings[i] if i < len(en_findings) else f
                en_txt = (en_f.get("title","") + " " + (en_f.get("body","") or ""))
                tickers = _tag_tickers(en_txt)
                all_findings.append({
                    "id":      f"{rid}-{i}",
                    "domain":  rid,
                    "domain_name": (r.get("zh") if lang=="zh" else r.get("name")) or rid,
                    "emoji":   r.get("emoji",""),
                    "colors":  r.get("colors","#888,#aaa"),
                    "title":   f.get("title",""),
                    "body":    (f.get("body","") or "")[:200],
                    "url":     f.get("url",""),
                    "image":   f.get("image",""),
                    "score":   f.get("score",3),
                    "tickers": tickers,
                    "date":    date,
                    "permalink": f"/domain/{r['id']}/{date}?lang={lang}#finding-{i}",
                })
    # Sort by score desc
    all_findings.sort(key=lambda x: x["score"], reverse=True)
    # Top tickers across all findings
    from collections import Counter
    ticker_counts = Counter(t for f in all_findings for t in f["tickers"])
    top_tickers = [t for t, _ in ticker_counts.most_common(12)]
    return render_template("terminal.html",
        lang=lang, researchers=RESEARCHERS, date=date,
        all_findings=all_findings,
        top_tickers=top_tickers)

# ── LIVE MARKET DATA ─────────────────────────────────────────────────────────
def _fetch_live_markets():
    result = {"crypto": [], "commodities": [], "fear_greed": {}, "central_banks": [], "ts": int(time.time())}
    # CoinGecko crypto prices
    try:
        r = http_requests.get(
            "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=bitcoin,ethereum,solana,ripple,hyperliquid,zcash,pump-fun&order=market_cap_desc&sparkline=false&price_change_percentage=24h",
            timeout=8, headers={"User-Agent": "Mozilla/5.0"}
        )
        for c in r.json():
            result["crypto"].append({
                "symbol": {"pump-fun": "PUMP"}.get(c["symbol"], c["symbol"].upper()),
                "name": c["name"],
                "price": c["current_price"],
                "change_24h": round(c.get("price_change_percentage_24h") or 0, 2)
            })
    except Exception as e:
        print(f"CoinGecko err: {e}")
    # Yahoo Finance commodities
    _COMM = {"CL=F": "OIL", "GC=F": "GOLD", "NG=F": "NAT GAS", "ZW=F": "WHEAT"}
    _YF_H = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    for ticker, label in _COMM.items():
        try:
            r = http_requests.get(
                f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=2d",
                timeout=8, headers=_YF_H
            )
            meta = r.json()["chart"]["result"][0]["meta"]
            price = meta.get("regularMarketPrice") or meta.get("previousClose") or 0
            prev  = meta.get("previousClose") or price
            chg   = round(((price - prev) / prev * 100) if prev else 0, 2)
            result["commodities"].append({"symbol": ticker, "name": label, "price": price, "change_pct": chg})
        except Exception as e:
            print(f"YF {ticker} err: {e}")
    # Alternative.me Fear & Greed Index
    try:
        r = http_requests.get("https://api.alternative.me/fng/?limit=1", timeout=8)
        d = r.json()["data"][0]
        result["fear_greed"] = {"value": int(d["value"]), "label": d["value_classification"], "ts": d["timestamp"]}
    except Exception as e:
        print(f"FnG err: {e}")
    # BIS central bank policy rates
    try:
        r = http_requests.get(
            "https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CBPOL_D/1.0/D..?startPeriod=2025-01-01&format=jsondata",
            timeout=10, headers={"Accept": "application/json"}
        )
        js = r.json()
        series = js.get("data", {}).get("dataSets", [{}])[0].get("series", {})
        dims   = js.get("data", {}).get("structure", {}).get("dimensions", {}).get("series", [])
        curr_dim = next((d for d in dims if d.get("id") == "REF_AREA"), None)
        if curr_dim:
            curr_vals = curr_dim.get("values", [])
            _BANKS = {"US": ("USD","Fed"), "XM": ("EUR","ECB"), "GB": ("GBP","BoE"), "JP": ("JPY","BoJ"), "CN": ("CNY","PBoC"), "AU": ("AUD","RBA")}
            for idx, cval in enumerate(curr_vals):
                cid = cval.get("id", "")
                if cid in _BANKS:
                    for sk, sv in series.items():
                        parts = sk.split(":")
                        if len(parts) > 1 and parts[1] == str(idx):
                            obs = sv.get("observations", {})
                            if obs:
                                latest_key = max(obs.keys(), key=lambda x: int(x))
                                rate_val = obs[latest_key][0]
                                if rate_val is not None:
                                    sym, bank = _BANKS[cid]
                                    result["central_banks"].append({"currency": sym, "bank": bank, "rate": round(float(rate_val), 2)})
                            break
    except Exception as e:
        print(f"BIS err: {e}")
    return result

@app.route("/api/live/markets")
def api_live_markets():
    cached = _pm_cached("live_markets", 300)
    if cached:
        return flask_jsonify(cached)
    data = _fetch_live_markets()
    _pm_set("live_markets", data)
    return flask_jsonify(data)


# ── LIVE EVENT DATA (USGS + NASA EONET) ──────────────────────────────────────
def _fetch_live_events():
    result = {"earthquakes": [], "eonet": [], "ts": int(time.time())}
    # USGS earthquakes M4.5+
    try:
        r = http_requests.get(
            "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&minmagnitude=4.5&limit=50&orderby=time",
            timeout=8
        )
        for feat in r.json().get("features", []):
            props  = feat["properties"]
            coords = feat["geometry"]["coordinates"]
            result["earthquakes"].append({
                "lng": coords[0], "lat": coords[1], "depth": round(coords[2], 1),
                "mag": props["mag"], "place": props.get("place") or "Unknown",
                "time_ms": props["time"]
            })
    except Exception as e:
        print(f"USGS err: {e}")
    # NASA EONET open events
    try:
        r = http_requests.get("https://eonet.gsfc.nasa.gov/api/v3/events?status=open&limit=30", timeout=8)
        for ev in r.json().get("events", []):
            geom = ev.get("geometry") or []
            if not geom:
                continue
            g = geom[-1] if isinstance(geom, list) else geom
            coords = g.get("coordinates")
            if not coords:
                continue
            if isinstance(coords[0], list):
                coords = coords[0]
            cat      = (ev.get("categories") or [{}])[0].get("title", "Other")
            date_str = g.get("date", "") if isinstance(geom, list) else ""
            result["eonet"].append({
                "lat": coords[1], "lng": coords[0],
                "title": ev["title"], "category": cat, "date": date_str
            })
    except Exception as e:
        print(f"EONET err: {e}")
    return result

@app.route("/api/live/events")
def api_live_events():
    cached = _pm_cached("live_events", 600)
    if cached:
        return flask_jsonify(cached)
    data = _fetch_live_events()
    _pm_set("live_events", data)
    return flask_jsonify(data)


# ── PHASE 2: ACLED ───────────────────────────────────────────────────────────
def _fetch_acled_events():
    """Real conflict events from ACLED — requires ACLED_ACCESS_TOKEN env var."""
    key   = os.environ.get("ACLED_ACCESS_TOKEN", "")
    email = os.environ.get("ACLED_EMAIL", "")
    if not key or not email:
        return {"events": [], "status": "no_key", "ts": int(time.time())}
    from datetime import datetime, timedelta
    today = datetime.utcnow().strftime("%Y-%m-%d")
    past  = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
    try:
        r = http_requests.get(
            "https://acleddata.com/api/acled/read",
            params={
                "key": key, "email": email, "limit": 150,
                "fields": "event_date|event_type|sub_event_type|actor1|actor2|country|latitude|longitude|fatalities|notes|source",
                "event_date": f"{past}|{today}", "event_date_where": "BETWEEN",
                "event_type": "Battles:Explosions/Remote violence:Violence against civilians:Riots",
            },
            timeout=10
        )
        data = r.json().get("data", [])
        events = []
        for ev in data:
            try:
                lat = float(ev.get("latitude") or 0)
                lng = float(ev.get("longitude") or 0)
                if lat == 0 and lng == 0:
                    continue
                events.append({
                    "lat": lat, "lng": lng,
                    "type": ev.get("event_type", ""),
                    "sub_type": ev.get("sub_event_type", ""),
                    "actor1": ev.get("actor1", ""),
                    "actor2": ev.get("actor2", ""),
                    "country": ev.get("country", ""),
                    "fatalities": int(ev.get("fatalities") or 0),
                    "notes": (ev.get("notes") or "")[:200],
                    "date": ev.get("event_date", ""),
                    "source": ev.get("source", ""),
                })
            except Exception:
                continue
        return {"events": events, "status": "ok", "count": len(events), "ts": int(time.time())}
    except Exception as e:
        print(f"ACLED err: {e}")
        return {"events": [], "status": "error", "ts": int(time.time())}

@app.route("/api/live/acled")
def api_live_acled():
    cached = _pm_cached("live_acled", 900)
    if cached:
        return flask_jsonify(cached)
    data = _fetch_acled_events()
    _pm_set("live_acled", data)
    return flask_jsonify(data)


# ── PHASE 2: FRED MACRO ──────────────────────────────────────────────────────
_FRED_SERIES = {
    "DGS2":    {"label": "2Y Yield",     "unit": "%"},
    "DGS10":   {"label": "10Y Yield",    "unit": "%"},
    "DGS30":   {"label": "30Y Yield",    "unit": "%"},
    "CPIAUCSL":{"label": "CPI YoY",      "unit": "%"},
    "M2SL":    {"label": "M2 Supply",    "unit": "B"},
    "UNRATE":  {"label": "Unemployment", "unit": "%"},
    "FEDFUNDS":{"label": "Fed Funds",    "unit": "%"},
}

def _fetch_fred_macro():
    key = os.environ.get("FRED_API_KEY", "")
    if not key:
        return {"series": [], "status": "no_key", "ts": int(time.time())}
    series_out = []
    for sid, meta in _FRED_SERIES.items():
        try:
            r = http_requests.get(
                "https://api.stlouisfed.org/fred/series/observations",
                params={"series_id": sid, "api_key": key, "file_type": "json",
                        "limit": 2, "sort_order": "desc"},
                timeout=8
            )
            obs = r.json().get("observations", [])
            if obs:
                val  = float(obs[0]["value"]) if obs[0]["value"] != "." else None
                prev = float(obs[1]["value"]) if len(obs) > 1 and obs[1]["value"] != "." else val
                chg  = round(val - prev, 3) if val is not None and prev is not None else 0
                series_out.append({
                    "id": sid, "label": meta["label"], "unit": meta["unit"],
                    "value": round(val, 3) if val is not None else None,
                    "change": chg, "date": obs[0]["date"]
                })
        except Exception as e:
            print(f"FRED {sid} err: {e}")
    return {"series": series_out, "status": "ok", "ts": int(time.time())}

@app.route("/api/live/macro")
def api_live_macro():
    cached = _pm_cached("live_macro", 3600)
    if cached:
        return flask_jsonify(cached)
    data = _fetch_fred_macro()
    _pm_set("live_macro", data)
    return flask_jsonify(data)


# ── PHASE 2: NASA FIRMS (Active Fires) ───────────────────────────────────────
def _fetch_firms_fires():
    key = os.environ.get("NASA_FIRMS_API_KEY", "")
    if not key:
        return {"fires": [], "status": "no_key", "ts": int(time.time())}
    try:
        r = http_requests.get(
            f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{key}/VIIRS_SNPP_NRT/-180,-90,180,90/1",
            timeout=15
        )
        fires = []
        for line in r.text.strip().split("\n")[1:]:  # skip header
            parts = line.split(",")
            if len(parts) < 9:
                continue
            try:
                fires.append({
                    "lat": float(parts[0]), "lng": float(parts[1]),
                    "brightness": float(parts[2]) if parts[2] else 0,
                    "date": parts[5], "confidence": parts[8].strip(),
                })
            except (ValueError, IndexError):
                continue
        return {"fires": fires[:500], "status": "ok", "count": len(fires), "ts": int(time.time())}
    except Exception as e:
        print(f"FIRMS err: {e}")
        return {"fires": [], "status": "error", "ts": int(time.time())}

@app.route("/api/live/fires")
def api_live_fires():
    cached = _pm_cached("live_fires", 1800)
    if cached:
        return flask_jsonify(cached)
    data = _fetch_firms_fires()
    _pm_set("live_fires", data)
    return flask_jsonify(data)


# ── PHASE 2: CLOUDFLARE RADAR (Internet Outages) ─────────────────────────────
def _fetch_cf_outages():
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
    if not token:
        return {"outages": [], "status": "no_key", "ts": int(time.time())}
    try:
        r = http_requests.get(
            "https://api.cloudflare.com/client/v4/radar/annotations/outages",
            params={"limit": 25, "dateRange": "7d"},
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            timeout=8
        )
        items = r.json().get("result", {}).get("annotations", [])
        outages = []
        for item in items:
            outages.append({
                "title": item.get("title", ""),
                "description": item.get("description", ""),
                "country": item.get("locations", [{}])[0].get("country", "") if item.get("locations") else "",
                "start": item.get("startDate", ""),
                "end": item.get("endDate", ""),
                "type": item.get("type", ""),
            })
        return {"outages": outages, "status": "ok", "count": len(outages), "ts": int(time.time())}
    except Exception as e:
        print(f"CF Radar err: {e}")
        return {"outages": [], "status": "error", "ts": int(time.time())}

@app.route("/api/live/outages")
def api_live_outages():
    cached = _pm_cached("live_outages", 1800)
    if cached:
        return flask_jsonify(cached)
    data = _fetch_cf_outages()
    _pm_set("live_outages", data)
    return flask_jsonify(data)


# ── PHASE 2: OTX AlienVault (Cyber Threats) ──────────────────────────────────
def _fetch_otx_threats():
    key = os.environ.get("OTX_API_KEY", "")
    if not key:
        return {"pulses": [], "status": "no_key", "ts": int(time.time())}
    try:
        r = http_requests.get(
            "https://otx.alienvault.com/api/v1/pulses/subscribed",
            params={"limit": 20},
            headers={"X-OTX-API-KEY": key},
            timeout=8
        )
        pulses = []
        for p in r.json().get("results", []):
            pulses.append({
                "name": p.get("name", ""),
                "description": (p.get("description") or "")[:200],
                "tags": p.get("tags", [])[:5],
                "adversary": p.get("adversary", ""),
                "malware_families": p.get("malware_families", [])[:3],
                "targeted_countries": p.get("targeted_countries", [])[:5],
                "indicators_count": p.get("indicators_count", 0),
                "modified": p.get("modified", ""),
            })
        return {"pulses": pulses, "status": "ok", "count": len(pulses), "ts": int(time.time())}
    except Exception as e:
        print(f"OTX err: {e}")
        return {"pulses": [], "status": "error", "ts": int(time.time())}

@app.route("/api/live/cyber")
def api_live_cyber():
    cached = _pm_cached("live_cyber", 3600)
    if cached:
        return flask_jsonify(cached)
    data = _fetch_otx_threats()
    _pm_set("live_cyber", data)
    return flask_jsonify(data)


# ── PHASE 2: FINNHUB (Stock Quotes) ──────────────────────────────────────────
_FINNHUB_SYMBOLS = {
    "NVDA": "NVIDIA", "TSLA": "Tesla", "SPY": "S&P 500",
    "QQQ": "Nasdaq", "LMT": "Lockheed", "RTX": "Raytheon",
    "GLD": "Gold ETF", "IBIT": "BTC ETF",
}

def _fetch_finnhub_quotes():
    key = os.environ.get("FINNHUB_API_KEY", "")
    if not key:
        return {"quotes": [], "status": "no_key", "ts": int(time.time())}
    quotes = []
    for symbol, name in _FINNHUB_SYMBOLS.items():
        try:
            r = http_requests.get(
                "https://finnhub.io/api/v1/quote",
                params={"symbol": symbol, "token": key},
                timeout=6
            )
            d = r.json()
            if d.get("c"):
                chg_pct = round(((d["c"] - d["pc"]) / d["pc"] * 100) if d.get("pc") else 0, 2)
                quotes.append({
                    "symbol": symbol, "name": name,
                    "price": round(d["c"], 2),
                    "change_pct": chg_pct,
                    "high": round(d.get("h", 0), 2),
                    "low":  round(d.get("l", 0), 2),
                })
        except Exception as e:
            print(f"Finnhub {symbol} err: {e}")
    return {"quotes": quotes, "status": "ok", "ts": int(time.time())}

@app.route("/api/live/stocks")
def api_live_stocks():
    cached = _pm_cached("live_stocks", 300)
    if cached:
        return flask_jsonify(cached)
    data = _fetch_finnhub_quotes()
    _pm_set("live_stocks", data)
    return flask_jsonify(data)


# ── PHASE 2: EIA (Energy Data) ───────────────────────────────────────────────
def _fetch_eia_energy():
    key = os.environ.get("EIA_API_KEY", "")
    if not key:
        return {"series": [], "status": "no_key", "ts": int(time.time())}
    _EIA_SERIES = [
        ("PET.RWTC.D",  "WTI Crude Oil", "$/bbl"),
        ("NG.RNGWHHD.D","Henry Hub Gas",  "$/MMBtu"),
        ("PET.RBRTE.D", "Brent Crude",   "$/bbl"),
    ]
    series_out = []
    for sid, label, unit in _EIA_SERIES:
        try:
            r = http_requests.get(
                "https://api.eia.gov/v2/seriesid/" + sid,
                params={"api_key": key, "data[]": "value", "sort[0][column]": "period",
                        "sort[0][direction]": "desc", "length": 2},
                timeout=8
            )
            obs = r.json().get("response", {}).get("data", [])
            if obs:
                val  = float(obs[0]["value"]) if obs[0].get("value") not in (None, "") else None
                prev = float(obs[1]["value"]) if len(obs) > 1 and obs[1].get("value") not in (None, "") else val
                chg  = round(((val - prev) / prev * 100) if val and prev else 0, 2)
                series_out.append({"id": sid, "label": label, "unit": unit,
                                   "value": round(val, 2) if val else None,
                                   "change_pct": chg, "date": obs[0].get("period","")})
        except Exception as e:
            print(f"EIA {sid} err: {e}")
    return {"series": series_out, "status": "ok", "ts": int(time.time())}

@app.route("/api/live/energy")
def api_live_energy():
    cached = _pm_cached("live_energy", 3600)
    if cached:
        return flask_jsonify(cached)
    data = _fetch_eia_energy()
    _pm_set("live_energy", data)
    return flask_jsonify(data)


# ── PHASE 2: WTO (Tariff & Trade Data) ───────────────────────────────────────
def _fetch_wto_tariffs():
    key = os.environ.get("WTO_API_KEY", "")
    if not key:
        return {"tariffs": [], "status": "no_key", "ts": int(time.time())}
    # MFN applied tariff rates for US(840), China(156), EU(097), UK(826)
    try:
        r = http_requests.get(
            "https://api.wto.org/timeseries/v1/data",
            params={"i": "TP_A_0020", "r": "840,156,097,826,392",
                    "p": "000", "ps": "2023,2022", "fmt": "json", "lang": 1, "head": "H"},
            headers={"Ocp-Apim-Subscription-Key": key},
            timeout=10
        )
        raw = r.json()
        _COUNTRIES = {"840": "USA", "156": "China", "097": "EU", "826": "UK", "392": "Japan"}
        tariffs = []
        for row in raw.get("Dataset", []):
            rc = str(row.get("ReporterCode", ""))
            if rc in _COUNTRIES:
                tariffs.append({
                    "reporter": _COUNTRIES[rc],
                    "year": row.get("Year", ""),
                    "rate": round(float(row.get("Value", 0)), 2),
                    "product": row.get("ProductOrSectorCode", "All"),
                })
        # Keep latest per country
        seen = {}
        for t in sorted(tariffs, key=lambda x: x["year"], reverse=True):
            if t["reporter"] not in seen:
                seen[t["reporter"]] = t
        return {"tariffs": list(seen.values()), "status": "ok", "ts": int(time.time())}
    except Exception as e:
        print(f"WTO err: {e}")
        return {"tariffs": [], "status": "error", "ts": int(time.time())}

@app.route("/api/live/tariffs")
def api_live_tariffs():
    cached = _pm_cached("live_tariffs", 86400)  # 24h — annual data
    if cached:
        return flask_jsonify(cached)
    data = _fetch_wto_tariffs()
    _pm_set("live_tariffs", data)
    return flask_jsonify(data)


# ── PHASE 2: STATUS (shows which keys are configured) ────────────────────────
@app.route("/api/live/status")
def api_live_status():
    _KEYS = {
        "ACLED":       ("ACLED_ACCESS_TOKEN", "acleddata.com/data/data-export-tool"),
        "FRED":        ("FRED_API_KEY",        "fred.stlouisfed.org/docs/api/api_key.html"),
        "NASA_FIRMS":  ("NASA_FIRMS_API_KEY",  "firms.modaps.eosdis.nasa.gov/api"),
        "Cloudflare":  ("CLOUDFLARE_API_TOKEN","dash.cloudflare.com/profile/api-tokens"),
        "OTX":         ("OTX_API_KEY",         "otx.alienvault.com"),
        "Finnhub":     ("FINNHUB_API_KEY",     "finnhub.io/dashboard"),
        "EIA":         ("EIA_API_KEY",         "eia.gov/opendata/register.php"),
        "WTO":         ("WTO_API_KEY",         "api.wto.org"),
    }
    status = {}
    for name, (env, url) in _KEYS.items():
        status[name] = {
            "configured": bool(os.environ.get(env)),
            "env_var": env,
            "register_url": f"https://{url}",
        }
    return flask_jsonify({"apis": status, "ts": int(time.time())})


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
