RISKY_BRANDS = [
    "Apple", "Nike", "Adidas", "Lego", "Samsung", "Sony", "Dyson",
    "Ghd", "Chanel", "Dior", "Gucci", "Prada", "Fitbit", "GoPro"
]

def is_risky(title):
    if not title: return False
    for brand in RISKY_BRANDS:
        if brand.lower() in title.lower():
            return True
    return False

# Expand with some common OA (Online Arbitrage) risky brands
OA_RISKY_BRANDS = [
    "Huggies", "Pampers", "Gillette", "Oral-B", "Aveeno", "Neutrogena",
    "La Roche-Posay", "CeraVe", "Vichy", "Estee Lauder", "Clinique"
]

def is_risky_expanded(title):
    if is_risky(title): return True
    for brand in OA_RISKY_BRANDS:
        if brand.lower() in title.lower():
            return True
    return False
