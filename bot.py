import requests
import time

BOT_TOKEN = "2002214368:AAG20ASn5uukBFAYFWNxH0uvOOBOyxplMGc"
CHANNEL = "@price_offhuhfcc"

API_URL = "https://BrsApi.ir/Api/Market/Gold_Currency.php?key=BPYUM5gxjVNMHPLPVxDiVKkUfBZM9BeF"

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHANNEL, "text": text})

def get_gold18_price():
    r = requests.get(API_URL, timeout=10).json()
    # گرفتن قیمت خرید طلا 18 عیار
    try:
        gold18_buy = int(r['Gold']['G18']['Price'])
    except:
        gold18_buy = 0

    gold18_sell = gold18_buy - 90000  # فروش = خرید - 90 هزار تومان
    return gold18_buy, gold18_sell

while True:
    try:
        buy, sell = get_gold18_price()
        msg = f"خرید : {buy:,} ریال\nفروش : {sell:,} ریال\n\nهاید طلا"
        send_message(msg)
        print("ارسال شد ✅")
    except Exception as e:
        print("خطا:", e)

    time.sleep(60)  # هر دقیقه
