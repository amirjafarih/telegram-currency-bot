import requests
import time

BOT_TOKEN = "2002214368:AAE41G7Wr5EAaJBZu3YZRjmRKlCjI37-MNg"
CHANNEL = "@price_offhuhfcc"

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHANNEL, "text": text})

def get_gold_price():
    # قیمت اونس جهانی طلا (USD) از Metals-API رایگان (demo key)
    r1 = requests.get("https://metals-api.com/api/latest?access_key=demo&base=USD&symbols=XAU")
    usd_to_ounce = r1.json()["rates"]["XAU"]

    # نرخ دلار آزاد ایران (API رایگان)
    r2 = requests.get("https://api.exchangerate.host/latest?base=USD&symbols=IRR")
    usd_to_irr = r2.json()["rates"]["IRR"]

    # قیمت طلا ۱۸ عیار (ریال) = اونس * نرخ دلار * 0.75
    gold_18 = usd_to_ounce * usd_to_irr * 0.75

    # قیمت انس طلا (USD)
    ounce_price = usd_to_ounce

    return round(gold_18), round(ounce_price)

while True:
    try:
        gold_18, ounce_price = get_gold_price()
        msg = f"📊 قیمت طلا ۱۸ عیار: {gold_18:,} ریال\n💰 انس طلا: {ounce_price} USD"
        send_message(msg)
        print("ارسال شد ✅")
    except Exception as e:
        print("خطا:", e)

    time.sleep(60)  # هر دقیقه
