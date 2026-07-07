import requests
from bs4 import BeautifulSoup
import time
import re
import json

# Mobile user agent is successful for Tesco
MOBILE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
}

def parse_units(title):
    if not title: return []
    title = title.lower()
    units = []

    # Pack size
    pack_match = re.search(r'pack of (\d+)', title) or re.search(r'(\d+)\s*pack', title)
    pack_size = float(pack_match.group(1)) if pack_match else 1.0
    units.append(("pack", pack_size))

    # Washes (common in grocery/laundry)
    wash_match = re.search(r'(\d+)\s*washes', title)
    if wash_match:
        units.append(("washes", float(wash_match.group(1))))

    # Volume/Weight
    vol_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(g|kg|ml|l)\b', title)
    for val, unit in vol_matches:
        val = float(val)
        if unit == 'kg': val *= 1000; unit = 'g'
        elif unit == 'l': val *= 1000; unit = 'ml'
        units.append((unit, val))
        if pack_size > 1:
            units.append(("total_" + unit, val * pack_size))

    # Multiplier (e.g. 6 x 330ml)
    mult_matches = re.findall(r'(\d+)\s*x\s*(\d+(?:\.\d+)?)\s*(g|kg|ml|l)\b', title)
    for count, val, unit in mult_matches:
        count = float(count)
        val = float(val)
        if unit == 'kg': val *= 1000; unit = 'g'
        elif unit == 'l': val *= 1000; unit = 'ml'
        units.append(("total_" + unit, count * val))

    return units

def units_match(units1, units2):
    if not units1 or not units2: return False
    u1_dict = dict(units1)
    u2_dict = dict(units2)

    matched_at_least_one_specific = False

    # Compare common units
    for key in ['washes', 'g', 'ml', 'total_g', 'total_ml']:
        if key in u1_dict and key in u2_dict:
            matched_at_least_one_specific = True
            if abs(u1_dict[key] - u2_dict[key]) > 0.1:
                return False
        elif key in u1_dict or key in u2_dict:
            return False

    # If no specific units matched, check pack size
    if not matched_at_least_one_specific:
        if u1_dict.get('pack', 1.0) != u2_dict.get('pack', 1.0):
            return False
        return True

    return True

def search_tesco(query):
    query_clean = " ".join(query.split()[:5])
    url = f"https://www.tesco.com/groceries/en-GB/search?query={requests.utils.quote(query_clean)}"
    print(f"[Tesco] Searching: {url}")
    try:
        resp = requests.get(url, headers=MOBILE_HEADERS, timeout=10)
        print(f"[Tesco] Status: {resp.status_code}")
        if resp.status_code != 200:
            return []

        products = []
        soup = BeautifulSoup(resp.text, "lxml")
        script = soup.find("script", id="__NEXT_DATA__")
        if script:
            try:
                data = json.loads(script.string)
                items = data.get("props", {}).get("pageProps", {}).get("initialState", {}).get("search", {}).get("results", {}).get("items", [])
                for item in items:
                    p = item.get("product", {})
                    title = p.get("title")
                    price = p.get("price", {}).get("actual") or p.get("unitPrice")
                    if title and price:
                        products.append({
                            "retailer": "Tesco",
                            "title": title,
                            "price": float(price),
                            "url": "https://www.tesco.com/groceries/en-GB/products/" + str(p.get("id", "")),
                            "units": parse_units(title)
                        })
                if products: print(f"  -> Found {len(products)} products via JSON")
            except: pass

        if not products:
            titles = re.findall(r'\"title\":\"([^\"]+)\"', resp.text)
            prices = re.findall(r'\"unitPrice\":([0-9.]+)', resp.text)
            if titles and prices:
                for t, p in zip(titles, prices):
                    if len(t) > 5 and not t.startswith("Sort and filter") and not t.startswith("Tesco Groceries"):
                        products.append({
                            "retailer": "Tesco",
                            "title": t,
                            "price": float(p),
                            "url": url,
                            "units": parse_units(t)
                        })
                if products: print(f"  -> Found {len(products)} products via Regex")

        if not products:
            print("  -> No products found on page.")

        return products
    except Exception as e:
        print(f"  -> Error: {e}")
        return []

def search_tkmaxx(query):
    query_clean = " ".join(query.split()[:4])
    url = f"https://www.tkmaxx.com/uk/en/search?text={requests.utils.quote(query_clean)}"
    print(f"[TK Maxx] Searching: {url}")
    try:
        resp = requests.get(url, headers=MOBILE_HEADERS, timeout=10)
        print(f"[TK Maxx] Status: {resp.status_code}")
        # Standard HTTP requests are typically blocked by Cloudflare (403)
        if resp.status_code == 403:
            print("  -> [WARNING] Blocked by Cloudflare (403). Requires browser automation.")
        return []
    except Exception as e:
        print(f"  -> Error: {e}")
        return []

def search_asda(query):
    query_clean = " ".join(query.split()[:4])
    url = f"https://groceries.asda.com/search/{requests.utils.quote(query_clean)}"
    print(f"[Asda] Searching: {url}")
    try:
        resp = requests.get(url, headers=MOBILE_HEADERS, timeout=10)
        print(f"[Asda] Status: {resp.status_code}")
        # Asda is very JS-heavy and typically returns 403 or empty 200 without a session
        if resp.status_code == 403:
            print("  -> [WARNING] Blocked by anti-bot measures (403).")
        return []
    except Exception as e:
        print(f"  -> Error: {e}")
        return []

def find_best_match(amazon_item, retailer_results):
    amz_units = parse_units(amazon_item['title'])
    if not amz_units: return None
    for res in retailer_results:
        if units_match(amz_units, res['units']):
            return res
    return None
