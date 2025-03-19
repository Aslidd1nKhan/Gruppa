import telebot
import json
import os

TOKEN = "7400009988:AAH8g6s0jvgflZueAzZw4YyvhcN1i44wej8"
DATA_FILE = "data.txt"
ADMINS_FILE = "admins.txt"

bot = telebot.TeleBot(TOKEN)

# **Ma'lumotlarni yuklash va saqlash funksiyalari**
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_admins():
    if not os.path.exists(ADMINS_FILE):
        return []
    with open(ADMINS_FILE, "r") as f:
        return [line.strip() for line in f.readlines()]

# **/start - adminlarga tugma**
@bot.message_handler(commands=["start"])
def handle_start(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    admins = load_admins()

    if str(user_id) in admins:
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton("➕ Guruhga qo‘shish", url=f"https://t.me/YOUR_BOT_USERNAME?startgroup=true")
        markup.add(btn)
        bot.send_message(chat_id, "👋 Salom, Admin! Guruhga qo‘shish uchun tugmani bosing.", reply_markup=markup)
    else:
        bot.send_message(chat_id, "👋 Salom! Meni guruhga qo‘shing, men kim qancha odam qo‘shganini hisoblab boraman.")

# **/stat - statistikani chiqarish**
@bot.message_handler(commands=["stat"])
def handle_stat(message):
    chat_id = message.chat.id
    data = load_data()

    if not data:
        bot.send_message(chat_id, "📊 Hali hech kim foydalanuvchi qo‘shmagan.")
        return

    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    response = "📊 *Eng ko‘p foydalanuvchi qo‘shganlar:*\n\n"
    for name, count in sorted_data[:10]:
        response += f"👤 {name} — {count} ta\n"

    bot.send_message(chat_id, response, parse_mode="Markdown")

# **/plus Ism miqdor - odam qo‘shish**
@bot.message_handler(commands=["plus"])
def handle_plus(message):
    chat_id = message.chat.id
    user_id = str(message.from_user.id)
    admins = load_admins()

    if user_id not in admins:
        bot.send_message(chat_id, "❌ Sizga ruxsat berilmagan.")
        return

    parts = message.text.split()
    if len(parts) < 3:
        bot.send_message(chat_id, "❌ To‘g‘ri format: `/plus Ism miqdor`")
        return

    name = parts[1]
    try:
        count = int(parts[2])
        if count <= 0:
            raise ValueError
    except ValueError:
        bot.send_message(chat_id, "❌ Miqdor musbat son bo‘lishi kerak.")
        return

    data = load_data()
    data[name] = data.get(name, 0) + count
    save_data(data)

    bot.send_message(chat_id, f"✅ {name}'ga {count} odam qo‘shildi!")

# **/qoshdim - hisobni boshqasiga o'tkazish**
@bot.message_handler(commands=["qoshdim"])
def handle_qoshdim(message):
    chat_id = message.chat.id
    user_id = str(message.from_user.id)

    data = load_data()
    if user_id not in data:
        bot.send_message(chat_id, "❌ Siz hali hech kimni qo‘shmagansiz.")
        return

    current_count = data[user_id]
    bot.send_message(chat_id, f"📊 Sizning hozirgi hisobingiz: {current_count} ta odam.\n\nKimga qancha miqdorda o'tkazishni yozing:\n\nFormat: `Ism miqdor`", parse_mode="Markdown")

    bot.register_next_step_handler(message, process_transfer)

def process_transfer(message):
    chat_id = message.chat.id
    user_id = str(message.from_user.id)
    data = load_data()

    if user_id not in data:
        bot.send_message(chat_id, "❌ Siz hali hech kimni qo‘shmagansiz.")
        return

    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(chat_id, "❌ To‘g‘ri format: `Ism miqdor`")
        return

    to_name = parts[0]
    try:
        amount = int(parts[1])
        if amount <= 0 or amount > data[user_id]:
            raise ValueError
    except ValueError:
        bot.send_message(chat_id, "❌ Noto‘g‘ri miqdor.")
        return

    data[user_id] -= amount
    data[to_name] = data.get(to_name, 0) + amount
    save_data(data)

    bot.send_message(chat_id, f"✅ {amount} odam {to_name}'ga o'tkazildi!")

bot.polling(none_stop=True)
