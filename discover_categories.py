import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
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

        # Focus on the navigation sidebar where category names are explicitly listed
        # Common selectors: div[role="tree"], ul[id="zg_browseRoot"]
        nav = soup.select_one('div[role="tree"]') or soup.select_one('ul[id*="zg_browseRoot"]')

        if nav:
            links = nav.find_all('a', href=True)
            for link in links:
                href = link['href']
                if "/bestsellers/" in href:
                    parts = href.split("/bestsellers/")
                    slug = parts[1].split("/")[0].split("?")[0]
                    name = link.get_text(strip=True)
                    # Filter out "See More" and other navigation noise
                    if slug and name and name not in ["Best Sellers", "See More", "See All"]:
                        results[name] = slug
        else:
            # Fallback but with stricter name filtering
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                if "/bestsellers/" in href:
                    parts = href.split("/bestsellers/")
                    slug = parts[1].split("/")[0].split("?")[0]
                    name = link.get_text(strip=True)
                    if slug and name and name not in ["Best Sellers", "See More", "See All"] and len(slug) > 1:
                        results[name] = slug
        return results
    except:
        return {}

def get_filtered_categories():
    all_cats = discover()
    print(f"Discovered {len(all_cats)} total categories on Amazon.")
    for name in all_cats:
        print(f"  - {name}")

    filtered = {}
    for name, slug in all_cats.items():
        if slug in NON_RETURNABLE_OPEN_CATEGORIES:
            filtered[name] = slug

    if not filtered:
        print("Discovery returned no matching 'Open' categories. Using static fallback.")
        filtered = {
            "Beauty": "beauty",
            "Grocery": "grocery",
            "Health & Personal Care": "drugstore",
            "Baby": "baby",
            "Pet Supplies": "pet-supplies"
        }

    print(f"Final targeting list: {', '.join(filtered.keys())}")
    return filtered

if __name__ == "__main__":
    get_filtered_categories()
