from __future__ import annotations
import time, requests, json, re
from bs4 import BeautifulSoup
from config import USER_AGENT, REQUEST_DELAY_SECONDS, TOP_N

# Mobile headers are more likely to return a parseable layout for Best Sellers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
    "Accept-Language": "en-GB,en;q=0.9",
}

def _fetch(url: str) -> BeautifulSoup | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200: return None
        return BeautifulSoup(resp.text, "lxml")
    except: return None

def _parse_listing(soup: BeautifulSoup, source: str, category: str) -> list[dict]:
    results = []
    # Try multiple common selectors for bestsellers grid items
    items = soup.select("div.zg-grid-general-faceout") or             soup.select("li.zg-item-immersion") or             soup.select("div[id^='p13n-asin-index']")

    for idx, item in enumerate(items[:TOP_N], start=1):
        asin_tag = item.select_one("a.a-link-normal")
        title_tag = item.select_one('div[class*="p13n-sc-css-line-clamp"]') or                     item.select_one('div.p13n-sc-truncate') or                     item.select_one('span.a-size-base')
        price_tag = item.select_one('span[class*="p13n-sc-price"]') or                     item.select_one('span.a-color-price')

        asin = None
        if asin_tag and asin_tag.get("href"):
            m = re.search(r'/dp/([A-Z0-9]{10})', asin_tag["href"])
            if m: asin = m.group(1)

        if asin:
            results.append({
                "source": source, "category": category, "rank": idx, "asin": asin,
                "title": title_tag.get_text(strip=True) if title_tag else None,
                "price_text": price_tag.get_text(strip=True) if price_tag else None,
            })

    # Regex Fallback for high stability (captures title/asin pairs from raw source)
    if not results:
        html = str(soup)
        # title and asin are often adjacent in modern rehydration blobs
        pattern = r'\"title\":\"([^\"]+)\",\"asin\":\"([A-Z0-9]{10})\"'
        matches = re.findall(pattern, html)
        for i, (title, asin) in enumerate(matches[:TOP_N]):
            results.append({
                "source": source, "category": category, "rank": i+1, "asin": asin,
                "title": title, "price_text": None
            })

    return results

def get_bestsellers(category_name: str, slug: str) -> list[dict]:
    print(f"Fetching Best Sellers: {category_name}")
    soup = _fetch(f"https://www.amazon.co.uk/gp/bestsellers/{slug}")
    time.sleep(REQUEST_DELAY_SECONDS)
    return _parse_listing(soup, "bestsellers", category_name) if soup else []

def get_movers_and_shakers(category_name: str, slug: str) -> list[dict]:
    print(f"Fetching Movers & Shakers: {category_name}")
    soup = _fetch(f"https://www.amazon.co.uk/gp/movers-and-shakers/{slug}")
    time.sleep(REQUEST_DELAY_SECONDS)
    return _parse_listing(soup, "movers_and_shakers", category_name) if soup else []
