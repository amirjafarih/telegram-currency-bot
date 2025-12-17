import requests
import time

BOT_TOKEN = "2002214368:AAE41G7Wr5EAaJBZu3YZRjmRKlCjI37-MNg"
CHANNEL = "@price_offhuhfcc"
GOLDAPI_KEY = "goldapi-9obs6smjadg28j-io"

DOLLAR_API = "https://api.exchangerate.host/latest?base=USD&symbols=IRR"

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHANNEL, "text": text})

def get_prices():
    # قیمت انس طلا
    r_gold = requests.get("https://www.goldapi.io/api/XAU/USD",
                          headers={"x-access-token": GOLDAPI_KEY}).json()
    ounce_price = r_gold.get("price", 0)

    # نرخ دلار به ریال
    r_usd = requests.get(DOLLAR_API).json()
    usd_to_irr = r_usd.get("rates", {}).get("IRR", None)
    if usd_to_irr is None:
        usd_to_irr = 42000  # fallback

    # قیمت طلا ۱۸ عیار ریالی
    gold_18 = ounce_price * usd_to_irr * 0.75

    return round(gold_18), round(ounce_price)

while True:
    try:
        gold_18, ounce_price = get_prices()
        msg = f"📊 قیمت طلا ۱۸ عیار: {gold_18:,} ریال\n💰 انس طلا: {ounce_price} USD"
        send_message(msg)
        print("ارسال شد ✅")
    except Exception as e:
        print("خطا:", e)

    time.sleep(60)
