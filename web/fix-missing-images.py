#!/usr/bin/env python3
"""
Fix missing images for a given date.
Strategies:
  1. Wikimedia API (for Wikipedia URLs)
  2. Fetch og:image with multiple UAs
  3. Wayback Machine
  4. Homepage fallback
  5. Brave Image Search (if key valid)
  6. Unsplash keyword search (free, no key)
"""

import sys, os, re, json, hashlib, requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

BASE = Path(__file__).resolve().parents[1]
BRAVE_API_KEY = os.environ.get("BRAVE_API_KEY", "")
TIMEOUT = 12

USER_AGENTS = [
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "curl/7.88.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
]
SKIP = ["publication-cover","default-cover","placeholder","logo-only","favicon","apple-touch","blank.","ghost.org/v","generic","1x1","pixel","spacer","tracking"]

def is_usable(url):
    if not url: return False
    low = url.lower()
    return not any(p in low for p in SKIP)

def resolve(img, base):
    if not img: return None
    if img.startswith("//"): return "https:" + img
    if not img.startswith("http"): return urljoin(base, img)
    return img

def og_from_html(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    for prop in ["og:image","twitter:image","twitter:image:src"]:
        tag = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
        if tag and tag.get("content"):
            url = resolve(tag["content"].strip(), base_url)
            if is_usable(url): return url
    for tag in soup.select("article img, main img, .article img, .post-content img"):
        src = tag.get("src") or tag.get("data-src") or tag.get("data-lazy-src")
        if not src: continue
        src = resolve(src, base_url)
        if not src or not src.startswith("http"): continue
        if int(tag.get("width") or 0) < 200: continue
        if is_usable(src): return src
    return None

def fetch_html(url, ua):
    try:
        r = requests.get(url, headers={"User-Agent": ua, "Accept": "text/html"}, timeout=TIMEOUT, allow_redirects=True)
        return r.text if r.status_code == 200 else None
    except: return None

def wikimedia_thumb(wiki_url):
    """Wikimedia API — gets the main page thumbnail for Wikipedia articles."""
    m = re.search(r'wikipedia\.org/wiki/(.+)', wiki_url)
    if not m: return None
    title = requests.utils.unquote(m.group(1)).split("#")[0]
    try:
        r = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action":"query","prop":"pageimages","pithumbsize":800,"titles":title,"format":"json"},
            headers={"User-Agent": "IntelSwarm/1.0 research bot"},
            timeout=10
        )
        pages = r.json().get("query",{}).get("pages",{})
        for p in pages.values():
            thumb = p.get("thumbnail",{}).get("source")
            if thumb: return thumb
    except: pass
    return None

def wayback_image(url):
    try:
        r = requests.get(f"https://archive.org/wayback/available?url={url}", timeout=8)
        snap = r.json().get("archived_snapshots",{}).get("closest",{})
        if snap.get("available") and snap.get("url"):
            html = fetch_html(snap["url"], USER_AGENTS[0])
            if html: return og_from_html(html, snap["url"])
    except: pass
    return None

def homepage_image(url):
    parsed = urlparse(url)
    home = f"{parsed.scheme}://{parsed.netloc}"
    for ua in USER_AGENTS[:2]:
        html = fetch_html(home, ua)
        if html:
            img = og_from_html(html, home)
            if img: return img
    return None

def brave_image(query):
    if not BRAVE_API_KEY: return None
    q = re.sub(r"[^\w\s]", " ", query)[:100].strip()
    try:
        r = requests.get(
            "https://api.search.brave.com/res/v1/images/search",
            headers={"Accept":"application/json","X-Subscription-Token":BRAVE_API_KEY},
            params={"q":q,"count":10,"safesearch":"off"}, timeout=10
        )
        if r.status_code != 200: return None
        for res in r.json().get("results",[]):
            src = res.get("properties",{}).get("url") or res.get("thumbnail",{}).get("src")
            if src and src.startswith("http") and is_usable(src): return src
    except: pass
    return None

def unsplash_image(query):
    """Unsplash unofficial source search — returns a relevant photo URL."""
    q = re.sub(r"[^\w\s]", "+", query)[:80].strip().replace(" ", "+")
    try:
        r = requests.get(
            f"https://source.unsplash.com/800x500/?{q}",
            headers={"User-Agent": USER_AGENTS[3]}, timeout=10, allow_redirects=True
        )
        if r.status_code == 200 and "image" in r.headers.get("Content-Type",""):
            return r.url
    except: pass
    return None

def download(img_url, dest_dir):
    dest_dir.mkdir(parents=True, exist_ok=True)
    name = hashlib.md5(img_url.encode()).hexdigest()[:12]
    ext  = Path(urlparse(img_url).path).suffix.lower()
    if ext not in {".jpg",".jpeg",".png",".gif",".webp"}: ext = ".jpg"
    dest = dest_dir / (name + ext)
    if dest.exists() and dest.stat().st_size > 2048:
        return str(dest)
    try:
        r = requests.get(img_url, headers={"User-Agent": USER_AGENTS[0]}, timeout=TIMEOUT, stream=True)
        if r.status_code != 200: return None
        data = b"".join(r.iter_content(65536))
        if len(data) < 2048: return None
        dest.write_bytes(data)
        return str(dest)
    except: return None

