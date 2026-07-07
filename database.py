import sqlite3
from datetime import datetime

DB_NAME = "sourcing_agent.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            asin TEXT PRIMARY KEY,
            title TEXT,
            category TEXT,
            last_updated DATETIME
        )
    ''')

    # History table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asin TEXT,
            amazon_price REAL,
            amazon_rank INTEGER,
            retail_price REAL,
            retailer TEXT,
            profit_margin REAL,
            timestamp DATETIME,
            FOREIGN KEY (asin) REFERENCES products (asin)
        )
    ''')

    conn.commit()
    conn.close()

def save_scan_result(row):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    now = datetime.now()
    asin = row.get("asin")

    if not asin:
        return

    # Update or insert product
    cursor.execute('''
        INSERT INTO products (asin, title, category, last_updated)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(asin) DO UPDATE SET
            title=excluded.title,
            category=excluded.category,
            last_updated=excluded.last_updated
    ''', (asin, row.get("title"), row.get("category"), now))

    # Record history
    cursor.execute('''
        INSERT INTO history (asin, amazon_price, amazon_rank, retail_price, retailer, profit_margin, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        asin,
        row.get("amazon_price"),
        row.get("rank"),
        row.get("retail_price"),
        row.get("retailer"),
        row.get("profit_margin"),
        now
    ))

    conn.commit()
    conn.close()

def get_product_history(asin):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM history WHERE asin = ? ORDER BY timestamp DESC', (asin,))
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
