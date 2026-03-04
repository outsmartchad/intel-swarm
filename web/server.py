#!/usr/bin/env python3
"""Intel Swarm — Intelligence News Dashboard"""

import os, glob, re
from flask import Flask, render_template, abort, request
import markdown as md_lib

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RESEARCHERS = [
    ("crypto",      "🪙", "Crypto",       "加密貨幣"),
    ("war",         "⚔️", "War",          "戰爭"),
    ("macro",       "📊", "Macro",        "宏觀"),
    ("ai-agents",   "🤖", "AI Agents",    "AI 代理"),
    ("singularity", "🧠", "Singularity",  "奇點"),
    ("quant",       "📈", "Quant",        "量化"),
    ("westeast",    "🌏", "West-East",    "東西方"),
    ("regulatory",  "⚖️", "Regulatory",  "監管"),
    ("power",       "🕴️", "Power",       "權力"),
    ("psyops",      "📡", "Psyops",       "心理戰"),
    ("blackbudget", "🖤", "Black Budget", "黑色預算"),
    ("conspiracy",  "🕳️", "Conspiracy",  "陰謀"),
    ("epstein",     "📁", "Epstein",      "愛潑斯坦"),
    ("emerging",    "🌍", "Emerging",     "新興市場"),
    ("culture",     "🎭", "Culture",      "文化"),
]

app = Flask(__name__)

def render_md(text):
    if not text: return ""
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
    return sorted(set(os.path.basename(f).replace(".md","") for f in files), reverse=True)

def get_latest_date():
    d = get_dates(); return d[0] if d else "2026-03-04"

def extract_findings(raw):
    """Parse researcher markdown → list of {title, body} dicts"""
    if not raw: return []
    findings = []
    # Match bold **title** — body pattern in bullet lists
    pattern = re.finditer(r'\*\*(.+?)\*\*[:\s—–-]*(.+?)(?=\n[-*]|\n\n|\Z)', raw, re.DOTALL)
    for m in pattern:
        title = m.group(1).strip()
        body = re.sub(r'\s+', ' ', m.group(2).strip())[:240]
        if len(title) > 10 and len(title) < 200:
            findings.append({"title": title, "body": body})
    return findings[:5]

def extract_headline(raw):
    """Get first strong finding title"""
    findings = extract_findings(raw)
    return findings[0]["title"] if findings else None

def extract_edge(raw):
    """Extract Edge Signal section"""
    if not raw: return None
    m = re.search(r'##\s*Edge Signal\s*\n(.+?)(?=\n##|\Z)', raw, re.DOTALL)
    if m: return re.sub(r'\s+', ' ', m.group(1).strip())[:300]
    return None

def get_researcher_data(rid, date, lang="en"):
    raw = read_file(f"{BASE}/researchers/{rid}/findings/{date}.md", lang)
    threads = read_file(f"{BASE}/researchers/{rid}/memory/threads.md", lang)
    sources = read_file(f"{BASE}/researchers/{rid}/memory/sources.md")
    return {
        "raw": raw,
        "html": render_md(raw),
        "findings": extract_findings(raw),
        "headline": extract_headline(raw),
        "edge": extract_edge(raw),
        "threads": render_md(threads),
        "sources": render_md(sources),
        "filed": raw is not None,
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

    # Parse synthesis headline
    syn_headline = None
    if synthesis_raw:
        m = re.search(r'##\s*The Connective Thread:\s*(.+)', synthesis_raw)
        syn_headline = m.group(1).strip() if m else "Intelligence Synthesis"

    # Build domain cards
    domains = []
    for rid, emoji, name, zh_name in RESEARCHERS:
        data = get_researcher_data(rid, date, lang)
        display_name = zh_name if lang == "zh" else name
        domains.append({
            "id": rid, "emoji": emoji, "name": display_name,
            **data
        })

    # Chief top call
    chief_action = None
    if chief_raw:
        m = re.search(r'##.*?Today.*?\n(.+?)(?=\n##|\Z)', chief_raw, re.DOTALL|re.IGNORECASE)
        if m:
            chief_action = re.sub(r'\s+', ' ', m.group(1).strip())[:400]

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
    _, emoji, name, zh_name = lookup[rid]

    data = get_researcher_data(rid, date, lang)

    # All dates for this researcher
    all_dates = sorted(set(
        os.path.basename(f).replace(".md","")
        for f in glob.glob(f"{BASE}/researchers/{rid}/findings/2026-*.md")
    ), reverse=True)

    display_name = zh_name if lang == "zh" else name
    return render_template("domain.html",
        rid=rid, emoji=emoji, name=display_name,
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
    for rid, emoji, name, zh_name in RESEARCHERS:
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
