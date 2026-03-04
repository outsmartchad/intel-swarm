#!/usr/bin/env python3
"""Intel Swarm — Intelligence News Dashboard"""

import os, glob, re, json, random, hashlib
from flask import Flask, render_template, abort, request, make_response
import markdown as md_lib

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RESEARCHERS = [
    ("culture",     "🎭", "Culture",      "文化",     "#7c3aed,#a855f7"),
    ("emerging",    "🌍", "Emerging",     "新興市場", "#065f46,#10b981"),
    ("ai-agents",   "🤖", "AI Agents",    "AI 代理",  "#1e40af,#3b82f6"),
    ("crypto",      "🪙", "Crypto",       "加密貨幣", "#92400e,#f59e0b"),
    ("war",         "⚔️", "War",          "戰爭",     "#7f1d1d,#ef4444"),
    ("macro",       "📊", "Macro",        "宏觀",     "#164e63,#06b6d4"),
    ("singularity", "🧠", "Singularity",  "奇點",     "#4c1d95,#8b5cf6"),
    ("quant",       "📈", "Quant",        "量化",     "#713f12,#eab308"),
    ("westeast",    "🌏", "West-East",    "東西方",   "#134e4a,#14b8a6"),
    ("regulatory",  "⚖️", "Regulatory",  "監管",     "#1e3a5f,#64748b"),
    ("power",       "🕴️", "Power",       "權力",     "#450a0a,#dc2626"),
    ("psyops",      "📡", "Psyops",       "心理戰",   "#500724,#ec4899"),
    ("blackbudget", "🖤", "Black Budget", "黑色預算", "#0c0a09,#44403c"),
    ("conspiracy",  "🕳️", "Conspiracy",  "陰謀",     "#14532d,#4ade80"),
    # ("epstein",  "📁", "Epstein",      "愛潑斯坦","#1c1917,#78716c"),
]

app = Flask(__name__, static_folder='static', static_url_path='/static')

@app.after_request
def no_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

KNOWN_SITES = {
    "theguardian.com": "The Guardian", "guardian.com": "The Guardian",
    "nytimes.com": "NY Times", "wsj.com": "WSJ", "ft.com": "FT",
    "bloomberg.com": "Bloomberg", "reuters.com": "Reuters",
    "bbc.com": "BBC", "bbc.co.uk": "BBC", "washingtonpost.com": "WashPost",
    "cnbc.com": "CNBC", "cnbcafrica.com": "CNBC Africa",
    "techcrunch.com": "TechCrunch", "wired.com": "Wired",
    "fortune.com": "Fortune", "forbes.com": "Forbes", "time.com": "Time",
    "economist.com": "The Economist", "apnews.com": "AP News",
    "axios.com": "Axios", "politico.com": "Politico",
    "coindesk.com": "CoinDesk", "cointelegraph.com": "CoinTelegraph",
    "theblock.co": "The Block", "decrypt.co": "Decrypt",
    "nature.com": "Nature", "science.org": "Science",
    "wikipedia.org": "Wikipedia", "arxiv.org": "arXiv",
    "understandingwar.org": "ISW", "defenseone.com": "Defense One",
    "wapo.com": "WashPost", "theintercept.com": "The Intercept",
    "propublica.org": "ProPublica", "bellingcat.com": "Bellingcat",
}

def url_to_label(url):
    """Extract a human-readable label from a URL."""
    try:
        m = re.search(r'https?://(?:www\.)?([^/]+)', url)
        if not m: return "Source"
        domain = m.group(1).lower()
        # Check known sites (longest match first)
        for key in sorted(KNOWN_SITES, key=len, reverse=True):
            if domain.endswith(key) or domain == key:
                return KNOWN_SITES[key]
        # Unknown: use domain name without TLD, capitalize
        name = domain.split('.')[0]
        return name.replace('-', ' ').title()
    except:
        return "Source"

