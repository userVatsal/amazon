import requests
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}
url = "https://www.amazon.co.uk/gp/new-releases/beauty"
resp = requests.get(url, headers=HEADERS)
print(f"Status: {resp.status_code}")
if "new-releases" in resp.text:
    print("Found new releases")
