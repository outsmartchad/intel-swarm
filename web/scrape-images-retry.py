#!/usr/bin/env python3
"""
Intel Swarm — Image Scrape Retry
Runs after scrape-images.py. Fills gaps for findings that got no image.

Strategies (tried in order):
  1. Googlebot User-Agent (bypasses many bot-detectors)
  2. Bingbot User-Agent
  3. Plain curl-style UA
  4. Google AMP version of the page
  5. Wayback Machine (latest snapshot)
  6. Domain homepage og:image (brand fallback)
  7. Brave Image Search — searches for a relevant image using the finding title

Usage:
  python3 scrape-images-retry.py <findings.md>
"""

import sys, os, re, json, hashlib, requests
from urllib.parse import urljoin, urlparse
from pathlib import Path
from bs4 import BeautifulSoup

BASE  = Path(__file__).resolve().parents[1]
TIMEOUT = 10

# Brave Search API key (loaded from openclaw config or env)
BRAVE_API_KEY = os.environ.get("BRAVE_API_KEY", "BRAVE_API_KEY_REDACTED")

# ── User-Agent rotation ────────────────────────────────────────────────────────
USER_AGENTS = [
    # Googlebot — most sites let it through
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    # Bingbot
    "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    # Plain curl (some CDNs allow it)
    "curl/7.88.1",
    # Safari on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
]

SKIP_PATTERNS = [
    "publication-cover", "default-cover", "placeholder", "logo-only",
    "favicon", "apple-touch", "blank.", "ghost.org/v", "generic",
]

# ── Helpers ────────────────────────────────────────────────────────────────────
def is_usable(img_url):
    low = img_url.lower()
    return not any(p in low for p in SKIP_PATTERNS)

def resolve(img_url, base_url):
    if not img_url: return None
    if img_url.startswith("//"): return "https:" + img_url
    if img_url.startswith("/"): return urljoin(base_url, img_url)
    if not img_url.startswith("http"): return urljoin(base_url, img_url)
    return img_url

def og_image_from_html(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    for prop in ["og:image", "twitter:image", "twitter:image:src"]:
        tag = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
        if tag and tag.get("content"):
            url = resolve(tag["content"].strip(), base_url)
            if url and is_usable(url):
                return url
    # Fallback: first large article image
    for tag in soup.select("article img, main img, .article img, .post-content img"):
        src = tag.get("src") or tag.get("data-src") or tag.get("data-lazy-src")
        if not src: continue
        src = resolve(src, base_url)
        if not src or not src.startswith("http"): continue
        w = int(tag.get("width") or 0)
        if w and w < 200: continue
        if is_usable(src):
            return src
    return None

def fetch_with_ua(url, ua):
    try:
        r = requests.get(url, headers={"User-Agent": ua, "Accept": "text/html"},
                         timeout=TIMEOUT, allow_redirects=True)
        if r.status_code == 200:
            return r.text
    except Exception:
        pass
    return None

def try_wayback(url):
    """Try Wayback Machine latest snapshot."""
    try:
        api = f"https://archive.org/wayback/available?url={url}"
        r = requests.get(api, timeout=8)
        data = r.json()
        closest = data.get("archived_snapshots", {}).get("closest", {})
        if closest.get("available") and closest.get("url"):
            snap_url = closest["url"]
            html = fetch_with_ua(snap_url, USER_AGENTS[0])
            if html:
                return og_image_from_html(html, snap_url)
    except Exception:
        pass
    return None

def try_homepage(url):
    """Use domain homepage og:image as brand fallback."""
    parsed = urlparse(url)
    home = f"{parsed.scheme}://{parsed.netloc}"
    for ua in USER_AGENTS[:2]:
        html = fetch_with_ua(home, ua)
        if html:
            img = og_image_from_html(html, home)
            if img:
                return img
    return None

def brave_image_search(query):
    """Search Brave Images API for a relevant image URL."""
    if not BRAVE_API_KEY:
        return None
    try:
        r = requests.get(
            "https://api.search.brave.com/res/v1/images/search",
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": BRAVE_API_KEY,
            },
            params={"q": query, "count": 5, "safesearch": "off"},
            timeout=10,
        )
        if r.status_code != 200:
            return None
        data = r.json()
        results = data.get("results", [])
        for result in results:
            img_url = result.get("thumbnail", {}).get("src") or result.get("url")
            # Prefer full-size source over thumbnail
            src = result.get("properties", {}).get("url") or img_url
            if src and src.startswith("http") and is_usable(src):
                return src
    except Exception:
        pass
    return None

def extract_title_from_block(block):
    """Extract the finding title from a markdown block for search query."""
    m = re.search(r"\*\*(.+?)\*\*", block)
    if m:
        return m.group(1).strip()
    # Fallback: first non-empty line
    for line in block.split("\n"):
        line = line.strip().lstrip("-* ")
        if len(line) > 10:
            return line[:120]
    return None

