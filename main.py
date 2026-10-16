import os
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from flask import Flask
from threading import Thread

# ১. Render.com এবং cron-job.org এর জন্য ওয়েব সার্ভার
app = Flask(__name__)

@app.route('/')
def home():
    return "PDF Telegram Bot is Awake and Running 24/7!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_server)
    t.daemon = True
    t.start()

# ২. ভিডিওর নিয়ম অনুযায়ী Environment Variable থেকে BOT_TOKEN নেওয়া হবে
# (যদি রেন্ডারে না পায়, তবে নিচের ফেক টোকেনটি ডিফল্ট হিসেবে থাকবে)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8618362074:AAEmwrYZPw_op74VXY_Fx_8TB6MFS_onQlU")

# আপনার গুগল ড্রাইভের পিডিএফ লিংক
PDF_LINK = "https://drive.google.com/file/d/1gZMl13utfnNko9RkIbuyZQBKo_lPBoy4/view?usp=drivesdk"

bot = telebot.TeleBot(BOT_TOKEN)

# ইউজার এবং ফর্ম/পিডিএফ সংখ্যা ট্র্যাক করার ফাইল
USERS_FILE = "users.txt"
COUNT_FILE = "count.txt"

def track_user(user_id):
    users = set()
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            users = set(f.read().splitlines())
    users.add(str(user_id))
    with open(USERS_FILE, "w") as f:
        f.write("\n".join(users))
    return len(users)

def increment_pdf_count():
    count = 0
    if os.path.exists(COUNT_FILE):
        with open(COUNT_FILE, "r") as f:
            try:
                count = int(f.read().strip())
            except ValueError:
                count = 0
    count += 1
    with open(COUNT_FILE, "w") as f:
        f.write(str(count))
    return count

def get_stats():
    total_users = len(open(USERS_FILE).read().splitlines()) if os.path.exists(USERS_FILE) else 0
    total_clicks = int(open(COUNT_FILE).read().strip()) if os.path.exists(COUNT_FILE) else 0
    return total_users, total_clicks

# /start কমান্ড হ্যান্ডলার
@bot.message_handler(commands=['start'])
def send_welcome(message):
    total_users = track_user(message.from_user.id)
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("/pdf"), KeyboardButton("পিডিএফ ঠিক আছে"))
    markup.add(KeyboardButton("/stats"), KeyboardButton("/help"))
    
    welcome_text = (
        f"স্বাগতম {message.from_user.first_name}! 🤖\n"
        f"👥 আপনি আমাদের {total_users} নম্বর ইউজার।\n\n"
        "নিচের কমান্ডগুলো ব্যবহার করুন:\n"
        "📄 /pdf - পিডিএফ ফাইলটির লিংক পেতে\n"
        "📊 /stats - মোট ইউজার ও পিডিএফ নেওয়ার সংখ্যা দেখতে\n"
        "ℹ️ /help - সাহায্যের জন্য"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

# /stats কমান্ড হ্যান্ডলার (মোট ইউজার ও ক্লিক সংখ্যা)
@bot.message_handler(commands=['stats'])
def send_stats(message):
    total_users, total_clicks = get_stats()
    stats_text = (
        "📊 **বটের স্ট্যাটাস রিপোর্ট:**\n\n"
        f"👤 মোট ইউনিক ইউজার: {total_users} জন\n"
        f"📥 মোট পিডিএফ/ফর্ম নেওয়া হয়েছে: {total_clicks} বার"
    )
    bot.send_message(message.chat.id, stats_text, parse_mode="Markdown")

# /help কমান্ড হ্যান্ডলার
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, "পিডিএফ ফাইলটি পেতে মেসেজে /pdf লিখুন অথবা নিচের বাটনে ক্লিক করুন।")

# পিডিএফ ও অন্যান্য মেসেজ হ্যান্ডলার
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.strip()
    track_user(message.from_user.id)

    if text in ["/pdf", "pdf", "PDF", "পিডিএফ", "পিডিএফ ঠিক আছে"]:
        total_clicks = increment_pdf_count()
        reply = (
            "পিডিএফ ঠিক আছে। নিচে আপনার পিডিএফের লিংক দেওয়া হলো:\n\n"
            f"🔗 {PDF_LINK}\n\n"
            f"✅ (এখন পর্যন্ত মোট {total_clicks} বার এই পিডিএফটি নেওয়া হয়েছে)"
        )
        bot.send_message(message.chat.id, reply)
    else:
        bot.send_message(message.chat.id, "সঠিক কমান্ড পেতে /start অথবা /pdf লিখুন।")

# মেইন প্রোগ্রাম রান করা
if __name__ == "__main__":
    keep_alive()  # ওয়েব সার্ভার চালু করবে
    print("Bot is running...")
    bot.infinity_polling()  # টেলিগ্রাম বট পোলিং চালু রাখবে