def web_path(disk_path, date_str, rid):
    p = Path(disk_path)
    return f"/static/images/{date_str}/{rid}/{p.name}"

def parse_findings(text):
    findings = []
    for m in re.finditer(r'\*\*(.+?)\*\*[:\s—–-]*(.+?)(?=\n[-*]|\n\n|\Z)', text, re.DOTALL):
        title = m.group(1).strip()
        body  = m.group(2).strip()
        if not (10 < len(title) < 200): continue
        url_m = re.search(r'https?://[^\s\)\]\"\'<>,]+', body)
        url   = url_m.group(0).rstrip(".,;)") if url_m else None
        findings.append((title, url))
        if len(findings) >= 5: break
    return findings

def fix_domain(findings_path):
    findings_path = Path(findings_path)
    date_str = findings_path.stem
    if date_str.endswith(".zh"): date_str = date_str[:-3]
    
    rid = "unknown"
    for i, part in enumerate(findings_path.parts):
        if part == "researchers" and i+1 < len(findings_path.parts):
            rid = findings_path.parts[i+1]; break
        if part in ("synthesis","chief"):
            rid = part; break

    img_dir   = BASE / "web" / "static" / "images" / date_str / rid
    json_path = findings_path.parent / f"{date_str}-images.json"

    # Load existing
    existing = {}
    if json_path.exists():
        try:
            for item in json.loads(json_path.read_text()):
                ipath = item.get("image_path","")
                disk  = BASE / "web" / ipath.lstrip("/")
                if ipath and disk.exists() and disk.stat().st_size > 2048:
                    existing[item["finding_idx"]] = item
        except: pass

    text     = findings_path.read_text()
    findings = parse_findings(text)
    need     = [i for i in range(len(findings)) if i not in existing]

    if not need:
        print(f"  [{rid}] ✓ All images present")
        return

    print(f"  [{rid}] Missing {len(need)}/{len(findings)}")
    changed = False

    for idx in need:
        title, url = findings[idx]
        print(f"    [{idx}] {title[:60]}")
        wp = None

        # Strategy 1: Wikimedia for Wikipedia URLs
        if url and "wikipedia.org" in url:
            img_url = wikimedia_thumb(url)
            if img_url:
                path = download(img_url, img_dir)
                if path:
                    wp = web_path(path, date_str, rid)
                    print(f"         ✓ Wikimedia API")

        # Strategy 2-4: UA rotation
        if not wp and url:
            for ua in USER_AGENTS:
                html = fetch_html(url, ua)
                if html:
                    img_url = og_from_html(html, url)
                    if img_url:
                        path = download(img_url, img_dir)
                        if path:
                            wp = web_path(path, date_str, rid)
                            print(f"         ✓ OG scrape ({ua[:30]})")
                            break

        # Strategy 5: Wayback Machine
        if not wp and url:
            img_url = wayback_image(url)
            if img_url:
                path = download(img_url, img_dir)
                if path:
                    wp = web_path(path, date_str, rid)
                    print(f"         ✓ Wayback Machine")

        # Strategy 6: Homepage
        if not wp and url:
            img_url = homepage_image(url)
            if img_url:
                path = download(img_url, img_dir)
                if path:
                    wp = web_path(path, date_str, rid)
                    print(f"         ✓ Homepage fallback")

        # Strategy 7: Brave Image Search
        if not wp:
            img_url = brave_image(title)
            if img_url:
                path = download(img_url, img_dir)
                if path:
                    wp = web_path(path, date_str, rid)
                    print(f"         ✓ Brave Image Search")

        # Strategy 8: Unsplash keyword
        if not wp:
            keywords = " ".join(title.split()[:5])
            img_url = unsplash_image(keywords)
            if img_url:
                path = download(img_url, img_dir)
                if path:
                    wp = web_path(path, date_str, rid)
                    print(f"         ✓ Unsplash ({keywords[:30]})")

        if wp:
            existing[idx] = {"finding_idx": idx, "source_url": url or "", "image_path": wp}
            changed = True
        else:
            print(f"         ✗ No image found — gradient fallback")

    if changed:
        items = sorted(existing.values(), key=lambda x: x["finding_idx"])
        json_path.write_text(json.dumps(items, indent=2))
        print(f"  [{rid}] Saved {len(items)}/{len(findings)} → {json_path.name}")

if __name__ == "__main__":
    date = sys.argv[1] if len(sys.argv) > 1 else "2026-03-09"
    DOMAINS = [
        "ai-agents","blackbudget","china","commodities","conspiracy",
        "emerging","epstein","health","macro","russia","singularity","westeast",
        # Also run all others in case
        "crypto","culture","north-korea","quant","religion","sports","war",
    ]
    for domain in DOMAINS:
        f = BASE / "researchers" / domain / "findings" / f"{date}.md"
        if f.exists():
            fix_domain(f)
