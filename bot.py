import requests
import time

BOT_TOKEN = "1820374516:AAF14hxxbGfnzvnHEcyufNUBCUXz1Q7WNbw"
CHANNEL = "@price_offhuhfcc"

API_URL = "https://api.alanchand.com/?type=currencies&token=nQQ2hMx1h57VqDH4MmuT"

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHANNEL,
        "text": text
    })

def get_prices():
    return requests.get(API_URL, timeout=10).json()

def format_message(data):
    now = time.strftime("%H:%M")
    msg = f"⏱ {now}\n\n"

    wanted = ["usd", "eur", "aed", "gbp"]
    for k in wanted:
        if k in data:
            i = data[k]
            msg += (
                f"💱 {i['name']}\n"
                f"📥 خرید: {i['buy']}\n"
                f"📤 فروش: {i['sell']}\n\n"
            )

    return msg

while True:
    try:
        send_message(format_message(get_prices()))
        print("sent")
    except Exception as e:
        print("error:", e)

    time.sleep(60)  # هر ۱ دقیقه
