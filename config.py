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

# Minimum acceptable ROI% before a product is even worth checking
# against retail prices in the next layer. This is a pre-filter, not
# the final profit calculation.
MIN_ROI_PREFILTER = 25

# Request pacing to avoid getting rate-limited / blocked.
REQUEST_DELAY_SECONDS = 3
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
