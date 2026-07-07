import requests
import config

def send_whatsapp_alert(product_title, margin, net_profit, retailer, link):
    """
    Sends a WhatsApp alert using CallMeBot free API.
    Requires user to have WHATSAPP_PHONE and WHATSAPP_API_KEY in config.py
    """
    phone = getattr(config, 'WHATSAPP_PHONE', None)
    apikey = getattr(config, 'WHATSAPP_API_KEY', None)

    if not phone or not apikey:
        print("[Notifications] WhatsApp credentials missing in config.py. Skipping alert.")
        return

    message = (
        f"*Amazon Profit Alert!* 🚀\n\n"
        f"*Product:* {product_title}\n"
        f"*Margin:* {margin}%\n"
        f"*Net Profit:* £{net_profit}\n"
        f"*Retailer:* {retailer}\n"
        f"*Link:* {link}"
    )

    url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={requests.utils.quote(message)}&apikey={apikey}"

    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            print(f"[Notifications] WhatsApp alert sent for {product_title}")
        else:
            print(f"[Notifications] Failed to send WhatsApp alert. Status: {resp.status_code}")
    except Exception as e:
        print(f"[Notifications] Error sending alert: {e}")

if __name__ == "__main__":
    # Test (will fail if credentials missing)
    send_whatsapp_alert("Test Product", 45, 12.50, "Tesco", "https://tesco.com")
