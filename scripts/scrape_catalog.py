import time
import csv
import re
import os
import random
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_SEARCH_URL = "https://www.shl.com/solutions/products/product-catalog/"
PRODUCT_BASE = "https://www.shl.com"


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


def fetch(url: str) -> str:
    """Fetch a URL with basic retry + realistic headers."""
    for attempt in range(1, 6):
        try:
            print(f"Fetching {url} (attempt {attempt})")
            resp = requests.get(url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"Fetch failed: {e}")
            time.sleep(1 + random.random())
    print(f"FAILED after retries: {url}")
    return ""


def debug_dump_html(html: str, filename: str = "debug_catalog_page1.html"):
    os.makedirs("debug", exist_ok=True)
    path = os.path.join("debug", filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"DEBUG: wrote HTML dump to {path}")
    print("Open this file in your browser and inspect how product links are structured.")


def parse_search_page(html: str, is_first_page: bool = False):
    """
    Parse one catalog page and extract product detail URLs.
    """
    soup = BeautifulSoup(html, "html.parser")

    # DEBUG: show first 50 hrefs the first time so you can see patterns
    if is_first_page:
        print("DEBUG: first 50 hrefs on the page:")
        hrefs = []
        for a in soup.find_all("a", href=True):
            hrefs.append(a["href"])
            if len(hrefs) >= 50:
                break
        for h in hrefs:
            print("  ", h)
        print("DEBUG: end of href preview")

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        full = urljoin(PRODUCT_BASE, href)

        # Detail pages look like /products/product-catalog/view/<slug>/ or /solutions/...
        if "/product-catalog/view/" not in full:
            continue

        # Exclude pre-packaged job solutions if they appear in your links
        if "pre-packaged-job-solutions" in full:
            continue

        links.append(full)

    links = sorted(set(links))
    print(f"  Parsed {len(links)} catalog detail links on this page.")
    return links


def slug_to_name(url: str) -> str:
    """Convert last URL segment into a readable name."""
    slug = url.rstrip("/").split("/")[-1]
    slug = slug.replace("-", " ")
    return " ".join(word.capitalize() for word in slug.split())


def save_catalog_from_urls(urls, out_path="data/catalog.csv"):
    os.makedirs("data", exist_ok=True)
    rows = []
    for u in sorted(urls):
        rows.append(
            {
                "url": u,
                "name": slug_to_name(u),
                "description": "",
                "duration": 0,
                "test_type": "",
                "remote_support": "Unknown",
                "adaptive_support": "Unknown",
            }
        )

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "url",
                "name",
                "description",
                "duration",
                "test_type",
                "remote_support",
                "adaptive_support",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"[CATALOG] Saved {len(rows)} rows to {out_path}")


def main():
    all_urls = set()

    # 1) COLLECT PRODUCT URLS
    for page in range(1, 30):
        if page == 1:
            page_url = BASE_SEARCH_URL
        else:
            offset = (page - 1) * 12
            page_url = f"{BASE_SEARCH_URL}?start={offset}&type=1"

        html = fetch(page_url)
        if not html:
            print(f"Stopping pagination due to empty HTML at {page_url}")
            break

        if page == 1:
            debug_dump_html(html)

        urls = parse_search_page(html, is_first_page=(page == 1))
        new_urls = [u for u in urls if u not in all_urls]
        print(f"  Found {len(urls)} urls on page, {len(new_urls)} new")

        if not new_urls:
            print("No new URLs found on this page. Stopping pagination.")
            break

        all_urls.update(new_urls)
        time.sleep(1.0)

    print(f"Collected {len(all_urls)} product URLs")

    # 2) Save URL list for future reuse / rebuilding
    os.makedirs("data", exist_ok=True)
    url_list_path = "data/url_list.txt"
    with open(url_list_path, "w", encoding="utf-8") as f:
        for u in sorted(all_urls):
            f.write(u + "\n")
    print(f"[URL LIST] Saved {len(all_urls)} URLs to {url_list_path}")

    # 3) Build a minimal catalog directly from URLs (no detail-page scraping)
    save_catalog_from_urls(all_urls, out_path="data/catalog.csv")


if __name__ == "__main__":
    main()
