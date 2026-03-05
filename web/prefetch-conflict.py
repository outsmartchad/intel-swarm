#!/usr/bin/env python3
"""
Prefetch conflict events from GDELT and save to a static JSON file.
Run once per hour via cron. The /api/conflict/events endpoint reads this file.
"""
import json, os, sys, zipfile, io, csv
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent.parent
OUT  = BASE / "web" / "static" / "conflict-events.json"

COUNTRY_COORDS = {
    "Iran": (32.4, 53.7), "Ukraine": (49.0, 32.0), "Russia": (61.5, 105.3),
    "Israel": (31.0, 35.0), "Gaza": (31.4, 34.3), "Lebanon": (33.9, 35.5),
    "Syria": (34.8, 38.9), "Iraq": (33.2, 43.7), "Yemen": (15.5, 48.5),
    "China": (35.9, 104.2), "Taiwan": (23.7, 121.0), "North Korea": (40.3, 127.5),
    "South Korea": (36.5, 127.9), "Japan": (36.2, 138.3), "India": (20.6, 79.0),
    "Pakistan": (30.4, 69.3), "Afghanistan": (33.9, 67.7), "Myanmar": (19.2, 96.7),
    "Sudan": (12.9, 30.2), "Ethiopia": (9.1, 40.5), "Somalia": (5.2, 46.2),
    "Mali": (17.6, -2.0), "Nigeria": (9.1, 8.7), "Congo": (-4.0, 21.8),
    "Libya": (26.3, 17.2), "Egypt": (26.8, 30.8), "Turkey": (39.0, 35.2),
    "Saudi Arabia": (24.7, 45.7), "United States": (37.1, -95.7),
    "Mexico": (23.6, -102.6), "Venezuela": (6.4, -66.6), "Colombia": (4.6, -74.1),
    "Thailand": (15.9, 100.9), "Philippines": (12.9, 121.8),
    "Haiti": (18.9, -72.3), "Serbia": (44.0, 21.0), "Kosovo": (42.6, 20.9),
    "Georgia": (42.3, 43.4), "Armenia": (40.1, 45.0), "Azerbaijan": (40.1, 47.6),
    "Palestine": (31.9, 35.2), "Cuba": (21.5, -77.8), "Bangladesh": (23.7, 90.4),
    "Indonesia": (-0.8, 113.9), "Ethiopia": (9.1, 40.5), "Sahel": (13.5, 2.0),
}

CONFLICT_WORDS = {"attack","bomb","kill","shoot","clash","explos","fight","strike","missile",
                  "rocket","assault","ambush","mortar","war","troops","military","shelling",
                  "siege","hostage","gunfir","casualt","airstrike","drone","killed","wounded"}
PROTEST_WORDS  = {"protest","demonstrat","riot","march","rally","blockade","activist","unrest",
                  "uprising","crowd","marche","demonstrators","rallied"}
POLITICAL_WORDS= {"sanction","diplomat","election","coup","summit","president","minister",
                  "parliament","ceasefire","treaty","negotiat","resign","arrest","indict",
                  "tariff","impose"}

def event_type(title):
    t = title.lower()
    for w in CONFLICT_WORDS:
        if w in t: return "CONFLICT"
    for w in PROTEST_WORDS:
        if w in t: return "PROTEST"
    for w in POLITICAL_WORDS:
        if w in t: return "POLITICAL"
    return "OTHER"

def geocode(title):
    t = title
    for name, coords in COUNTRY_COORDS.items():
        if name.lower() in t.lower():
            import random
            return coords[0] + random.uniform(-0.6,0.6), coords[1] + random.uniform(-0.6,0.6), name
    return None, None, ""

