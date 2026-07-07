"""
Scrapes Amazon UK's public Best Sellers and Movers & Shakers pages.

IMPORTANT — read before running at scale:
- These pages are public, no login needed, but scraping them is a grey
  area under Amazon's Conditions of Use. Light, infrequent, personal-use
  pulls (a few categories, a few times a day) are what most sourcing
  tools quietly do. Hammering it will get your IP rate-limited or
  blocked, and could affect any seller account run from the same network.
- Amazon changes its HTML periodically, which will break the CSS
  selectors below. Treat this as a starting point to maintain, not a
  fire-and-forget tool.
- For a compliant, stable alternative to raw scraping, Keepa
  (keepa.com/#!api) sells this same rank/price data via a proper paid
  API with a UK dataset — worth it once this is making real money.
"""
import time
import requests
from bs4 import BeautifulSoup
from config import USER_AGENT, REQUEST_DELAY_SECONDS, TOP_N

BASE_BESTSELLERS = "https://www.amazon.co.uk/gp/bestsellers/{slug}"
BASE_MOVERS = "https://www.amazon.co.uk/gp/movers-and-shakers/{slug}"

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "en-GB,en;q=0.9",
}


def _fetch(url: str) -> BeautifulSoup | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            print(f"  [warn] {url} returned status {resp.status_code}")
            return None
        return BeautifulSoup(resp.text, "lxml")
    except requests.RequestException as e:
        print(f"  [error] failed to fetch {url}: {e}")
        return None


def _parse_listing(soup: BeautifulSoup, source: str, category: str) -> list[dict]:
    """Parses a bestsellers-style grid into structured rows.
    Amazon's markup shifts often; this targets the current
    div[data-asin] grid item pattern as of mid-2026."""
    results = []
    items = soup.select("div.p13n-desktop-grid > div[id^='p13n-asin-index']") \
        or soup.select("div.zg-grid-general-faceout")

    for idx, item in enumerate(items[:TOP_N], start=1):
        asin_tag = item.select_one("a.a-link-normal")
        title_tag = item.select_one("div._cDEzb_p13n-sc-css-line-clamp-1_1Fn1y") \
            or item.select_one("div.p13n-sc-truncate-desktop-type2")
        price_tag = item.select_one("span._cDEzb_p13n-sc-price_3mJ9Z") \
            or item.select_one("span.p13n-sc-price")
        rating_tag = item.select_one("span.a-icon-alt")

        asin = None
        if asin_tag and asin_tag.get("href"):
            href = asin_tag["href"]
            for part in href.split("/"):
                if len(part) == 10 and part.isalnum():
                    asin = part
                    break

        results.append({
            "source": source,
            "category": category,
            "rank": idx,
            "asin": asin,
            "title": title_tag.get_text(strip=True) if title_tag else None,
            "price_text": price_tag.get_text(strip=True) if price_tag else None,
            "rating_text": rating_tag.get_text(strip=True) if rating_tag else None,
        })
    return results


def get_bestsellers(category_name: str, slug: str) -> list[dict]:
    print(f"Fetching Best Sellers: {category_name}")
    soup = _fetch(BASE_BESTSELLERS.format(slug=slug))
    time.sleep(REQUEST_DELAY_SECONDS)
    if not soup:
        return []
    return _parse_listing(soup, "bestsellers", category_name)


def get_movers_and_shakers(category_name: str, slug: str) -> list[dict]:
    print(f"Fetching Movers & Shakers: {category_name}")
    soup = _fetch(BASE_MOVERS.format(slug=slug))
    time.sleep(REQUEST_DELAY_SECONDS)
    if not soup:
        return []
    return _parse_listing(soup, "movers_and_shakers", category_name)
