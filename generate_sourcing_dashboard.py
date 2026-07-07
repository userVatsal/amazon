import csv, glob, json, os, sqlite3
from datetime import datetime
from database import DB_NAME

def find_latest_report() -> str:
    files = glob.glob("unsaturated_sourcing_report_*.csv")
    if not files: return None
    return max(files, key=os.path.getmtime)

def load_rows(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def get_history_summary(asin):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT amazon_price, timestamp FROM history WHERE asin = ? ORDER BY timestamp DESC LIMIT 5', (asin,))
        rows = cursor.fetchall()
        conn.close()
        if len(rows) > 1:
            latest = rows[0][0]
            oldest = rows[-1][0]
            change = ((latest - oldest) / oldest) * 100
            return f"{'+' if change > 0 else ''}{change:.1f}% price change"
        return "No history"
    except:
        return "History error"

def build_html(rows: list[dict], source_file: str) -> str:
    clean = [r for r in rows if r.get("title")]
    clean.sort(key=lambda r: (float(r.get("profit_margin") or 0), float(r.get("unsat_score") or 0)), reverse=True)
    top = clean[:40]

    chart_labels = json.dumps([r["title"][:30] for r in top[:15]])
    chart_margins = json.dumps([float(r.get("profit_margin") or 0) for r in top[:15]])

    table_rows = []
    for r in top:
        history = get_history_summary(r.get('asin'))
        table_rows.append(f"""<tr>
            <td><strong>{r.get('profit_margin','')}%</strong></td>
            <td>£{r.get('net_profit','')}</td>
            <td><span class="badge {'badge-new' if r.get('unsat_score') == '100' else 'badge-mover' if r.get('unsat_score') == '80' else 'badge-saturated'}">
                { 'New' if r.get('unsat_score') == '100' else 'Rising' if r.get('unsat_score') == '80' else 'Saturated' }
            </span></td>
            <td class="title">{r.get('title','')}<br><small style="color:#888">{history}</small></td>
            <td>£{r.get('amazon_price','')}</td>
            <td>£{r.get('retail_price','')}</td>
            <td>{r.get('retailer','')}</td>
            <td><a href="{r.get('retail_url','')}" target="_blank">View</a></td>
            <td>{r.get('trend_score','') or '-'}</td>
        </tr>""")

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Advanced Sourcing Dashboard</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
<style>
  body {{ font-family: -apple-system, Arial, sans-serif; margin: 24px; background: #f7f7f8; color: #1a1a1a; }}
  h1 {{ margin-bottom: 4px; }}
  .subtitle {{ color: #666; margin-bottom: 24px; font-size: 14px; }}
  table {{ border-collapse: collapse; width: 100%; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid #eee; font-size: 13px; }}
  th {{ background: #1a1a2e; color: white; position: sticky; top: 0; }}
  td.title {{ max-width: 300px; }}
  .chart-wrap {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  .badge {{ padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; color: white; }}
  .badge-new {{ background: #e67e22; }}
  .badge-mover {{ background: #3498db; }}
  .badge-saturated {{ background: #95a5a6; }}
</style>
</head>
<body>
  <h1>Advanced Sourcing Dashboard</h1>
  <div class="subtitle">Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Source: {source_file}</div>
  <div class="chart-wrap"><canvas id="marginChart" height="90"></canvas></div>
  <table>
    <thead><tr><th>Margin</th><th>Net Profit</th><th>Status</th><th>Title & History</th><th>Amazon Price</th><th>Retail Price</th><th>Retailer</th><th>Link</th><th>Trend</th></tr></thead>
    <tbody>{"\n".join(table_rows)}</tbody>
  </table>
<script>
new Chart(document.getElementById('marginChart'), {{
  type: 'bar',
  data: {{
    labels: {chart_labels},
    datasets: [{{ label: 'Profit Margin %', data: {chart_margins}, backgroundColor: '#2ecc71' }}]
  }},
  options: {{
    plugins: {{ legend: {{ display: false }}, title: {{ display: true, text: 'Top 15 by Profit Margin %' }} }},
    scales: {{ y: {{ beginAtZero: true }}, x: {{ ticks: {{ autoSkip: false, maxRotation: 60, minRotation: 40 }} }} }}
  }}
}});
</script>
</body>
</html>"""

def run():
    report_file = find_latest_report()
    if not report_file: return
    rows = load_rows(report_file)
    html = build_html(rows, report_file)
    with open("sourcing_dashboard.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Built advanced sourcing_dashboard.html from {report_file}")

if __name__ == "__main__": run()
