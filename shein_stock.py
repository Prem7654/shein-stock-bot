import os
import json
import requests
from datetime import datetime

MEN_API = "https://www.sheinindia.in/pd/search/get_products?cat_id=5939&page=1&page_size=1"
WOMEN_API = "https://www.sheinindia.in/pd/search/get_products?cat_id=37961&page=1&page_size=1"
SHEIN_LINK = "https://www.sheinindia.in/c/sverse-5939-37961"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
EVENT = os.getenv("GITHUB_EVENT_NAME")

LAST_FILE = "last_stock.json"


def fetch_count(url):
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    data = r.json()
    return int(data["info"]["total"])


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text,
        "disable_web_page_preview": False
    })


def load_last():
    if not os.path.exists(LAST_FILE):
        return {"men": 0, "women": 0}
    with open(LAST_FILE, "r") as f:
        return json.load(f)


def save_last(men, women):
    with open(LAST_FILE, "w") as f:
        json.dump({"men": men, "women": women}, f)


def main():
    last = load_last()

    men_now = fetch_count(MEN_API)
    women_now = fetch_count(WOMEN_API)

    men_old = last["men"]
    women_old = last["women"]

    is_manual = EVENT == "workflow_dispatch"

    # --- MANUAL CHECK ---
    if is_manual:
        msg = (
            "📦 SHEIN STOCK (Manual Check)\n\n"
            f"👨 Men → {men_old}\n"
            f"👩 Women → {women_old}\n\n"
            f"🕒 {datetime.now().strftime('%d %b %Y, %I:%M %p')}\n"
            f"🔗 {SHEIN_LINK}"
        )
        send_message(msg)
        return

    # --- AUTO STOCK UP ONLY ---
    if men_now > men_old or women_now > women_old:
        men_added = men_now - men_old
        women_added = women_now - women_old

        msg = (
            "🔔 Shein Stock Update\n\n"
            f"👨 Men → {men_old} + {men_added} ⬆️ = {men_now}\n"
            f"👩 Women → {women_old} + {women_added} ⬆️ = {women_now}\n\n"
            f"⏰ {datetime.now().strftime('%d %b %Y, %I:%M %p')}\n"
            f"🔗 {SHEIN_LINK}"
        )

        send_message(msg)
        save_last(men_now, women_now)


if __name__ == "__main__":
    main()
