#!/usr/bin/env python3
"""
Intel Swarm — Unified Image Fetcher
Single script that handles both scraping AND fallback.

Strategy per finding (in order):
  1. OG/twitter:image from source URL  (4 UA variants)
  2. Wayback Machine snapshot
  3. Domain homepage og:image
  4. Brave Image Search (title query)  ← guaranteed if API key present

Usage:
  python3 fetch-images.py <path/to/YYYY-MM-DD.md>
  python3 fetch-images.py <path/to/YYYY-MM-DD.md> --force   # re-fetch all

Safe to run multiple times (idempotent — skips findings that already have a
valid image file on disk).
"""
import sys, os, re, json, hashlib, argparse
import requests
from urllib.parse import urljoin, urlparse
from pathlib import Path
from bs4 import BeautifulSoup

BASE    = Path(__file__).resolve().parents[1]
TIMEOUT = 10
BRAVE_API_KEY = os.environ.get("BRAVE_API_KEY", "")

USER_AGENTS = [
    # Googlebot — most publisher sites let it through
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    # Bingbot
    "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    # Plain curl — some CDNs pass this
    "curl/7.88.1",
    # Safari macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Safari/605.1.15",
]

SKIP_PATTERNS = [
    "publication-cover", "default-cover", "placeholder", "logo-only",
    "favicon", "apple-touch", "blank.", "ghost.org/v", "generic",
]

# ─── Helpers ──────────────────────────────────────────────────────────────────

def is_usable(url: str) -> bool:
    return bool(url) and not any(p in url.lower() for p in SKIP_PATTERNS)

def resolve(img_url: str, base_url: str) -> str | None:
    if not img_url: return None
    if img_url.startswith("//"): return "https:" + img_url
    if not img_url.startswith("http"): return urljoin(base_url, img_url)
    return img_url

