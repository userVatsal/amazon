"""
Pulls UK search-interest momentum from Google Trends for candidate
product titles. This is the closest legitimate proxy to "what people
are searching for" — there is no public API for Amazon's own internal
search data, so Google Trends (UK-filtered) is the standard substitute
the sourcing-tool industry actually uses.

Note: pytrends is an unofficial wrapper around Google Trends' web
interface. It's widely used but can be rate-limited if you query too
many terms too fast — keep batches small and cached.
"""
import time
from pytrends.request import TrendReq
from config import TRENDS_TIMEFRAME, TRENDS_GEO, REQUEST_DELAY_SECONDS


def get_trend_score(product_title: str) -> dict:
    """Returns a simple momentum score: average interest over the
    period and the % change from first half to second half of it."""
    pytrends = TrendReq(hl="en-GB", tz=0)
    # Trim titles to a short, searchable query — full Amazon titles are
    # too long/noisy for Trends to match well.
    query = " ".join(product_title.split()[:5]) if product_title else None
    if not query:
        return {"query": None, "avg_interest": None, "momentum_pct": None}

    try:
        pytrends.build_payload([query], timeframe=TRENDS_TIMEFRAME, geo=TRENDS_GEO)
        df = pytrends.interest_over_time()
        time.sleep(REQUEST_DELAY_SECONDS)

        if df.empty or query not in df.columns:
            return {"query": query, "avg_interest": 0, "momentum_pct": 0}

        series = df[query]
        avg_interest = round(series.mean(), 1)

        half = len(series) // 2
        first_half_avg = series[:half].mean() if half > 0 else series.mean()
        second_half_avg = series[half:].mean()
        momentum_pct = (
            round(((second_half_avg - first_half_avg) / first_half_avg) * 100, 1)
            if first_half_avg > 0 else 0
        )
        return {"query": query, "avg_interest": avg_interest, "momentum_pct": momentum_pct}

    except Exception as e:
        print(f"  [warn] trends lookup failed for '{query}': {e}")
        return {"query": query, "avg_interest": None, "momentum_pct": None}
