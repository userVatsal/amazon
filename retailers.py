import requests
from bs4 import BeautifulSoup
import time
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

def parse_units(title):
    if not title: return []
    # Matches 500g, 1kg, 100ml, 1.5L, Pack of 6, 6 x 500ml etc.
    # We want to normalize these
    title = title.lower()
    units = []

    # 1. Look for "Pack of X" or "X pack"
    pack_match = re.search(r'pack of (\d+)', title) or re.search(r'(\d+)\s*pack', title)
    if pack_match:
        units.append(("pack", float(pack_match.group(1))))

    # 2. Look for weight/volume
    # (\d+(?:\.\d+)?)\s*(g|kg|ml|l)
    vol_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(g|kg|ml|l)\b', title)
    for val, unit in vol_matches:
        val = float(val)
        if unit == 'kg':
            val *= 1000
            unit = 'g'
        elif unit == 'l':
            val *= 1000
            unit = 'ml'
        units.append((unit, val))

    # 3. Look for X x Yml
    mult_matches = re.findall(r'(\d+)\s*x\s*(\d+(?:\.\d+)?)\s*(g|kg|ml|l)\b', title)
    for count, val, unit in mult_matches:
        count = float(count)
        val = float(val)
        if unit == 'kg': val *= 1000; unit = 'g'
        elif unit == 'l': val *= 1000; unit = 'ml'
        units.append(("total_" + unit, count * val))

    return units

def units_match(units1, units2):
    if not units1 or not units2: return True # If we can't find units, we assume they might match (optimistic)

    # If both have units, they MUST match at least one significant unit
    for u1 in units1:
        for u2 in units2:
            if u1[0] == u2[0]:
                if abs(u1[1] - u2[1]) > 0.01: # allow tiny float diff
                    return False
    return True

def search_tesco(query):
    # Tesco often blocks simple requests, using a cleaner search URL
    print(f"Searching Tesco for: {query}")
    query_clean = " ".join(query.split()[:5]) # keep it short
    url = f"https://www.tesco.com/groceries/en-GB/search?query={requests.utils.quote(query_clean)}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200: return []
        soup = BeautifulSoup(resp.text, "lxml")
        products = []
        # Update selector based on current Tesco layout if possible
        items = soup.select('.product-list--list-item')
        for item in items:
            title_tag = item.select_one('h3 a')
            price_tag = item.select_one('.value')
            if title_tag and price_tag:
                title = title_tag.get_text(strip=True)
                price = float(price_tag.get_text(strip=True).replace("£", ""))
                products.append({
                    "retailer": "Tesco",
                    "title": title,
                    "price": price,
                    "url": "https://www.tesco.com" + title_tag['href'],
                    "units": parse_units(title)
                })
        return products
    except Exception as e:
        print(f"Tesco search error: {e}")
        return []

def search_tkmaxx(query):
    print(f"Searching TK Maxx for: {query}")
    query_clean = " ".join(query.split()[:4])
    url = f"https://www.tkmaxx.com/uk/en/search?text={requests.utils.quote(query_clean)}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200: return []
        soup = BeautifulSoup(resp.text, "lxml")
        products = []
        items = soup.select('.product-item')
        for item in items:
            title_tag = item.select_one('.title a')
            price_tag = item.select_one('.price')
            if title_tag and price_tag:
                title = title_tag.get_text(strip=True)
                # Extract price £12.00 -> 12.00
                price_text = price_tag.get_text(strip=True)
                price_match = re.search(r'£?(\d+\.\d{2})', price_text)
                price = float(price_match.group(1)) if price_match else 0.0
                products.append({
                    "retailer": "TK Maxx",
                    "title": title,
                    "price": price,
                    "url": title_tag['href'],
                    "units": parse_units(title)
                })
        return products
    except Exception as e:
        print(f"TK Maxx search error: {e}")
        return []

def find_best_match(amazon_item, retailer_results):
    amz_units = parse_units(amazon_item['title'])
    best_match = None

    for res in retailer_results:
        if units_match(amz_units, res['units']):
            # For now, just take the first matching unit one
            # Ideally, check title similarity
            return res
    return None

if __name__ == "__main__":
    # Test unit parser
    print(parse_units("Cadbury Dairy Milk 200g Pack of 2"))
    print(parse_units("Coke 6 x 330ml"))

def search_asda(query):
    # Asda blocks simple requests, skipping for now or would need a proxy/browser automation
    # print(f"Searching Asda for: {query}")
    return []
