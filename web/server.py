#!/usr/bin/env python3
"""Intel Swarm — Local Intelligence Dashboard"""

import os
import glob
import json
from datetime import datetime
from flask import Flask, render_template, abort
import markdown

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RESEARCHERS = [
    ("crypto",      "🪙", "Crypto"),
    ("ai-agents",   "🤖", "AI Agents"),
    ("conspiracy",  "🕳️", "Conspiracy"),
    ("epstein",     "📁", "Epstein"),
    ("war",         "⚔️", "War"),
    ("macro",       "📊", "Macro"),
    ("power",       "🕴️", "Power"),
    ("singularity", "🧠", "Singularity"),
    ("psyops",      "📡", "Psyops"),
    ("blackbudget", "🖤", "Black Budget"),
    ("emerging",    "🌍", "Emerging"),
    ("regulatory",  "⚖️", "Regulatory"),
    ("westeast",    "🌏", "West-East"),
    ("quant",       "📈", "Quant"),
    ("culture",     "🎭", "Culture"),
]

app = Flask(__name__)

def md(text):
    return markdown.markdown(text, extensions=["extra", "nl2br"]) if text else ""

def read_file(path):
    try:
        with open(path, "r") as f:
            return f.read()
    except:
        return None

def get_dates():
    files = glob.glob(f"{BASE}/synthesis/findings/2026-*.md")
    dates = sorted(set(
        os.path.basename(f).replace(".md", "") for f in files
    ), reverse=True)
    return dates

def get_latest_date():
    dates = get_dates()
    return dates[0] if dates else datetime.now().strftime("%Y-%m-%d")

@app.route("/")
def index():
    date = get_latest_date()
    return daily(date)

@app.route("/date/<date>")
def daily(date):
    dates = get_dates()
    synthesis_raw = read_file(f"{BASE}/synthesis/findings/{date}.md")
    chief_raw = read_file(f"{BASE}/chief/findings/{date}.md")
    synthesis = md(synthesis_raw)
    chief = md(chief_raw)

    researchers_data = []
    for rid, emoji, name in RESEARCHERS:
        content = read_file(f"{BASE}/researchers/{rid}/findings/{date}.md")
        threads = read_file(f"{BASE}/researchers/{rid}/memory/threads.md")
        researchers_data.append({
            "id": rid, "emoji": emoji, "name": name,
            "content": md(content),
            "threads": md(threads),
            "has_content": content is not None
        })

    thesis = read_file(f"{BASE}/synthesis/memory/thesis.md")
    predictions = read_file(f"{BASE}/chief/memory/predictions.md")

    return render_template("index.html",
        date=date,
        dates=dates,
        synthesis=synthesis,
        chief=chief,
        researchers=researchers_data,
        thesis=md(thesis),
        predictions=md(predictions),
        researchers_list=RESEARCHERS,
    )

@app.route("/memory")
def memory():
    dates = get_dates()
    thesis = read_file(f"{BASE}/synthesis/memory/thesis.md")
    predictions = read_file(f"{BASE}/chief/memory/predictions.md")
    chief_thesis = read_file(f"{BASE}/chief/memory/thesis.md")

    threads_data = []
    for rid, emoji, name in RESEARCHERS:
        t = read_file(f"{BASE}/researchers/{rid}/memory/threads.md")
        threads_data.append({
            "id": rid, "emoji": emoji, "name": name,
            "threads": md(t)
        })

    return render_template("memory.html",
        dates=dates,
        thesis=md(thesis),
        predictions=md(predictions),
        chief_thesis=md(chief_thesis),
        threads_data=threads_data,
        researchers_list=RESEARCHERS,
    )

if __name__ == "__main__":
    local_ip = os.popen("ipconfig getifaddr en0 2>/dev/null || ifconfig | grep 'inet ' | grep -v 127 | awk '{print $2}' | head -1").read().strip()
    print(f"\n🐝 Intel Swarm Dashboard")
    print(f"   Local:   http://localhost:5757")
    print(f"   Network: http://{local_ip}:5757\n")
    app.run(host="0.0.0.0", port=5757, debug=False)
