"""
Config for the trend layer.
Edit CATEGORIES to focus on niches you actually want to source in
(matching what's realistically stocked at Tesco/Asda/TK Maxx: home,
beauty, toys, kitchen, grocery, health & personal care work best —
electronics/luxury are heavily gated on Amazon, avoid early on).
"""

# Amazon UK Best Sellers category slugs.
# Full list: https://www.amazon.co.uk/gp/bestsellers -> browse categories,
# copy the slug from the URL (the part after /bestsellers/).
CATEGORIES = {
    "toys": "toys",
    "kitchen": "kitchen",
    "health-personal-care": "drugstore",
    "beauty": "beauty",
    "grocery": "grocery",
}

# How many rank positions to pull per category (Amazon shows top 100).
TOP_N = 50

# Google Trends UK: how many days back to look for momentum.
TRENDS_TIMEFRAME = "today 1-m"
TRENDS_GEO = "GB"

# Google's free Trends endpoint aggressively rate-limits (HTTP 429) if
# hit too many times in a row. Two mitigations: space calls out much
# more than the scraping delay, and only bother checking momentum for
# a capped number of top candidates (by Amazon rank) instead of every
# single product — you don't need Trends data on rank #47 in Grocery.
TRENDS_DELAY_SECONDS = 12
TRENDS_MAX_LOOKUPS = 30
TRENDS_MAX_RETRIES = 2

# Minimum acceptable ROI% before a product is even worth checking
# against retail prices in the next layer. This is a pre-filter, not
# the final profit calculation.
MIN_ROI_PREFILTER = 25

# "X+ bought in past month" badge lookups: real Amazon-disclosed data,
# but requires one extra page fetch per product, so cap it hard and
# space it out — this is the most request-heavy part of the pipeline.
BOUGHT_COUNT_MAX_LOOKUPS = 20
BOUGHT_COUNT_DELAY_SECONDS = 4

# Request pacing to avoid getting rate-limited / blocked.
REQUEST_DELAY_SECONDS = 3
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
# Retailer search caps to avoid IP blocking
RETAILER_SEARCH_MAX_LOOKUPS = 20
