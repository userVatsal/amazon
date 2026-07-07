def calculate_profit(buy_price, sell_price, category, weight_kg=0.5):
    """
    Calculates net profit and margin.
    buy_price: price from retailer
    sell_price: price on Amazon
    category: for referral fee calculation
    weight_kg: for FBA fee calculation
    """
    # 1. Referral Fee (approx 15% for most categories)
    referral_fee_rate = 0.15
    if category.lower() in ["grocery", "beauty"]:
        referral_fee_rate = 0.08 if sell_price < 10 else 0.15

    referral_fee = sell_price * referral_fee_rate

    # 2. FBA Fee (Estimate for a small/medium parcel in UK)
    # Average ~£3.50 for many common items
    fba_fee = 3.50
    if weight_kg < 0.1: fba_fee = 2.50
    elif weight_kg > 1.0: fba_fee = 5.00

    # 3. Fixed Costs (£36/month)
    # Assume selling 100 units a month for pro-rating
    fixed_cost_per_unit = 36.0 / 100.0

    # 4. Total Costs
    total_costs = buy_price + referral_fee + fba_fee + fixed_cost_per_unit

    net_profit = sell_price - total_costs
    profit_margin = (net_profit / sell_price) * 100 if sell_price > 0 else 0

    return {
        "net_profit": round(net_profit, 2),
        "profit_margin": round(profit_margin, 2),
        "total_costs": round(total_costs, 2),
        "referral_fee": round(referral_fee, 2),
        "fba_fee": round(fba_fee, 2)
    }
