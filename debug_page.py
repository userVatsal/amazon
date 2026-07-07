"""
One-off diagnostic. Saves the raw HTML of one Best Sellers page and one
Movers & Shakers page to disk, so we can find the real CSS selectors
Amazon is currently using (they clearly differ from what main.py assumes).

Run: python3 debug_page.py
Then open bestsellers_debug.html and movers_debug.html in a text editor
(or VS Code), search (Cmd+F) for one of the ASINs you already have —
e.g. B0BRV61DPY — and paste me the ~20 lines of HTML around it.
"""
import requests
from config import USER_AGENT

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "en-GB,en;q=0.9",
}

targets = {
    "bestsellers_debug.html": "https://www.amazon.co.uk/gp/bestsellers/kitchen",
    "movers_debug.html": "https://www.amazon.co.uk/gp/movers-and-shakers/kitchen",
}

for filename, url in targets.items():
    print(f"Fetching {url} ...")
    resp = requests.get(url, headers=HEADERS, timeout=15)
    print(f"  status: {resp.status_code}, length: {len(resp.text)} chars")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(resp.text)
    print(f"  saved to {filename}")

print("\nDone. Open the saved files, search for an ASIN like B0BRV61DPY,")
print("and paste me the surrounding HTML so I can fix the selectors exactly.")