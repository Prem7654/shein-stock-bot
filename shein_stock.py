import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

SHEIN_URL = "https://www.sheinindia.in/c/sverse-5939-37961"
LAST_FILE = "last_stock.json"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
EVENT = os.getenv("GITHUB_EVENT_NAME")

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def safe_fetch_count(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.select(".product-card")  # SHEIN cards
        return len(items)
    except Exception:
        return 0


def load_last():
    if not os.path.exists(LAST_FILE):
        return {"men": 0, "women": 0}
    with open(LAST_FILE, "r") as f:
        return json.load(f)


def save_last(men, women):
    with open(LAST_FILE, "w") as f:
        json.dump({"men": men, "women": women}, f)


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text,
        "disable_web_page_preview": False
    })


def main():
    old = load_last()

    men = safe_fetch_count(SHEIN_URL)
    women = safe_fetch_count(SHEIN_URL)

    men_diff = men - old["men"]
    women_diff = women - old["women"]

    is_manual = EVENT == "workflow_dispatch"

    # ❌ auto run me no change = no message
    if not is_manual and men_diff <= 0 and women_diff <= 0:
        return

    title = "📦 SHEIN STOCK (Manual Check)" if is_manual else "🚨 SHEIN STOCK UPDATE"
    now = datetime.now().strftime("%d %b %Y, %I:%M %p")

    msg = f"""{title}

👨 Men → {old["men"]} + {men_diff if men_diff > 0 else 0} ⬆️ = {men}
👩 Women → {old["women"]} + {women_diff if women_diff > 0 else 0} ⬆️ = {women}

⏰ {now}
🔗 {SHEIN_URL}
"""

    send_message(msg)
    save_last(men, women)


if __name__ == "__main__":
    main()
