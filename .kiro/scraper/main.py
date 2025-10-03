#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sitemap-driven crawler that IGNores robots.txt.
- Parses sitemap (sitemap index supported)
- Renders pages with Playwright (Chromium)
- Saves HTML, full-page screenshot, per-page HAR
- Extracts metadata for LLM task generation
- Handles www vs apex domain
- Optional throttle, but default is 0s (no delay)

Usage:
  python main.py --base https://teammates.ai --out out_teammates --max-pages 150

Setup:
  pip install -r requirements.txt
  playwright install
"""

import argparse
import hashlib
import json
import os
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from lxml import etree, html
from tqdm import tqdm

from playwright.sync_api import sync_playwright


# --------------------------
# Helpers
# --------------------------

def safe_name_from_url(u: str) -> str:
    """Turn a URL into a safe-ish unique filename stem."""
    parsed = urlparse(u)
    stem = (parsed.netloc + parsed.path).strip("/")
    if not stem:
        stem = "root"
    stem = re.sub(r"[^a-zA-Z0-9._-]+", "_", stem)
    h = hashlib.sha1(u.encode("utf-8")).hexdigest()[:8]
    return f"{stem}_{h}"


def hosts_equivalent(a: str, b: str) -> bool:
    """Treat www. and apex as the same host."""
    def norm(h: str) -> str:
        h = h.lower()
        return h[4:] if h.startswith("www.") else h
    return norm(urlparse(a).netloc) == norm(urlparse(b).netloc)


def fetch(url: str, **kwargs) -> requests.Response:
    return requests.get(url, timeout=30, **kwargs)


# --------------------------
# Sitemap parsing
# --------------------------

def parse_sitemap(sitemap_url: str) -> list[str]:
    """
    Parse a sitemap or sitemap index into a flat list of <loc> URLs.
    Supports nested indexes.
    """
    urls = []
    r = fetch(sitemap_url)
    r.raise_for_status()
    root = etree.fromstring(r.content)

    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_tags = root.findall(".//sm:sitemap", ns)
    url_tags = root.findall(".//sm:url", ns)

    if sitemap_tags:
        # sitemap index
        for st in sitemap_tags:
            loc = st.findtext("sm:loc", namespaces=ns)
            if loc:
                urls.extend(parse_sitemap(loc))
    elif url_tags:
        # url set
        for ut in url_tags:
            loc = ut.findtext("sm:loc", namespaces=ns)
            if loc:
                urls.append(loc)
    else:
        # Fallback: try <loc> without namespaces
        for loc in root.findall(".//loc"):
            if loc.text:
                urls.append(loc.text.strip())

    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for u in urls:
        if u not in seen:
            deduped.append(u)
            seen.add(u)
    return deduped


# --------------------------
# HTML extraction utilities
# --------------------------

def extract_metadata(html_text: str, page_url: str) -> dict:
    """Extract title, meta description, H1, forms, links, and asset URLs."""
    try:
        doc = html.fromstring(html_text)
    except Exception:
        return {}

    def text_or_none(x):
        return x.strip() if x else None

    title = doc.xpath("string(//title)")
    meta_desc = doc.xpath("string(//meta[@name='description']/@content)")
    h1 = doc.xpath("string(//h1)")

    # Forms
    forms = []
    for f in doc.xpath("//form"):
        action = f.get("action") or ""
        method = (f.get("method") or "GET").upper()
        inputs = []
        for inp in f.xpath(".//input|.//textarea|.//select|.//button"):
            inputs.append({
                "tag": inp.tag,
                "type": inp.get("type"),
                "name": inp.get("name"),
                "id": inp.get("id"),
                "placeholder": inp.get("placeholder"),
                "value": inp.get("value"),
                "text": (inp.text or "").strip()
            })
        forms.append({
            "action": action,
            "method": method,
            "inputs": inputs
        })

    # Links (absolute)
    links = [l for l in doc.xpath("//a/@href") if l]
    abs_links = []
    for l in links:
        try:
            abs_links.append(urljoin(page_url, l))
        except Exception:
            pass

    # Assets (absolute)
    images = [urljoin(page_url, s) for s in doc.xpath("//img/@src")]
    scripts = [urljoin(page_url, s) for s in doc.xpath("//script/@src") if s]
    styles = [urljoin(page_url, s) for s in doc.xpath("//link[@rel='stylesheet']/@href")]

    return {
        "title": text_or_none(title),
        "meta_description": text_or_none(meta_desc),
        "h1": text_or_none(h1),
        "forms": forms,
        "links": abs_links,
        "assets": {
            "images": images,
            "scripts": scripts,
            "stylesheets": styles
        }
    }


# --------------------------
# Main crawl
# --------------------------

def crawl_pages(base_url: str,
                urls: list[str],
                out_dir: Path,
                max_pages: int | None,
                throttle_seconds: float = 0.0,
                keep_only_same_host: bool = True):
    """
    Visit each URL with Playwright, save HTML/screenshot/HAR, extract metadata.
    - Ignores robots.txt entirely.
    - throttle_seconds: add sleep between requests (0 by default).
    - keep_only_same_host: if True, only crawl URLs whose host matches base (www-aware).
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    pages_dir = out_dir / "pages"
    pages_dir.mkdir(exist_ok=True)
    har_dir = out_dir / "har"
    har_dir.mkdir(exist_ok=True)
    shots_dir = out_dir / "screenshots"
    shots_dir.mkdir(exist_ok=True)

    # Filter by host (optional)
    start_count = len(urls)
    if keep_only_same_host:
        urls = [u for u in urls if hosts_equivalent(base_url, u)]
    filtered_count = len(urls)

    if max_pages:
        urls = urls[:max_pages]

    # User-Agent: a mainstream Chrome UA reduces chance of WAF blocks
    agent = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/127.0.0.0 Safari/537.36"
    )

    records = []
    errors = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for u in tqdm(urls, desc="Crawling"):
            if throttle_seconds > 0:
                time.sleep(throttle_seconds)

            # one context per page so each gets its own HAR
            har_path = str((har_dir / f"{safe_name_from_url(u)}.har").resolve())
            context = browser.new_context(
                user_agent=agent,
                record_har_path=har_path,
                record_har_mode="full",
                ignore_https_errors=True,
                java_script_enabled=True,
                viewport={"width": 1400, "height": 900}
            )
            page = context.new_page()

            status_code = None
            html_path = str((pages_dir / f"{safe_name_from_url(u)}.html").resolve())
            shot_path = str((shots_dir / f"{safe_name_from_url(u)}.png").resolve())

            try:
                resp = page.goto(u, wait_until="networkidle", timeout=45000)
                if resp:
                    status_code = resp.status

                # Save rendered DOM HTML
                content = page.content()
                Path(html_path).write_text(content, encoding="utf-8")

                # Full page screenshot
                page.screenshot(path=shot_path, full_page=True)

                # Extract metadata
                meta = extract_metadata(content, u)

            except Exception as e:
                meta = {"error": str(e)}
                errors += 1
            finally:
                context.close()

            rec = {
                "url": u,
                "status": status_code,
                "html_path": html_path,
                "screenshot_path": shot_path,
                "har_path": har_path,
                "extracted": meta
            }
            records.append(rec)

    # Write summary JSON
    summary_path = out_dir / "pages_summary.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    # Simple report
    print("\n--- Crawl report ---")
    print(f"Initial URLs from sitemap: {start_count}")
    if keep_only_same_host:
        print(f"Kept (same host as base): {filtered_count}")
    print(f"Crawled (after max-pages): {len(urls)}")
    print(f"Errors: {errors}")
    print(f"Summary JSON: {summary_path}")

    return str(summary_path)


