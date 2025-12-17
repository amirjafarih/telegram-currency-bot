import requests
from bs4 import BeautifulSoup
import time

BOT_TOKEN = "2002214368:AAE41G7Wr5EAaJBZu3YZRjmRKlCjI37-MNg"
CHANNEL = "@price_offhuhfcc"

TALA_URL = (
    "https://api.allorigins.win/raw?"
    "url=https://www.tala.ir/webservice/price_live.php?new=1"
)

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHANNEL, "text": text})

def parse_tala():
    r = requests.get(TALA_URL, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    data = []
    for td in soup.find_all("td"):
        txt = td.get_text(strip=True)
        if txt:
            data.append(txt)
    return data

while True:
    try:
        data = parse_tala()
        msg = "📊 قیمت لحظه‌ای طلا و سکه\n\n"

        for i in range(0, len(data), 2):
            price = data[i]
            name = data[i+1] if i+1 < len(data) else ""
            msg += f"{name}: {price}\n"

        send_message(msg)
        print("ارسال شد ✅")

    except Exception as e:
        print("خطا:", e)

    time.sleep(60)
