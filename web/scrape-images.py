#!/usr/bin/env python3
"""
Scrape OG images from source URLs in intel findings.
Usage: python3 scrape-images.py <path-to-findings.md>
Output: findings/YYYY-MM-DD-images.json + images/YYYY-MM-DD/{slug}.jpg
"""

import sys, os, re, json, hashlib, time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
TIMEOUT = 8
MAX_IMG_MB = 3

def extract_urls(text):
    """Extract all https URLs from markdown text."""
    return re.findall(r'https?://[^\s\)\]\"\'<>]+', text)

def get_og_image(url):
    """Fetch a page and return its og:image URL."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        if r.status_code != 200: return None
        soup = BeautifulSoup(r.text, 'html.parser')
        # Try og:image first
        for prop in ['og:image', 'twitter:image', 'twitter:image:src']:
            tag = soup.find('meta', property=prop) or soup.find('meta', attrs={'name': prop})
            if tag and tag.get('content'):
                img_url = tag['content'].strip()
                if img_url.startswith('//'): img_url = 'https:' + img_url
                elif img_url.startswith('/'): img_url = urljoin(url, img_url)
                return img_url
    except Exception as e:
        pass
    return None

def download_image(img_url, save_path):
    """Download image to save_path. Returns True on success."""
    try:
        r = requests.get(img_url, headers=HEADERS, timeout=TIMEOUT, stream=True)
        if r.status_code != 200: return False
        content_type = r.headers.get('content-type', '')
        if not any(t in content_type for t in ['image/', 'jpeg', 'jpg', 'png', 'webp', 'gif']):
            return False
        size = 0
        with open(save_path, 'wb') as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
                size += len(chunk)
                if size > MAX_IMG_MB * 1024 * 1024:
                    f.close(); os.remove(save_path); return False
        return os.path.getsize(save_path) > 1000  # must be >1KB
    except:
        return False

def url_slug(url):
    """Short unique filename from URL."""
    return hashlib.md5(url.encode()).hexdigest()[:12]

def ext_from_url(url):
    """Get image extension from URL."""
    path = urlparse(url).path.lower()
    for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
        if path.endswith(ext): return ext
    return '.jpg'

def scrape_findings_images(findings_path):
    """Main: scrape all OG images for a findings file."""
    if not os.path.exists(findings_path):
        print(f"Not found: {findings_path}"); return

    with open(findings_path) as f:
        content = f.read()

    # Derive paths — images always stored in web/static/images/{date}/{rid}/
    script_dir = os.path.dirname(os.path.abspath(__file__))  # web/
    static_dir = os.path.join(script_dir, 'static', 'images')
    findings_dir = os.path.dirname(findings_path)
    date = os.path.basename(findings_path).replace('.md', '').replace('.zh', '')
    # Determine researcher id from path
    parts = findings_path.replace('\\', '/').split('/')
    rid = 'unknown'
    for i, p in enumerate(parts):
        if p in ('researchers', 'synthesis', 'chief'):
            rid = parts[i+1] if p == 'researchers' else p
            break
    images_dir = os.path.join(static_dir, date, rid)
    os.makedirs(images_dir, exist_ok=True)
    images_json_path = findings_path.replace('.md', '-images.json')

    # Skip if already scraped and newer than findings
    if os.path.exists(images_json_path):
        if os.path.getmtime(images_json_path) >= os.path.getmtime(findings_path):
            print(f"Up to date: {images_json_path}"); return

    # Parse findings blocks — each **bold** finding with sources
    findings_blocks = re.split(r'\n(?=[-*]\s*\*\*)', content)
    results = []

    print(f"Scraping images for {findings_path}")

    for idx, block in enumerate(findings_blocks):
        urls = extract_urls(block)
        if not urls: continue

        # Try each URL until we get an OG image
        image_saved = None
        for url in urls[:3]:  # max 3 URLs per finding
            og_url = get_og_image(url)
            if not og_url:
                continue
            slug = url_slug(og_url)
            ext = ext_from_url(og_url)
            save_path = os.path.join(images_dir, f"{slug}{ext}")
            # Web path = /static/images/{date}/{rid}/{slug}{ext}
            web_path = f"/static/images/{date}/{rid}/{slug}{ext}"
            if download_image(og_url, save_path):
                image_saved = web_path
                print(f"  ✓ [{idx}] {url[:60]} → {slug}{ext}")
                break
            time.sleep(0.3)

        if image_saved:
            results.append({
                "finding_idx": idx,
                "source_url": urls[0],
                "image_path": image_saved
            })

        time.sleep(0.4)  # polite delay

    with open(images_json_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Saved {len(results)} images → {images_json_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: scrape-images.py <findings.md>"); sys.exit(1)
    scrape_findings_images(sys.argv[1])