def og_from_html(html: str, base_url: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    for prop in ["og:image", "twitter:image", "twitter:image:src"]:
        tag = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
        if tag and tag.get("content"):
            url = resolve(tag["content"].strip(), base_url)
            if is_usable(url): return url
    # Fallback: first large content image
    for tag in soup.select("article img, main img, .article img, .post-content img"):
        src = tag.get("src") or tag.get("data-src") or tag.get("data-lazy-src")
        if not src: continue
        src = resolve(src, base_url)
        if not src or not src.startswith("http"): continue
        if int(tag.get("width") or 0) < 200: continue
        if is_usable(src): return src
    return None

def fetch_html(url: str, ua: str) -> str | None:
    try:
        r = requests.get(url, headers={"User-Agent": ua, "Accept": "text/html"},
                         timeout=TIMEOUT, allow_redirects=True)
        return r.text if r.status_code == 200 else None
    except: return None

def wayback_image(url: str) -> str | None:
    try:
        r = requests.get(f"https://archive.org/wayback/available?url={url}", timeout=8)
        snap = r.json().get("archived_snapshots", {}).get("closest", {})
        if snap.get("available") and snap.get("url"):
            html = fetch_html(snap["url"], USER_AGENTS[0])
            if html: return og_from_html(html, snap["url"])
    except: pass
    return None

def homepage_image(url: str) -> str | None:
    parsed = urlparse(url)
    home = f"{parsed.scheme}://{parsed.netloc}"
    for ua in USER_AGENTS[:2]:
        html = fetch_html(home, ua)
        if html:
            img = og_from_html(html, home)
            if img: return img
    return None

def brave_image(title: str) -> str | None:
    if not BRAVE_API_KEY: return None
    query = re.sub(r"[^\w\s]", " ", title)[:100].strip()
    try:
        r = requests.get(
            "https://api.search.brave.com/res/v1/images/search",
            headers={"Accept": "application/json", "X-Subscription-Token": BRAVE_API_KEY},
            params={"q": query, "count": 10, "safesearch": "off"},
            timeout=10,
        )
        if r.status_code != 200: return None
        for res in r.json().get("results", []):
            src = res.get("properties", {}).get("url") or res.get("thumbnail", {}).get("src")
            if src and src.startswith("http") and is_usable(src):
                return src
    except: pass
    return None

def download(img_url: str, dest_dir: Path) -> str | None:
    """Download image → returns local disk path, or None on failure."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    name = hashlib.md5(img_url.encode()).hexdigest()[:12]
    ext  = Path(urlparse(img_url).path).suffix.lower()
    if ext not in {".jpg", ".jpeg", ".png", ".gif", ".webp"}: ext = ".jpg"
    dest = dest_dir / (name + ext)
    if dest.exists() and dest.stat().st_size > 2048:
        return str(dest)  # already cached
    try:
        r = requests.get(img_url, headers={"User-Agent": USER_AGENTS[0]},
                         timeout=TIMEOUT, stream=True)
        if r.status_code != 200: return None
        data = b"".join(r.iter_content(65536))
        if len(data) < 2048: return None   # too small → not a real image
        dest.write_bytes(data)
        return str(dest)
    except: return None

# ─── Finding parser (mirrors server.py extract_findings) ──────────────────────

def parse_findings(text: str) -> list[tuple[str, str | None]]:
    """
    Parse findings using the same regex as server.py's extract_findings().
    Returns list of (title, first_url | None), capped at 5.
    """
    findings = []
    for m in re.finditer(
        r'\*\*(.+?)\*\*[:\s—–-]*(.+?)(?=\n[-*]|\n\n|\Z)', text, re.DOTALL
    ):
        title = m.group(1).strip()
        body  = m.group(2).strip()
        if not (10 < len(title) < 200): continue
        url_m = re.search(r'https?://[^\s\)\]\"\'<>,]+', body)
        url   = url_m.group(0).rstrip(".,;)") if url_m else None
        findings.append((title, url))
        if len(findings) >= 5: break
    return findings

# ─── Core: fetch image for one finding ────────────────────────────────────────

def fetch_one(idx: int, title: str, url: str | None, dest_dir: Path) -> str | None:
    """
    Try all strategies in order. Returns web path (/static/images/...) or None.
    """
    def web_path(disk_path: str) -> str:
        p = Path(disk_path)
        return "/static/images/" + "/".join(p.parts[-3:])

    # Strategies 1-4: UA rotation on source URL
    if url:
        for ua in USER_AGENTS:
            html = fetch_html(url, ua)
            if html:
                img_url = og_from_html(html, url)
                if img_url:
                    path = download(img_url, dest_dir)
                    if path:
                        print(f"    [{idx}] ✓ OG scrape")
                        return web_path(path)

        # Strategy 5: Wayback Machine
        img_url = wayback_image(url)
        if img_url:
            path = download(img_url, dest_dir)
            if path:
                print(f"    [{idx}] ✓ Wayback Machine")
                return web_path(path)

        # Strategy 6: Domain homepage fallback
        img_url = homepage_image(url)
        if img_url:
            path = download(img_url, dest_dir)
            if path:
                print(f"    [{idx}] ✓ Domain homepage")
                return web_path(path)

    # Strategy 7: Brave Image Search (title-based query)
    img_url = brave_image(title)
    if img_url:
        path = download(img_url, dest_dir)
        if path:
            print(f"    [{idx}] ✓ Brave: '{title[:50]}'")
            return web_path(path)

    print(f"    [{idx}] ✗ No image found for: {title[:60]}")
    return None

# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Fetch images for intel-swarm findings")
    ap.add_argument("findings", help="Path to findings YYYY-MM-DD.md")
    ap.add_argument("--force", action="store_true", help="Re-fetch all, ignore existing")
    args = ap.parse_args()

    findings_path = Path(args.findings)
    if not findings_path.exists():
        print(f"Not found: {findings_path}"); sys.exit(1)

    # Derive date and researcher id from path
    date_str = findings_path.stem
    if date_str.endswith(".zh"): date_str = date_str[:-3]

    rid = "unknown"
    for i, part in enumerate(findings_path.parts):
        if part == "researchers" and i + 1 < len(findings_path.parts):
            rid = findings_path.parts[i + 1]; break
        if part in ("synthesis", "chief"):
            rid = part; break

    img_dir   = BASE / "web" / "static" / "images" / date_str / rid
    json_path = findings_path.parent / f"{date_str}-images.json"

    # Load existing (only entries with real files on disk)
    existing: dict[int, dict] = {}
    if json_path.exists() and not args.force:
        try:
            for item in json.loads(json_path.read_text()):
                ipath = item.get("image_path", "")
                disk  = BASE / "web" / ipath.lstrip("/")
                if ipath and disk.exists() and disk.stat().st_size > 2048:
                    existing[item["finding_idx"]] = item
        except: pass

    text     = findings_path.read_text()
    findings = parse_findings(text)

    if not findings:
        print(f"  [{rid}] No findings parsed — skipping"); return

    need = [i for i in range(len(findings)) if i not in existing]
    print(f"  [{rid}/{date_str}] {len(findings)} findings · {len(existing)} cached · {len(need)} to fetch")

    if not need:
        print(f"  [{rid}] All images present ✓"); return

    changed = False
    for idx in need:
        title, url = findings[idx]
        wp = fetch_one(idx, title, url, img_dir)
        if wp:
            existing[idx] = {
                "finding_idx": idx,
                "source_url":  url or "",
                "image_path":  wp,
            }
            changed = True

    if changed or not json_path.exists():
        items = sorted(existing.values(), key=lambda x: x["finding_idx"])
        json_path.write_text(json.dumps(items, indent=2))
        total = len(items)
        print(f"  [{rid}] Saved {total}/{len(findings)} images → {json_path.name}")

if __name__ == "__main__":
    main()