def render_md(text):
    if not text: return ""
    # Convert [https://url] → [Label](url)
    def replace_bracket_url(m):
        url = m.group(1)
        return f"[{url_to_label(url)}]({url})"
    text = re.sub(r'\[(?!.*\]\()(https?://[^\]]+)\]', replace_bracket_url, text)
    # Convert bare https://url (not already in markdown link) → [Label](url)
    def replace_bare_url(m):
        url = m.group(0).rstrip('.,;)')
        return f"[{url_to_label(url)}]({url})"
    text = re.sub(r'(?<!\()(?<!\[)https?://\S+', replace_bare_url, text)
    return md_lib.markdown(text, extensions=["extra", "nl2br", "sane_lists"])

def read_file(path, lang="en"):
    # Try Chinese version first if lang=zh
    if lang == "zh":
        zh_path = path.replace(".md", ".zh.md")
        try:
            with open(zh_path) as f: return f.read()
        except: pass
    try:
        with open(path) as f: return f.read()
    except: return None

def get_lang():
    return request.args.get("lang", "en")

def get_dates():
    files = glob.glob(f"{BASE}/synthesis/findings/2026-*.md")
    # Exclude .zh.md translated files — only want base date files
    dates = set()
    for f in files:
        name = os.path.basename(f)
        if name.endswith(".zh.md"): continue
        dates.add(name.replace(".md", ""))
    return sorted(dates, reverse=True)

def get_latest_date():
    d = get_dates(); return d[0] if d else "2026-03-04"

def extract_findings(raw):
    """Parse researcher markdown → list of {title, body, score} dicts"""
    if not raw: return []
    findings = []
    pattern = re.finditer(r'\*\*(.+?)\*\*[:\s—–-]*(.+?)(?=\n[-*]|\n\n|\Z)', raw, re.DOTALL)
    for m in pattern:
        title = m.group(1).strip()
        body_raw = m.group(2).strip()
        # Extract inline score tag [SCORE:N] or [★★★★☆] if present
        score = 3  # default
        score_m = re.search(r'\[SCORE[:\s]*([1-5])\]', body_raw, re.IGNORECASE)
        if score_m:
            score = int(score_m.group(1))
            body_raw = body_raw[:score_m.start()].strip()
        # Boost score for keywords
        elif any(k in title.lower() for k in ['breaking','critical','urgent','war','attack','collapse','ban','crash']):
            score = 4
        body = re.sub(r'\s+', ' ', body_raw)[:240]
        if len(title) > 10 and len(title) < 200:
            findings.append({"title": title, "body": body, "score": score})
    return findings[:5]

def top_score(findings):
    """Get highest significance score from findings list"""
    if not findings: return 3
    return max(f.get("score", 3) for f in findings)

def extract_headline(raw):
    """Get first strong finding title — prefers Chinese text if available"""
    findings = extract_findings(raw)
    if not findings: return None
    for f in findings:
        title = f["title"]
        body = f.get("body", "")
        # If title has Chinese chars, use it directly
        if any('\u4e00' <= c <= '\u9fff' for c in title):
            return title
        # Title is English (technical term) — try to get first Chinese sentence from body
        zh_match = re.search(r'[\u4e00-\u9fff][^\n]{10,}', body)
        if zh_match:
            return zh_match.group(0)[:120]
        return title  # fallback to English title
    return findings[0]["title"]

def extract_edge(raw):
    """Extract Edge Signal section (EN or ZH)"""
    if not raw: return None
    m = re.search(r'##\s*(?:Edge Signal|邊緣信號|边缘信号|邊緣訊號)\s*\n(.+?)(?=\n##|\Z)', raw, re.DOTALL)
    if m: return re.sub(r'\s+', ' ', m.group(1).strip())[:300]
    return None

def extract_tail_sections(raw):
    """Extract sections after the main findings (Edge Signal, Connects To, etc.)"""
    if not raw: return ""
    m = re.search(
        r'(##\s*(?:Edge Signal|邊緣信號|Connects To|連接到|連結至|相關連結|Edge|Signal).+)',
        raw, re.DOTALL | re.IGNORECASE
    )
    return m.group(1).strip() if m else ""

