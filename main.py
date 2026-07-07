"""
Sourcing Agent - Main Pipeline
Integrates Amazon trends, Retailer price matching, and Profit calculation.
Focuses on "Unsaturated" opportunities by checking New Releases and Movers & Shakers.
"""
from __future__ import annotations
import re
import csv
import time
from datetime import datetime

from config import (
    TRENDS_MAX_LOOKUPS, BOUGHT_COUNT_MAX_LOOKUPS,
    REQUEST_DELAY_SECONDS, RETAILER_SEARCH_MAX_LOOKUPS
)
from discover_categories import get_filtered_categories
from amazon_bestsellers import get_bestsellers, get_movers_and_shakers
from amazon_new_releases import get_new_releases
from google_trends import get_trend_score
from retailers import search_tesco, search_tkmaxx, find_best_match
from profit_calculator import calculate_profit
from brand_risk import is_risky_expanded

def parse_price(price_text: str | None) -> float | None:
    if not price_text:
        return None
    match = re.search(r"[\d,]+\.\d{2}", price_text.replace("£", ""))
    return float(match.group().replace(",", "")) if match else None

def run():
    print(f"Starting Sourcing Agent (Unsaturated Focus) - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. Discover Categories
    categories = get_filtered_categories()
    print(f"Targeting categories: {', '.join(categories.keys())}")

    all_rows = []
    for cat_name, slug in categories.items():
        all_rows.extend(get_new_releases(cat_name, slug))
        all_rows.extend(get_movers_and_shakers(cat_name, slug))
        all_rows.extend(get_bestsellers(cat_name, slug))

    print(f"\nCollected {len(all_rows)} raw listings. Filtering and Matching...\n")

    filtered_rows = []
    for row in all_rows:
        price = parse_price(row.get("price_text"))
        if price is None:
            continue # CRITICAL: Skip if price cannot be parsed

        row["amazon_price"] = price

        if price > 100:
            continue

        if is_risky_expanded(row.get("title")):
            continue

        source = row.get("source")
        if source == "new_releases": row["unsat_score"] = 100
        elif source == "movers_and_shakers": row["unsat_score"] = 80
        else: row["unsat_score"] = 40

        filtered_rows.append(row)

    filtered_rows.sort(key=lambda r: (-r["unsat_score"], r.get("rank", 999)))

    print(f"Filtered down to {len(filtered_rows)} candidates. Searching retailers (limit {RETAILER_SEARCH_MAX_LOOKUPS})...\n")

    results = []
    trends_budget = TRENDS_MAX_LOOKUPS
    retail_budget = RETAILER_SEARCH_MAX_LOOKUPS

    for row in filtered_rows:
        if retail_budget <= 0: break

        title = row.get("title")
        if not title: continue

        # 2. Search Retailers
        tesco_results = search_tesco(title)
        tk_results = search_tkmaxx(title)
        # Note: Asda implementation currently limited by anti-scraping measures

        retail_budget -= 1

        best_retail_match = find_best_match(row, tesco_results + tk_results)

        if best_retail_match:
            row["retail_price"] = best_retail_match["price"]
            row["retailer"] = best_retail_match["retailer"]
            row["retail_url"] = best_retail_match["url"]

            # 3. Calculate Profit
            profit_data = calculate_profit(row["retail_price"], row["amazon_price"], row["category"])
            row.update(profit_data)

            # 4. Check Trends if profitable
            if row["profit_margin"] >= 40 and trends_budget > 0:
                print(f"  [Match Found] {title} - Profit: £{row['net_profit']} ({row['profit_margin']}%)")
                trend = get_trend_score(title)
                row["trend_score"] = trend["avg_interest"]
                row["momentum_pct"] = trend["momentum_pct"]
                trends_budget -= 1
            else:
                row["trend_score"] = 0
                row["momentum_pct"] = 0

            if row["profit_margin"] >= 40:
                results.append(row)

        time.sleep(REQUEST_DELAY_SECONDS)

    results.sort(key=lambda x: (x["profit_margin"], x.get("momentum_pct", 0), x["unsat_score"]), reverse=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    outfile = f"unsaturated_sourcing_report_{timestamp}.csv"
    fieldnames = [
        "profit_margin", "net_profit", "unsat_score", "category", "title", "amazon_price",
        "retail_price", "retailer", "retail_url", "asin", "trend_score",
        "momentum_pct", "total_costs"
    ]

    with open(outfile, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    print(f"\nDone. {len(results)} unsaturated profitable products written to {outfile}")

if __name__ == "__main__":
    run()
