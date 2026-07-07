"""
Trend layer entry point.

Run: python main.py

Output: trend_report_<timestamp>.csv — ranked list of candidate products
with Amazon rank data + Google Trends momentum + a combined trend_score.

This is layer 1 of the pipeline. It tells you WHAT looks worth chasing.
It does NOT check retailer prices or Amazon fees/margin — that's the
price-match layer and profit calculator, built next.
"""
import re
import csv
from datetime import datetime

from config import CATEGORIES
from amazon_bestsellers import get_bestsellers, get_movers_and_shakers
from google_trends import get_trend_score


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

    for row in all_rows:
        row["price_gbp"] = parse_price(row.get("price_text"))
        row["rating_score"] = parse_rating_count(row.get("rating_text"))

        trend = get_trend_score(row.get("title"))
        row["trend_query"] = trend["query"]
        row["avg_interest"] = trend["avg_interest"]
        row["momentum_pct"] = trend["momentum_pct"]

        row["trend_score"] = score_row(row)

    all_rows.sort(key=lambda r: r["trend_score"], reverse=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    outfile = f"trend_report_{timestamp}.csv"
    fieldnames = [
        "trend_score", "category", "source", "rank", "asin", "title",
        "price_gbp", "rating_score", "avg_interest", "momentum_pct",
    ]
    with open(outfile, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Done. {len(all_rows)} products written to {outfile}")
    print("Next: feed the top rows (highest trend_score) into the price-match layer.")


if __name__ == "__main__":
    run()
