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
RUN_INTERVAL_HOURS = 6

# WhatsApp Notifications (Optional)
# 1. Message +34 644 20 13 23 on WhatsApp with "I allow callmebot to send me messages"
# 2. You will get an API Key. Enter it below along with your phone number (intl format).
WHATSAPP_PHONE = ""
WHATSAPP_API_KEY = ""
