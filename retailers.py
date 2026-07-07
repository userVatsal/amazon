import requests
from bs4 import BeautifulSoup
import time
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

def parse_units(title):
    if not title: return []
    title = title.lower()
    units = []

    pack_match = re.search(r'pack of (\d+)', title) or re.search(r'(\d+)\s*pack', title)
    pack_size = float(pack_match.group(1)) if pack_match else 1.0
    units.append(("pack", pack_size))

    vol_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(g|kg|ml|l)\b', title)
    for val, unit in vol_matches:
        val = float(val)
        if unit == 'kg': val *= 1000; unit = 'g'
        elif unit == 'l': val *= 1000; unit = 'ml'
        units.append((unit, val))
        # Also track total weight/volume if pack size > 1
        if pack_size > 1:
            units.append(("total_" + unit, val * pack_size))

    mult_matches = re.findall(r'(\d+)\s*x\s*(\d+(?:\.\d+)?)\s*(g|kg|ml|l)\b', title)
    for count, val, unit in mult_matches:
        count = float(count)
        val = float(val)
        if unit == 'kg': val *= 1000; unit = 'g'
        elif unit == 'l': val *= 1000; unit = 'ml'
        units.append(("total_" + unit, count * val))

    return units

def units_match(units1, units2):
    # CRITICAL: Strict matching. If we have unit info, it MUST match.
    if not units1 or not units2:
        return False # Safer: If we can't find units on one side, don't risk a mismatch

    # Check packs
    u1_dict = dict(units1)
    u2_dict = dict(units2)

    if u1_dict.get('pack', 1.0) != u2_dict.get('pack', 1.0):
        return False

    # Check weights/volumes
    for key in ['g', 'ml', 'total_g', 'total_ml']:
        if key in u1_dict and key in u2_dict:
            if abs(u1_dict[key] - u2_dict[key]) > 0.1:
                return False
        elif key in u1_dict or key in u2_dict:
            # If one has a specific weight/volume and the other doesn't, it's risky
            return False

    return True

def search_tesco(query):
    print(f"Searching Tesco for: {query}")
    query_clean = " ".join(query.split()[:5])
    url = f"https://www.tesco.com/groceries/en-GB/search?query={requests.utils.quote(query_clean)}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200: return []
        soup = BeautifulSoup(resp.text, "lxml")
        products = []
        items = soup.select('.product-list--list-item')
        for item in items:
            title_tag = item.select_one('h3 a')
            price_tag = item.select_one('.value')
            if title_tag and price_tag:
                title = title_tag.get_text(strip=True)
                try:
                    price = float(price_tag.get_text(strip=True).replace("£", ""))
                    products.append({
                        "retailer": "Tesco",
                        "title": title,
                        "price": price,
                        "url": "https://www.tesco.com" + title_tag['href'],
                        "units": parse_units(title)
                    })
                except: continue
        return products
    except:
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
                price_text = price_tag.get_text(strip=True)
                price_match = re.search(r'£?(\d+\.\d{2})', price_text)
                if price_match:
                    price = float(price_match.group(1))
                    products.append({
                        "retailer": "TK Maxx",
                        "title": title,
                        "price": price,
                        "url": title_tag['href'],
                        "units": parse_units(title)
                    })
        return products
    except:
        return []

def find_best_match(amazon_item, retailer_results):
    amz_units = parse_units(amazon_item['title'])
    if not amz_units: return None # Safety

    for res in retailer_results:
        if units_match(amz_units, res['units']):
            return res
    return None
