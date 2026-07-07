"""
Config for the trend layer.
"""
CATEGORIES = {
    "toys": "toys",
    "kitchen": "kitchen",
    "health-personal-care": "drugstore",
    "beauty": "beauty",
    "grocery": "grocery",
}
TOP_N = 50
TRENDS_TIMEFRAME = "today 1-m"
TRENDS_GEO = "GB"
TRENDS_DELAY_SECONDS = 12
TRENDS_MAX_LOOKUPS = 30
TRENDS_MAX_RETRIES = 2
MIN_ROI_PREFILTER = 25
BOUGHT_COUNT_MAX_LOOKUPS = 20
BOUGHT_COUNT_DELAY_SECONDS = 4
REQUEST_DELAY_SECONDS = 3
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
RETAILER_SEARCH_MAX_LOOKUPS = 50
