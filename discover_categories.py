import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
}

# Categories generally considered "Open" for new sellers and "Non-returnable"
NON_RETURNABLE_OPEN_CATEGORIES = [
    "beauty",
    "grocery",
    "drugstore", # Health & Personal Care
    "baby",
    "pet-supplies",
]

def discover():
    url = "https://www.amazon.co.uk/gp/bestsellers"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return {}

        soup = BeautifulSoup(resp.text, "lxml")
        results = {}

        # Looking for category links in the sidebar or body
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            if "/gp/bestsellers/" in href:
                parts = href.split("/gp/bestsellers/")
                slug = parts[1].split("/")[0].split("?")[0]
                name = link.get_text(strip=True)
                if slug and name and name != "Best Sellers" and len(slug) > 1:
                    results[name] = slug
        return results
    except:
        return {}

def get_filtered_categories():
    all_cats = discover()
    filtered = {}
    for name, slug in all_cats.items():
        if slug in NON_RETURNABLE_OPEN_CATEGORIES:
            filtered[name] = slug

    # If we didn't find them dynamically (blocked/markup change), use defaults as fallback
    if not filtered:
        filtered = {
            "Beauty": "beauty",
            "Grocery": "grocery",
            "Health & Personal Care": "drugstore",
            "Baby": "baby",
            "Pet Supplies": "pet-supplies"
        }
    return filtered
