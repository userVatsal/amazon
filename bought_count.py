"""
Fetches Amazon's own disclosed "X+ bought in past month" badge from a
product's page. This is real data Amazon publishes (bucketed/rounded —
e.g. "50+", "200+", "1K+" — not an exact count), not an estimate model.

It only appears on individual product pages (amazon.co.uk/dp/ASIN),
not on the Best Sellers grid, so this is one extra HTTP request per
product you check — keep BOUGHT_COUNT_MAX_LOOKUPS small in config.py.

Matching is done with a text-pattern regex rather than a CSS class,
since visible customer-facing copy ("bought in past month") is far
more stable across Amazon's frontend rebuilds than hashed CSS class
names — that's the lesson from the title-selector breaking earlier.
"""
from __future__ import annotations
import re
import time
import requests
from config import USER_AGENT, BOUGHT_COUNT_DELAY_SECONDS

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "en-GB,en;q=0.9",
}

BOUGHT_PATTERN = re.compile(r"([\d,]+\.?\d*[KkMm]?\+?)\s*bought in past month", re.IGNORECASE)


def get_bought_last_month(asin: str) -> str | None:
    """Returns the raw bucketed string (e.g. '600+') or None if the
    badge isn't present on the page (common for lower-volume products —
    Amazon only shows this badge above a certain sales threshold)."""
    url = f"https://www.amazon.co.uk/dp/{asin}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        time.sleep(BOUGHT_COUNT_DELAY_SECONDS)
        if resp.status_code != 200:
            print(f"  [warn] {asin}: page returned status {resp.status_code}")
            return None

        match = BOUGHT_PATTERN.search(resp.text)
        return match.group(1) if match else None

    except requests.RequestException as e:
        print(f"  [warn] {asin}: failed to fetch product page: {e}")
        return None