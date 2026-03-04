#!/usr/bin/env python3
"""Batch scrape OG images for all researchers for a given date."""
import sys, os, subprocess

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRAPER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scrape-images.py")
date = sys.argv[1] if len(sys.argv) > 1 else __import__('datetime').date.today().isoformat()

RESEARCHERS = [
    "culture","emerging","ai-agents","crypto","war","macro",
    "singularity","quant","westeast","regulatory","power",
    "psyops","blackbudget","conspiracy"
]

procs = []
for r in RESEARCHERS:
    f = f"{BASE}/researchers/{r}/findings/{date}.md"
    if os.path.exists(f):
        p = subprocess.Popen(["python3", SCRAPER, f])
        procs.append((r, p))

# Also synthesis + chief
for name in ["synthesis", "chief"]:
    f = f"{BASE}/{name}/findings/{date}.md"
    if os.path.exists(f):
        p = subprocess.Popen(["python3", SCRAPER, f])
        procs.append((name, p))

for name, p in procs:
    p.wait()
    print(f"  {'✓' if p.returncode == 0 else '✗'} {name}")

print(f"Done — {date}")