def fetch_gdelt_csv():
    """Download and parse the latest GDELT 2.0 events CSV."""
    import urllib.request, time
    # Get the latest file URL from the master list
    with urllib.request.urlopen("http://data.gdeltproject.org/gdeltv2/lastupdate.txt", timeout=10) as resp:
        lines = resp.read().decode().strip().split("\n")
    # First line = export file, second = mentions, third = gkg
    export_url = lines[0].split()[-1]   # e.g. http://data.gdeltproject.org/gdeltv2/20260305120000.export.CSV.zip
    print(f"  Fetching {export_url}")
    with urllib.request.urlopen(export_url, timeout=30) as resp:
        raw = resp.read()
    z = zipfile.ZipFile(io.BytesIO(raw))
    csv_name = z.namelist()[0]
    rows = z.read(csv_name).decode("latin-1").splitlines()

    # GDELT 2.0 export column layout (57 cols):
    # 0=GLOBALEVENTID, 1=SQLDATE, 5=Actor1Name, 11=Actor2Name, 26=EventCode, 27=EventBaseCode,
    # 28=EventRootCode, 34=GoldsteinScale, 37=AvgTone, 53=Actor1Geo_FullName,
    # 57=ActionGeo_FullName, 53=Actor1Geo_Lat, 54=Actor1Geo_Long,
    # 56=ActionGeo_FeatureID, 57=ActionGeo_FullName, 58=ActionGeo_CountryCode,
    # 53=Actor1Geo_Lat, 54=Actor1Geo_Long, 55=Actor1Geo_FeatureID
    # Cols: ActionGeo_Lat=53, ActionGeo_Long=54, ActionGeo_FullName=52, ActionGeo_CountryCode=51
    # Actually GDELT 2.0 has these key columns:
    # [53]=Actor1Geo_Lat [54]=Actor1Geo_Long [56]=ActionGeo_FullName [57]=ActionGeo_CountryCode
    # [30]=NumMentions, [34]=GoldsteinScale (neg=destabilizing)

    events = []
    seen_locs = {}
    reader = csv.reader(rows, delimiter="\t")
    for row in reader:
        # GDELT 2.0: 61 columns
        # Key columns: ActionGeo_Lat=56, ActionGeo_Long=57, ActionGeo_FullName=52,
        #              ActionGeo_CountryCode=53, GoldsteinScale=30, AvgTone=34,
        #              NumMentions=31, EventRootCode=28, Actor1Name=6, Actor2Name=16,
        #              DATEADDED=59, SOURCEURL=60
        if len(row) < 60: continue
        try:
            lat  = float(row[56]) if row[56] else None
            lng  = float(row[57]) if row[57] else None
            geo  = row[52] or ""
            country_code = row[53] or ""
            goldstein = float(row[30]) if row[30] else 0.0
            avg_tone  = float(row[34]) if row[34] else 0.0
            mentions  = int(row[31]) if row[31] else 1
            date_str  = row[1]  # YYYYMMDD
            source_url = row[60] if len(row) > 60 else ""
            actor1 = row[6] or ""
            actor2 = row[16] or ""
            root_code = row[28] or ""
        except (ValueError, IndexError):
            continue
        if not lat or not lng: continue
        # Filter: only negative Goldstein (destabilizing) or high mentions
        if goldstein > -1 and mentions < 3: continue
        title = f"{actor1} — {actor2}" if actor2 and actor1 != actor2 else (actor1 or geo or "Unknown")
        etype = "CONFLICT" if root_code in ("14","15","16","17","18","19","20") else \
                "PROTEST" if root_code in ("14",) else "POLITICAL"
        date_fmt = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}" if len(date_str)==8 else date_str
        events.append({
            "title":   title,
            "url":     source_url,
            "tone":    round(avg_tone, 1),
            "date":    date_fmt,
            "country": country_code,
            "geo":     geo,
            "lat":     round(lat, 3),
            "lng":     round(lng, 3),
            "type":    etype,
            "mentions": mentions,
        })
        if len(events) >= 500: break

    events.sort(key=lambda e: e["tone"])
    return events

def fetch_gdelt_api():
    """Fallback: use GDELT DOC API if CSV fails."""
    import urllib.request, urllib.parse, time
    time.sleep(6)  # GDELT rate limit: 1 req/5s
    params = urllib.parse.urlencode({
        "query": "(war OR conflict OR attack OR bomb OR missile OR strike OR protest OR sanction) sourcelang:english",
        "mode": "ArtList",
        "maxrecords": "250",
        "timespan": "24h",
        "format": "json",
    })
    url = f"https://api.gdeltproject.org/api/v2/doc/doc?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "intel-swarm/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
    articles = data.get("articles") or []
    events = []
    seen = set()
    for a in articles:
        title = (a.get("title") or "").strip()
        url   = a.get("url") or ""
        if not title or url in seen: continue
        seen.add(url)
        lat, lng, country = geocode(title)
        etype = event_type(title)
        tone  = -8.0 if etype == "CONFLICT" else (-4.0 if etype == "PROTEST" else -2.0)
        date_raw = (a.get("seendate") or "")[:8]
        date_fmt = f"{date_raw[:4]}-{date_raw[4:6]}-{date_raw[6:]}" if len(date_raw)==8 else ""
        events.append({
            "title": title, "url": url, "tone": tone,
            "date": date_fmt, "country": country, "geo": country,
            "lat": round(lat, 3) if lat else None,
            "lng": round(lng, 3) if lng else None,
            "type": etype,
        })
    return events

if __name__ == "__main__":
    print("[conflict] Fetching GDELT events…")

    # Use CSV only (DOC API rate limited to 1 req/5s)
    events = []
    try:
        events = fetch_gdelt_csv()
        print(f"  CSV: {len(events)} events")
    except Exception as e:
        print(f"  CSV failed: {e}")

    result = {"events": events, "count": len(events),
              "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    OUT.write_text(json.dumps(result))
    print(f"[conflict] Saved {len(events)} events → {OUT}")
