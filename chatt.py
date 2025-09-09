# -*- coding: utf-8 -*-
import telebot
from flask import Flask, request

TOKEN = '7850920014:AAHqKq_qpALnsJQQqQYulsOMack3wA4K2G8'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)  # ✅ to‘g‘rilandi

waiting_users = []
paired_users = {}
users = set()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    users.add(user_id)

    if user_id in paired_users or user_id in waiting_users:
        bot.send_message(user_id, "ℹ️ Kamu sudah dalam antrean atau sedang mengobrol.")
        return

    if waiting_users:
        partner_id = waiting_users.pop(0)
        paired_users[user_id] = partner_id
        paired_users[partner_id] = user_id
        bot.send_message(user_id, "✅ Kamu telah terhubung! Kirim pesanmu.")
        bot.send_message(partner_id, "✅ Kamu telah terhubung! Kirim pesanmu.")
    else:
        waiting_users.append(user_id)
        bot.send_message(user_id, "⏳ Menunggu pasangan untuk terhubung...")

    bot.send_message(user_id, "ℹ️ Gunakan perintah: /stop, /next, /help, /stats")

@bot.message_handler(commands=['stop'])
def stop_chat(message):
    user_id = message.chat.id
    users.add(user_id)

    if user_id in paired_users:
        partner_id = paired_users.pop(user_id)
        paired_users.pop(partner_id, None)
        bot.send_message(user_id, "❌ Kamu telah meninggalkan obrolan.")
        bot.send_message(partner_id, "❌ Pasanganmu telah meninggalkan obrolan.")
    elif user_id in waiting_users:
        waiting_users.remove(user_id)
        bot.send_message(user_id, "🚪 Kamu telah keluar dari antrean.")
    else:
        bot.send_message(user_id, "⚠️ Kamu tidak dalam obrolan.")

@bot.message_handler(commands=['next'])
def next_chat(message):
    user_id = message.chat.id
    users.add(user_id)

    if user_id in paired_users:
        partner_id = paired_users.pop(user_id)
        paired_users.pop(partner_id, None)
        bot.send_message(partner_id, "🔁 Pasanganmu telah meninggalkan obrolan.")

    if user_id in waiting_users:
        waiting_users.remove(user_id)

    if waiting_users:
        partner_id = waiting_users.pop(0)
        paired_users[user_id] = partner_id
        paired_users[partner_id] = user_id
        bot.send_message(user_id, "🔗 Kamu telah terhubung dengan pasangan baru!")
        bot.send_message(partner_id, "🔗 Kamu telah terhubung dengan pasangan baru!")
    else:
        waiting_users.append(user_id)
        bot.send_message(user_id, "⏳ Menunggu pasangan baru untuk terhubung...")

@bot.message_handler(commands=['help'])
def help_command(message):
    users.add(message.chat.id)
    help_text = (
        "📘 *Panduan Bot Anonim:*\n\n"
        "/start - Mulai obrolan anonim\n"
        "/stop - Hentikan obrolan saat ini\n"
        "/next - Cari pasangan baru\n"
        "/help - Lihat panduan ini lagi\n"
        "/stats - Lihat jumlah pengguna bot\n\n"
        "🚫 Jangan kirim informasi pribadi!"
    )
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['stats'])
def stats(message):
    user_id = message.chat.id
    users.add(user_id)
    total_users = len(users)
    bot.send_message(user_id, f"👥 Jumlah total pengguna bot: {total_users}")

@bot.message_handler(func=lambda message: True)
def forward_messages(message):
    user_id = message.chat.id
    users.add(user_id)
    if user_id in paired_users:
        partner_id = paired_users[user_id]
        bot.send_message(partner_id, message.text)

@app.route(f"/{TOKEN}", methods=['POST'])
def receive_update():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@app.route('/')
def index():
    return "Bot ishlayapti!", 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    bot.remove_webhook()
    bot.set_webhook(url=f"https://chatt-bot-mhh6.onrender.com/{TOKEN}")
    app.run(host="0.0.0.0", port=port)




