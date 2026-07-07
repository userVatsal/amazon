# Amazon UK Sourcing Agent

Automated tool to find profitable products from UK retailers (Tesco, TK Maxx) to sell on Amazon UK.

## Features
- **Trend Detection**: Identifies trending products using Amazon Best Sellers and Google Trends.
- **Dynamic Category Discovery**: Automatically finds "Open" and "Non-returnable" categories.
- **Retailer Price Matching**: Searches for identical items (with unit/weight matching) at Tesco and TK Maxx.
- **Profit Calculation**: Estimates net profit factoring in referral fees, FBA fees, and fixed monthly costs.
- **Risk Mitigation**: Filters out brands known for Intellectual Property (IP) complaints.

## Requirements
- Python 3.8+
- Requirements from `requirements.txt`

## Usage
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the sourcing agent:
   ```bash
   python main.py
   ```
3. Generate the visual dashboard:
   ```bash
   python generate_sourcing_dashboard.py
   ```
4. Open `sourcing_dashboard.html` in your browser to view the results.

## Configuration
Edit `config.py` to adjust:
- `RETAILER_SEARCH_MAX_LOOKUPS`: Limit how many products to search for at retailers (prevents IP blocking).
- `TRENDS_MAX_LOOKUPS`: Limit Google Trends requests.
- `REQUEST_DELAY_SECONDS`: Delay between requests to avoid rate limits.

## Disclaimer
Scraping retail websites is subject to their Terms of Service. Use this tool responsibly and infrequently.