# --------------------------
# CLI
# --------------------------

def resolve_sitemap_url(base_url: str, explicit_sitemap: str | None) -> str:
    if explicit_sitemap:
        return explicit_sitemap
    parsed = urlparse(base_url)
    return f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"


def main():
    ap = argparse.ArgumentParser(description="Sitemap → Playwright crawler (ignores robots.txt).")
    ap.add_argument("--base", required=True, help="Base site URL (e.g., https://teammates.ai)")
    ap.add_argument("--sitemap", help="Override sitemap URL (defaults to <base>/sitemap.xml)")
    ap.add_argument("--out", default="out", help="Output directory")
    ap.add_argument("--max-pages", type=int, default=None, help="Max pages to crawl (default: all)")
    ap.add_argument("--throttle", type=float, default=0.0, help="Seconds to sleep between requests (default: 0)")
    ap.add_argument("--all-hosts", action="store_true",
                    help="If set, crawl ALL hosts present in sitemap (dangerous). Default: only same host (www-aware).")
    args = ap.parse_args()

    base_url = args.base.rstrip("/")
    out_dir = Path(args.out)

    # 1) Resolve sitemap
    sitemap_url = resolve_sitemap_url(base_url, args.sitemap)
    print(f"[1/3] Fetching sitemap: {sitemap_url}")
    try:
        url_list = parse_sitemap(sitemap_url)
    except Exception as e:
        raise SystemExit(f"Failed to parse sitemap: {e}")

    if not url_list:
        raise SystemExit("No URLs found in sitemap.")

    print(f"[2/3] Found {len(url_list)} URLs in sitemap.")

    # 2) Crawl with Playwright (ignoring robots)
    print("[3/3] Crawling pages (robots.txt ignored)...")
    summary_path = crawl_pages(
        base_url=base_url,
        urls=url_list,
        out_dir=out_dir,
        max_pages=args.max_pages,
        throttle_seconds=args.throttle,
        keep_only_same_host=not args.all_hosts
    )

    print("Done.")
    print(f"Artifacts:\n  HTML: {out_dir / 'pages'}\n  Screenshots: {out_dir / 'screenshots'}\n  HAR: {out_dir / 'har'}\n  Summary: {summary_path}")


if __name__ == "__main__":
    main()
