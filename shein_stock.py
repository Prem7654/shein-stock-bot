import os
import json
import requests
from datetime import datetime

SHEIN_LINK = "https://www.sheinindia.in/c/sverse-5939-37961"
MEN_API = "https://www.sheinindia.in/api/product/list?cat_id=5939&page=1&limit=200"
WOMEN_API = "https://www.sheinindia.in/api/product/list?cat_id=37961&page=1&limit=200"

LAST_FILE = "last_stock.json"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
EVENT = os.getenv("GITHUB_EVENT_NAME")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13)",
    "Accept": "application/json",
    "Referer": "https://www.sheinindia.in/"
}

def safe_fetch_count(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        if not r.text.strip().startswith("{"):
            return 0
        data = r.json()
        return int(data.get("info", {}).get("total", 0))
    except:
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

    men = safe_fetch_count(MEN_API)
    women = safe_fetch_count(WOMEN_API)

    # ==== TEST MODE (TEMPORARY) ====
    men = 5
    women = 2

    now = datetime.now().strftime("%d %b %Y, %I:%M %p")

    men_diff = men - old["men"]
    women_diff = women - old["women"]

    is_manual = EVENT == "workflow_dispatch"

    # ❌ Auto me sirf STOCK UP
    if not is_manual and men_diff <= 0 and women_diff <= 0:
        return

    title = "📦 SHEIN STOCK (Manual Check)" if is_manual else "🔔 SHEIN STOCK UPDATE"

    msg = f"""{title}

👨 Men → {old["men"]} + {men_diff if men_diff>0 else 0} ⬆️ = {men}
👩 Women → {old["women"]} + {women_diff if women_diff>0 else 0} ⬆️ = {women}

⏰ {now}
🔗 {SHEIN_LINK}
"""

    send_message(msg)

    # save only when stock increases OR manual
    if men_diff > 0 or women_diff > 0 or is_manual:
        save_last(men, women)

if __name__ == "__main__":
    main()
