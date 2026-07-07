from __future__ import annotations
import time
import requests
from bs4 import BeautifulSoup
from config import USER_AGENT, REQUEST_DELAY_SECONDS, TOP_N
from amazon_bestsellers import _fetch, _parse_listing

BASE_NEW_RELEASES = "https://www.amazon.co.uk/gp/new-releases/{slug}"

def get_new_releases(category_name: str, slug: str) -> list[dict]:
    print(f"Fetching New Releases: {category_name}")
    soup = _fetch(BASE_NEW_RELEASES.format(slug=slug))
    time.sleep(REQUEST_DELAY_SECONDS)
    if not soup:
        return []
    return _parse_listing(soup, "new_releases", category_name)
