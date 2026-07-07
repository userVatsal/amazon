"""
Trend layer entry point.

Run: python main.py

Output: trend_report_<timestamp>.csv — ranked list of candidate products
with Amazon rank data + Google Trends momentum + a combined trend_score
+ Amazon's own disclosed "X+ bought in past month" badge (bucketed,
real data — see bought_count.py) for the top-ranked candidates.

This is layer 1 of the pipeline. It tells you WHAT looks worth chasing.
It does NOT check retailer prices or Amazon fees/margin — that's the
price-match layer and profit calculator, built next.
"""
from __future__ import annotations
import re
import csv
from datetime import datetime

from config import CATEGORIES, TRENDS_MAX_LOOKUPS, BOUGHT_COUNT_MAX_LOOKUPS
from amazon_bestsellers import get_bestsellers, get_movers_and_shakers
from google_trends import get_trend_score
from bought_count import get_bought_last_month


def parse_price(price_text: str | None) -> float | None:
    if not price_text:
        return None
    match = re.search(r"[\d,]+\.\d{2}", price_text.replace("£", ""))
    return float(match.group().replace(",", "")) if match else None


def parse_rating_count(rating_text: str | None) -> float | None:
    if not rating_text:
        return None
    match = re.search(r"[\d.]+", rating_text)
    return float(match.group()) if match else None


def score_row(row: dict) -> float:
    """Combines Amazon rank (lower = better) and Trends momentum
    (higher = better) into one comparable score, 0-100."""
    rank_score = max(0, 100 - row.get("rank", 100))
    momentum = row.get("momentum_pct") or 0
    momentum_score = max(0, min(100, 50 + momentum))  # center at 50
    mover_bonus = 15 if row.get("source") == "movers_and_shakers" else 0
    return round((rank_score * 0.5) + (momentum_score * 0.4) + mover_bonus, 1)


def run():
    all_rows = []

    for category_name, slug in CATEGORIES.items():
        all_rows.extend(get_bestsellers(category_name, slug))
        all_rows.extend(get_movers_and_shakers(category_name, slug))

    print(f"\nCollected {len(all_rows)} raw listings. Scoring trend momentum...\n")

    # Only spend Trends calls on the best-ranked candidates (rank <= a
    # threshold), capped at TRENDS_MAX_LOOKUPS overall — this is the
    # single biggest lever against Google's 429 rate limiting. Every
    # other row still gets written out, just without momentum data.
    all_rows.sort(key=lambda r: r.get("rank", 999))
    lookup_budget = TRENDS_MAX_LOOKUPS

    for row in all_rows:
        row["price_gbp"] = parse_price(row.get("price_text"))
        row["rating_score"] = parse_rating_count(row.get("rating_text"))

        if row.get("title") and lookup_budget > 0:
            trend = get_trend_score(row.get("title"))
            lookup_budget -= 1
        else:
            trend = {"query": None, "avg_interest": None, "momentum_pct": None}

        row["trend_query"] = trend["query"]
        row["avg_interest"] = trend["avg_interest"]
        row["momentum_pct"] = trend["momentum_pct"]

        row["trend_score"] = score_row(row)

    all_rows.sort(key=lambda r: r["trend_score"], reverse=True)

    # Bought-count badge is the most request-heavy lookup (one full
    # product page per item), so it only runs on the FINAL top-ranked
    # candidates — the ones actually worth a closer look — not the
    # whole list.
    print(f"\nChecking 'bought in past month' badge on top {BOUGHT_COUNT_MAX_LOOKUPS} candidates...\n")
    bought_budget = BOUGHT_COUNT_MAX_LOOKUPS
    for row in all_rows:
        if row.get("asin") and bought_budget > 0:
            row["bought_last_month"] = get_bought_last_month(row["asin"])
            bought_budget -= 1
        else:
            row["bought_last_month"] = None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    outfile = f"trend_report_{timestamp}.csv"
    fieldnames = [
        "trend_score", "category", "source", "rank", "asin", "title",
        "price_gbp", "rating_score", "avg_interest", "momentum_pct",
        "bought_last_month",
    ]
    with open(outfile, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Done. {len(all_rows)} products written to {outfile}")
    print("Next: feed the top rows (highest trend_score) into the price-match layer.")


if __name__ == "__main__":
    run()