# Trend Layer (Layer 1 of the sourcing agent)

Finds what looks like it's trending on Amazon UK right now, as a
shortlist for the next layer (price-matching against Tesco/Asda/TK Maxx).

## What this actually does
- Pulls Amazon UK's public **Best Sellers** and **Movers & Shakers**
  pages for the categories in `config.py`.
- Cross-checks each product title against **Google Trends UK** to see
  if search interest is rising or falling.
- Combines both into a single `trend_score` and writes a ranked CSV.

## What this does NOT do (and nothing legally can)
- There's no public feed of Amazon's actual internal search/purchase
  data. Best Sellers rank + Trends momentum is the standard proxy the
  whole sourcing-tool industry uses instead — it's a good signal, not
  ground truth.
- It doesn't check retailer prices yet (next layer).
- It doesn't check Amazon fees, gating, or margin yet (also next layer).

## Setup
```bash
pip install -r requirements.txt
python main.py
```
Takes a few minutes — it deliberately paces requests (`REQUEST_DELAY_SECONDS`
in config.py) to avoid getting IP-blocked by Amazon or rate-limited by
Google Trends. Don't drop this to 0 and don't run it every few minutes;
that's how sourcing tools get their IP banned.

## Before you run this seriously
1. **Selectors will break.** Amazon changes its Best Sellers page markup
   periodically. If `main.py` runs but every `asin`/`title` comes back
   `None`, open the page in a browser, inspect the current HTML, and
   update the CSS selectors in `amazon_bestsellers.py`.
2. **Scraping Amazon is a grey area under their Conditions of Use**,
   not a criminal offence, but it's not officially sanctioned either.
   Light personal use is what people do in practice; don't scale this
   into hundreds of requests a minute from one IP. If OutputLens-style
   reliability matters to you, budget for **Keepa's API** (~£20/month)
   which gives you the same rank/price history data through a proper
   paid, ToS-compliant API instead of scraping.
3. **Google Trends is also unofficial** (pytrends wraps the public web
   UI, no official API exists). It's the industry-standard proxy for
   "what people are searching for" since Amazon doesn't expose that.

## Tuning
- `config.CATEGORIES` — add/remove Amazon category slugs.
- `config.TOP_N` — how deep into each list to go (max ~100).
- `score_row()` in `main.py` — the weighting between rank position and
  Trends momentum; adjust once you see real output and know what
  correlates with things that actually sell.

## Next layer (not built yet)
Take the top N rows of `trend_report_*.csv` (highest `trend_score`) and
feed the `title`/`asin` into a price-match module against Tesco, Asda,
and TK Maxx product search, then run each match through a profit
calculator (buy price + VAT + Amazon referral fee + FBA fee vs. current
Amazon sell price) before anything gets bought.
