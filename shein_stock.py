import requests
from bs4 import BeautifulSoup
import telegram
import os
from datetime import datetime

URL = "https://www.sheinindia.in/c/sverse-5939-37961"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def get_counts():
    r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")

    text = soup.get_text(" ", strip=True)

    men = text.lower().count("men")
    women = text.lower().count("women")

    return men, women

def main():
    men, women = get_counts()
    now = datetime.now().strftime("%d %b %Y, %I:%M %p")

    msg = f"""🔔 SHEIN STOCK UPDATE

👨 Men → {men}
👩 Women → {women}

⏰ {now}
🔗 {URL}
"""

    bot = telegram.Bot(token=BOT_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=msg)

if __name__ == "__main__":
    main()
