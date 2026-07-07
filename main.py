"""
Sourcing Agent - Advanced main pipeline with Database and WhatsApp Notifications.
"""
from __future__ import annotations
import re, csv, time
from datetime import datetime
import config
from discover_categories import get_filtered_categories
from amazon_bestsellers import get_bestsellers, get_movers_and_shakers
from amazon_new_releases import get_new_releases
from google_trends import get_trend_score
from retailers import search_tesco, search_tkmaxx, search_asda, find_best_match
from profit_calculator import calculate_profit
from brand_risk import is_risky_expanded
from database import init_db, save_scan_result
from notifications import send_whatsapp_alert

def parse_price(price_text: str | None) -> float | None:
    if not price_text: return None
    match = re.search(r"[\d,]+\.\d{2}", price_text.replace("£", ""))
    return float(match.group().replace(",", "")) if match else None

def run():
    print(f"Starting Sourcing Agent - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    init_db()

    categories = get_filtered_categories()

    all_rows = []
    for cat_name, slug in categories.items():
        all_rows.extend(get_new_releases(cat_name, slug))
        all_rows.extend(get_movers_and_shakers(cat_name, slug))
        all_rows.extend(get_bestsellers(cat_name, slug))

    print(f"\nCollected {len(all_rows)} potential listings. Filtering and Matching...\n")

    filtered_rows = []
    for row in all_rows:
        price = parse_price(row.get("price_text"))
        if price is None: continue
        row["amazon_price"] = price
        if price > 100 or is_risky_expanded(row.get("title")): continue
        source = row.get("source")
        row["unsat_score"] = 100 if source == "new_releases" else 80 if source == "movers_and_shakers" else 40
        filtered_rows.append(row)

    filtered_rows.sort(key=lambda r: (-r["unsat_score"], r.get("rank", 999)))

    results = []
    trends_budget = config.TRENDS_MAX_LOOKUPS
    retail_budget = config.RETAILER_SEARCH_MAX_LOOKUPS

    for row in filtered_rows:
        if retail_budget <= 0: break
        title = row.get("title")
        if not title: continue

        tesco_res = search_tesco(title)
        tk_res = search_tkmaxx(title)
        asda_res = search_asda(title)
        retail_budget -= 1

        best_retail_match = find_best_match(row, tesco_res + tk_res + asda_res)

        if best_retail_match:
            row["retail_price"] = best_retail_match["price"]
            row["retailer"] = best_retail_match["retailer"]
            row["retail_url"] = best_retail_match["url"]

            profit_data = calculate_profit(row["retail_price"], row["amazon_price"], row["category"])
            row.update(profit_data)

            if row["profit_margin"] >= 40:
                print(f"  [Match Found] {title} - Profit: £{row['net_profit']} ({row['profit_margin']}%)")

                # Check Trends
                if trends_budget > 0:
                    trend = get_trend_score(title)
                    row["trend_score"], row["momentum_pct"] = trend["avg_interest"], trend["momentum_pct"]
                    trends_budget -= 1

                results.append(row)
                save_scan_result(row)

                # Send Alert
                send_whatsapp_alert(
                    row["title"], row["profit_margin"], row["net_profit"],
                    row["retailer"], row["retail_url"]
                )

        time.sleep(config.REQUEST_DELAY_SECONDS)

    results.sort(key=lambda x: (x["profit_margin"], x.get("momentum_pct", 0), x["unsat_score"]), reverse=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    outfile = f"unsaturated_sourcing_report_{timestamp}.csv"
    fieldnames = ["profit_margin", "net_profit", "unsat_score", "category", "title", "amazon_price", "retail_price", "retailer", "retail_url", "asin", "trend_score", "momentum_pct", "total_costs"]

    with open(outfile, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    print(f"\nDone. {len(results)} unsaturated profitable products written to {outfile}")

if __name__ == "__main__":
    run()
