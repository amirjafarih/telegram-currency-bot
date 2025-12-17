import requests
import time

BOT_TOKEN = "2002214368:AAG20ASn5uukBFAYFWNxH0uvOOBOyxplMGc"
CHANNEL = "@price_offhuhfcc"

API_URL = "https://BrsApi.ir/Api/Market/Gold_Currency.php?key=BPYUM5gxjVNMHPLPVxDiVKkUfBZM9BeF"

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHANNEL, "text": text})

def get_gold18_price():
    try:
        r = requests.get(API_URL, timeout=10).json()
        print("JSON دریافت شد:", r)  # لاگ JSON

        # گرفتن قیمت خرید طلا 18 عیار
        gold18_buy = int(r['Gold']['G18']['Price'])
        gold18_sell = gold18_buy - 90000  # فروش = خرید - 90 هزار تومان
        return gold18_buy, gold18_sell
    except Exception as e:
        print("خطا در دریافت قیمت:", e)
        return None, None

while True:
    buy, sell = get_gold18_price()
    if buy and sell:
        msg = f"خرید : {buy:,} ریال\nفروش : {sell:,} ریال\n\nهاید طلا"
        send_message(msg)
        print("ارسال شد ✅")
    else:
        print("قیمت دریافت نشد ❌")

    time.sleep(60)  # هر دقیقه