def find_image(url, title=None):
    """Try all strategies in order. Return first image URL found."""
    # Strategy 1-4: different User-Agents on the original URL
    for ua in USER_AGENTS:
        html = fetch_with_ua(url, ua)
        if html:
            img = og_image_from_html(html, url)
            if img:
                print(f"    ✓ UA: {ua[:40]}")
                return img

    # Strategy 5: Wayback Machine
    img = try_wayback(url)
    if img:
        print(f"    ✓ Wayback Machine")
        return img

    # Strategy 6: Domain homepage (brand image)
    img = try_homepage(url)
    if img:
        print(f"    ✓ Domain homepage fallback")
        return img

    # Strategy 7: Brave Image Search — find relevant image by title
    if title:
        query = re.sub(r"[^\w\s]", " ", title)[:100].strip()
        img = brave_image_search(query)
        if img:
            print(f"    ✓ Brave Image Search: '{query[:50]}'")
            return img

    return None

def download_image(img_url, dest_dir):
    """Download an image and return its local path."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    name = hashlib.md5(img_url.encode()).hexdigest()[:12]
    ext  = os.path.splitext(urlparse(img_url).path)[1].lower() or ".jpg"
    if ext not in {".jpg", ".jpeg", ".png", ".gif", ".webp"}: ext = ".jpg"
    dest = dest_dir / (name + ext)
    if dest.exists():
        return f"/static/images/{dest.parent.parent.name}/{dest.parent.name}/{dest.name}"
    try:
        r = requests.get(img_url, headers={"User-Agent": USER_AGENTS[0]},
                         timeout=TIMEOUT, stream=True)
        if r.status_code == 200:
            data = b"".join(r.iter_content(1024 * 64))
            if len(data) < 2048:        # < 2 KB = probably not a real image
                return None
            with open(dest, "wb") as f:
                f.write(data)
            return f"/static/images/{dest.parent.parent.name}/{dest.parent.name}/{dest.name}"
    except Exception:
        pass
    return None

# ── URL extraction from findings file ─────────────────────────────────────────
def extract_finding_urls(findings_path):
    """Return list of (finding_idx, first_url, title) for all findings."""
    text   = Path(findings_path).read_text()
    blocks = re.split(r"\n(?=[-*]\s*(?:\*\*|🟢|🟡|🔴))", text)
    blocks = [b for b in blocks if len(b.strip()) > 20 and re.search(r"https?://", b)]
    result = []
    for i, block in enumerate(blocks):
        m = re.search(r"https?://[^\s\)\]\"\'<>,]+", block)
        url = m.group(0).rstrip(".,;)") if m else None
        title = extract_title_from_block(block)
        result.append((i, url, title))
    return result

# ── Main ───────────────────────────────────────────────────────────────────────
def main(findings_path):
    findings_path = Path(findings_path)
    if not findings_path.exists():
        print(f"Not found: {findings_path}")
        sys.exit(1)

    # Determine date and researcher id from path
    date_str = findings_path.stem          # e.g. 2026-03-04
    rid      = findings_path.parents[1].name  # e.g. ai-agents
    json_path = findings_path.parent / f"{date_str}-images.json"
    img_dir  = BASE / "web" / "static" / "images" / date_str / rid

    # Load existing results
    existing = {}
    if json_path.exists():
        try:
            items = json.loads(json_path.read_text())
            existing = {item["finding_idx"]: item for item in items}
        except Exception:
            pass

    # Find which finding indices are missing
    all_findings = extract_finding_urls(findings_path)
    missing = [(i, url, title) for i, url, title in all_findings if i not in existing and url]

    if not missing:
        print(f"✅ All findings already have images — nothing to retry")
        return

    print(f"🔄 Retrying {len(missing)} missing finding(s) for {rid}/{date_str}")
    new_found = 0

    for idx, url, title in missing:
        print(f"  [{idx}] {url[:70]}")
        img_url = find_image(url, title=title)
        if not img_url:
            print(f"    ✗ No image found")
            continue
        local_path = download_image(img_url, img_dir)
        if not local_path:
            print(f"    ✗ Download failed")
            continue
        existing[idx] = {
            "finding_idx": idx,
            "source_url":  url,
            "image_path":  local_path,
            "via": "retry",
        }
        print(f"    ✓ Saved → {os.path.basename(local_path)}")
        new_found += 1

    if new_found > 0:
        # Re-sort by finding_idx and save
        items = sorted(existing.values(), key=lambda x: x["finding_idx"])
        json_path.write_text(json.dumps(items, indent=2))
        print(f"✅ Retry recovered {new_found} image(s) → {json_path.name}")
    else:
        print(f"⚠️  Retry found nothing new — {len(missing)} finding(s) will use gradient fallback")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <path/to/YYYY-MM-DD.md>")
        sys.exit(1)
    main(sys.argv[1])
