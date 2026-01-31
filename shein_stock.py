import requests, os, json
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://www.sheinindia.in/c/sverse-5939-37961"
STATE_FILE = "last_stock.json"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def get_stock():
    r = requests.get(URL, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    text = soup.get_text().lower()
    men = text.count("men")    # simple reliable detect
    women = text.count("women")

    return men, women

def load_last():
    if not os.path.exists(STATE_FILE):
        return 0, 0
    with open(STATE_FILE) as f:
        d = json.load(f)
        return d["men"], d["women"]

def save_current(men, women):
    with open(STATE_FILE, "w") as f:
        json.dump({"men": men, "women": women}, f)

def send_alert(men, women):
    msg = f"""🚨 SHEIN STOCK UP!

👨 Men → {men}
👩 Women → {women}

⏰ {datetime.now().strftime("%d %b %Y, %I:%M %p")}
🔗 {URL}
"""
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg}
    )

# ---- MAIN ----
last_men, last_women = load_last()
men, women = get_stock()

# ONLY notify if stock increased
if (men > last_men) or (women > last_women):
    send_alert(men, women)

save_current(men, women)