def assign_layout(domains, date):
    """Assign BBC/CNBC-style card sizes — hero rotates daily by date seed + score."""
    seed = int(hashlib.md5(date.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)

    scored = sorted(range(len(domains)), key=lambda i: domains[i].get("score", 3), reverse=True)
    # Hero: pick from top-3 scorers (date-seeded)
    hero_pool = scored[:min(3, len(scored))]
    hero_i = rng.choice(hero_pool)
    remaining = [i for i in scored if i != hero_i]
    # Featured: pick from next top-3
    feat_pool = remaining[:min(3, len(remaining))]
    feat_i = rng.choice(feat_pool)
    rest = [i for i in remaining if i != feat_i]

    for i, d in enumerate(domains):
        if i == hero_i:     d["layout"] = "hero"
        elif i == feat_i:   d["layout"] = "featured"
        elif i in rest[:3]: d["layout"] = "medium"
        else:               d["layout"] = "small"
    return domains

def render_findings_cards(findings):
    """Render findings as image cards for the domain article view."""
    if not findings: return ""
    parts = []
    for f in findings:
        img_html = ""
        if f.get("image"):
            img_html = f'<div class="fc-img-wrap"><img src="{f["image"]}" class="fc-img" alt="" loading="lazy"></div>'
        title = f.get("title", "")
        body  = f.get("body", "")
        # Render any source links in body
        body_rendered = render_md(body) if body else ""
        score = f.get("score", 3)
        pips = "".join(
            f'<span class="fc-pip {"filled" if i <= score else "empty"}"></span>'
            for i in range(1, 6)
        )
        parts.append(f'''
<div class="finding-card">
  {img_html}
  <div class="fc-content">
    <div class="fc-score">{pips}</div>
    <div class="fc-title">{title}</div>
    <div class="fc-body">{body_rendered}</div>
  </div>
</div>''')
    return "\n".join(parts)

def load_images(rid, date):
    """Load scraped OG images for a researcher's findings."""
    path = f"{BASE}/researchers/{rid}/findings/{date}-images.json"
    try:
        with open(path) as f:
            items = json.load(f)
        # Return as dict: finding_idx → image_path
        return {str(item["finding_idx"]): item["image_path"] for item in items}
    except:
        return {}

def get_researcher_data(rid, date, lang="en"):
    raw = read_file(f"{BASE}/researchers/{rid}/findings/{date}.md", lang)
    threads = read_file(f"{BASE}/researchers/{rid}/memory/threads.md", lang)
    sources = read_file(f"{BASE}/researchers/{rid}/memory/sources.md")
    findings = extract_findings(raw)
    images = load_images(rid, date)
    # Attach image to each finding by index
    for i, f in enumerate(findings):
        f["image"] = images.get(str(i)) or images.get(str(i+1))
    return {
        "raw": raw,
        "html": render_md(raw),
        "findings": findings,
        "findings_cards": render_findings_cards(findings),
        "tail_html": render_md(extract_tail_sections(raw)),
        "headline": extract_headline(raw),
        "edge": extract_edge(raw),
        "threads": render_md(threads),
        "sources": render_md(sources),
        "filed": raw is not None,
        "cover_image": findings[0].get("image") if findings else None,
    }

@app.route("/")
def index():
    return home(get_latest_date())

@app.route("/date/<date>")
def home(date):
    dates = get_dates()
    lang = get_lang()
    synthesis_raw = read_file(f"{BASE}/synthesis/findings/{date}.md", lang)
    chief_raw = read_file(f"{BASE}/chief/findings/{date}.md", lang)

    # Parse synthesis headline (try zh version too)
    syn_headline = None
    if synthesis_raw:
        m = re.search(r'##\s*(?:The Connective Thread:|連接線索：?|主線：?)\s*(.+)', synthesis_raw)
        syn_headline = m.group(1).strip() if m else ("情報綜合" if lang == "zh" else "Intelligence Synthesis")

    # Build domain cards
    domains = []
    for rid, emoji, name, zh_name, colors in RESEARCHERS:
        data = get_researcher_data(rid, date, lang)
        display_name = zh_name if lang == "zh" else name
        findings = data.get("findings", [])
        domains.append({
            "id": rid, "emoji": emoji, "name": display_name,
            "colors": colors, "score": top_score(findings),
            **data
        })

    # Chief top call
    chief_action = None
    if chief_raw:
        m = re.search(r'##.*?Today.*?\n(.+?)(?=\n##|\Z)', chief_raw, re.DOTALL|re.IGNORECASE)
        if m:
            chief_action = re.sub(r'\s+', ' ', m.group(1).strip())[:400]

    domains = assign_layout(domains, date)

    return render_template("home.html",
        date=date, dates=dates, lang=lang,
        synthesis_raw=synthesis_raw,
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
    dates = get_dates()
    lang = get_lang()
    lookup = {r[0]: r for r in RESEARCHERS}
    if rid not in lookup: abort(404)
    _, emoji, name, zh_name, colors = lookup[rid]

    data = get_researcher_data(rid, date, lang)

    # All dates for this researcher
    all_dates = sorted(set(
        os.path.basename(f).replace(".md","")
        for f in glob.glob(f"{BASE}/researchers/{rid}/findings/2026-*.md")
        if not f.endswith(".zh.md")
    ), reverse=True)

    display_name = zh_name if lang == "zh" else name
    return render_template("domain.html",
        rid=rid, emoji=emoji, name=display_name, colors=colors,
        date=date, dates=dates, lang=lang,
        all_dates=all_dates,
        researchers=RESEARCHERS,
        **data
    )

@app.route("/brief")
def brief():
    return brief_date(get_latest_date())

@app.route("/brief/<date>")
def brief_date(date):
    dates = get_dates()
    lang = get_lang()
    synthesis_raw = read_file(f"{BASE}/synthesis/findings/{date}.md", lang)
    chief_raw = read_file(f"{BASE}/chief/findings/{date}.md", lang)
    thesis = read_file(f"{BASE}/synthesis/memory/thesis.md")
    predictions = read_file(f"{BASE}/chief/memory/predictions.md")

    return render_template("brief.html",
        date=date, dates=dates, lang=lang,
        synthesis_html=render_md(synthesis_raw),
        chief_html=render_md(chief_raw),
        thesis_html=render_md(thesis),
        predictions_html=render_md(predictions),
        researchers=RESEARCHERS,
    )

@app.route("/memory")
def memory():
    dates = get_dates()
    thesis = read_file(f"{BASE}/synthesis/memory/thesis.md")
    predictions = read_file(f"{BASE}/chief/memory/predictions.md")
    chief_thesis = read_file(f"{BASE}/chief/memory/thesis.md")

    threads_data = []
    for rid, emoji, name, zh_name, colors in RESEARCHERS:
        t = read_file(f"{BASE}/researchers/{rid}/memory/threads.md")
        threads_data.append({"id": rid, "emoji": emoji, "name": name, "threads": render_md(t)})

    return render_template("memory.html",
        dates=dates,
        thesis=render_md(thesis),
        predictions=render_md(predictions),
        chief_thesis=render_md(chief_thesis),
        threads_data=threads_data,
        researchers=RESEARCHERS,
    )

if __name__ == "__main__":
    import os
    local_ip = os.popen("ipconfig getifaddr en0 2>/dev/null || ifconfig | grep 'inet ' | grep -v 127 | awk '{print $2}' | head -1").read().strip()
    print(f"\n🐝 Intel Swarm")
    print(f"   Local:   http://localhost:5757")
    print(f"   Network: http://{local_ip}:5757\n")
    app.run(host="0.0.0.0", port=5757, debug=False)
