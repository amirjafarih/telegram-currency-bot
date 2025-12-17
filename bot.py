import requests
from bs4 import BeautifulSoup
import time

BOT_TOKEN = "2002214368:AAE41G7Wr5EAaJBZu3YZRjmRKlCjI37-MNg"
CHANNEL = "@price_offhuhfcc"

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHANNEL, "text": text})

def parse_tala():
    url = "https://www.tala.ir/webservice/price_live.php?new=1"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    
    lines = []
    for item in soup.find_all("td"):
        text = item.get_text(strip=True)
        lines.append(text)
    return lines

while True:
    try:
        data = parse_tala()
        msg = "📊 قیمت لحظه‌ای طلا و سکه\n\n"

        for i in range(0, len(data), 2):
            val = data[i]
            name = data[i+1] if i+1 < len(data) else ""
            msg += f"{name}: {val}\n"

        send_message(msg)
        print("پیام ارسال شد ✅")
    except Exception as e:
        print("خطا:", e)

    time.sleep(60)  # هر ۱ دقیقه
