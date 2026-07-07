# Advanced Amazon UK Sourcing Agent

A professional-grade automated tool to identify profitable, unsaturated products from UK retailers (Tesco, TK Maxx, Asda) to sell on Amazon UK.

## Features
- **Unsaturated Focus**: Prioritizes "Hot New Releases" and "Movers & Shakers" to find trends before they become saturated.
- **Robust Price Matching**: Advanced matching for Tesco (using mobile headers and JSON/Regex parsing) with strict unit/weight verification.
- **Historical Tracking**: Local SQLite database stores every scan, allowing you to track price and rank changes over time.
- **WhatsApp Alerts**: Instant notifications via WhatsApp when a product hitting your 40% profit target is found.
- **Automated Scheduling**: Built-in scheduler to run scans autonomously every few hours.
- **Profit Calculator**: Precise calculation factoring in Amazon referral fees, FBA fees, and your £36/month fixed business costs.
- **Risk Mitigation**: Built-in filter for brands known for IP complaints.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure your settings in `config.py`.

## WhatsApp Setup (Optional)
To receive alerts on your phone:
1. Add **+34 644 20 13 23** to your phone contacts.
2. Send a WhatsApp message to this number: `I allow callmebot to send me messages`.
3. You will receive an API Key.
4. In `config.py`, enter your phone number (international format, e.g., `447123456789`) and the API Key.

## Usage
- **Run Once**: `python main.py`
- **Run Continuously (Scheduler)**: `python scheduler.py`
- **Generate Dashboard**: `python generate_sourcing_dashboard.py`

## Retailer Status
- **Tesco**: Fully supported (Robust).
- **TK Maxx & Asda**: Currently flagged as blocked by anti-bot measures (403). These require advanced browser automation or premium proxy services for production use.

## Disclaimer
This tool is for educational and personal use. Scraping retail websites may violate their Terms of Service.
