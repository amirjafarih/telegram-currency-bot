#!/usr/bin/env python3
import os
import sqlite3
import threading
import csv
from datetime import datetime, timedelta
from io import StringIO

from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

DB_PATH = os.getenv("EXPENSES_DB", "expenses.db")
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise RuntimeError("1878195114:AAHnxProYtRmDNkNn8Kfhm1H6QNziaa4Sr8")

# SQLite connection (shared, with a lock for thread-safety)
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
lock = threading.Lock()

def init_db():
    with lock:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT,
            note TEXT,
            ts INTEGER NOT NULL
        )
        """)
        conn.commit()

def add_expense(user_id: int, amount: float, category: str, note: str):
    ts = int(datetime.utcnow().timestamp())
    with lock:
        cur = conn.cursor()
        cur.execute("INSERT INTO expenses (user_id, amount, category, note, ts) VALUES (?, ?, ?, ?, ?)",
                    (user_id, amount, category, note, ts))
        conn.commit()

def get_expenses_since(user_id: int, since_dt: datetime):
    since_ts = int(since_dt.timestamp())
    with lock:
        cur = conn.cursor()
        cur.execute("SELECT id, amount, category, note, ts FROM expenses WHERE user_id = ? AND ts >= ? ORDER BY ts DESC",
                    (user_id, since_ts))
        rows = cur.fetchall()
    return rows

def delete_older_than(days: int = 30):
    cutoff = int((datetime.utcnow() - timedelta(days=days)).timestamp())
    with lock:
        cur = conn.cursor()
        cur.execute("DELETE FROM expenses WHERE ts < ?", (cutoff,))
        deleted = cur.rowcount
        conn.commit()
    return deleted

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! من ربات مدیریت مخارج‌ات هستم.\n"
        "دستورها:\n"
        "/add <مبلغ> <دسته> [یادداشت] — ثبت خرج\n"
        "مثال: /add 12500 ناهار ساندویچ\n"
        "/list — فهرست خرج‌های ۳۰ روز گذشته\n"
        "/total — جمع کل ۳۰ روز گذشته\n"
        "/export — دریافت CSV برای ۳۰ روز گذشته\n"
    )

async def add_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text or ""
    parts = text.split(maxsplit=3)  # ['/add', amount, category, note...]
    if len(parts) < 3:
        await update.message.reply_text("فرمت درست: /add <مبلغ> <دسته> [یادداشت]\nمثال: /add 45000 خرید نان")
        return
    try:
        amount = float(parts[1])
    except ValueError:
        await update.message.reply_text("مبلغ نامعتبر است. فقط عدد وارد کن.")
        return
    category = parts[2]
    note = parts[3] if len(parts) >= 4 else ""
    add_expense(user_id, amount, category, note)
    await update.message.reply_text(f"ثبت شد: {amount} تومان — {category} {('('+note+')') if note else ''}")

async def list_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    since = datetime.utcnow() - timedelta(days=30)
    rows = get_expenses_since(user_id, since)
    if not rows:
        await update.message.reply_text("هیچ خرجی در ۳۰ روز گذشته ثبت نشده.")
        return
    lines = []
    total = 0.0
    for r in rows:
        _id, amount, category, note, ts = r
        dt = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
        lines.append(f"{dt} — {amount} تومان — {category} {('('+note+')') if note else ''}")
        total += amount
    msg = "خرج‌های ۳۰ روز گذشته:\n" + "\n".join(lines) + f"\n\nجمع: {total} تومان"
    # Telegram has message length limits; split if needed
    for chunk in [msg[i:i+4000] for i in range(0, len(msg), 4000)]:
        await update.message.reply_text(chunk)

async def total_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    since = datetime.utcnow() - timedelta(days=30)
    rows = get_expenses_since(user_id, since)
    total = sum(r[1] for r in rows)
    await update.message.reply_text(f"جمع مخارج ۳۰ روز گذشته: {total} تومان")

async def export_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    since = datetime.utcnow() - timedelta(days=30)
    rows = get_expenses_since(user_id, since)
    if not rows:
        await update.message.reply_text("هیچ داده‌ای برای خروجی وجود ندارد.")
        return
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "amount", "category", "note", "utc_timestamp", "datetime_utc"])
    for r in rows:
        _id, amount, category, note, ts = r
        dt = datetime.utcfromtimestamp(ts).isoformat()
        writer.writerow([_id, amount, category, note, ts, dt])
    output.seek(0)
    await update.message.reply_document(document=InputFile(output, filename="expenses_30days.csv"))

async def cleanup_and_report(context: ContextTypes.DEFAULT_TYPE):
    deleted = delete_older_than(30)
    # optionally log to console
    print(f"[{datetime.utcnow().isoformat()}] پاکسازی روزانه انجام شد. سطرهای حذف‌شده: {deleted}")

def main():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_cmd))
    app.add_handler(CommandHandler("list", list_cmd))
    app.add_handler(CommandHandler("total", total_cmd))
    app.add_handler(CommandHandler("export", export_cmd))

    # هر بار بوت، یکبار پاکسازی کن
    delete_older_than(30)

    # زمان‌بندی پاکسازی روزانه: از JobQueue داخلی python-telegram-bot استفاده می‌کنیم
    job_queue = app.job_queue
    # اجرا هر 24 ساعت
    job_queue.run_repeating(cleanup_and_report, interval=24*3600, first=60)  # اولین اجرا پس از 60 ثانیه

    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()