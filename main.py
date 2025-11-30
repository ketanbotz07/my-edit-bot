from flask import Flask, request
import telebot

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
WEBHOOK_URL = "https://YOUR-KOYEB-APP-URL.koyeb.app/webhook"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# -----------------------------
# Telegram Webhook Receiver
# -----------------------------
@app.route('/webhook', methods=['POST'])
def webhook():
    json_update = request.get_json()
    if json_update:
        bot.process_new_updates([telebot.types.Update.de_json(json_update)])
    return "OK", 200


# -----------------------------
# Commands / Handlers
# -----------------------------
@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "Bot Webhook Mode me chal raha hai sir! 👌🔥")


@bot.message_handler(func=lambda m: True)
def echo(msg):
    bot.reply_to(msg, f"Received: {msg.text}")


# -----------------------------
# Flask Root Test Route
# -----------------------------
@app.route('/')
def home():
    return "Telegram Webhook Bot Running Successfully!"


# -----------------------------
# Set Webhook on Startup
# -----------------------------
if __name__ == "__main__":
    # Pehle purana webhook remove करो
    bot.remove_webhook()

    # Naya webhook set karo
    bot.set_webhook(url=WEBHOOK_URL)

    print("Webhook set successfully:", WEBHOOK_URL)

    # Flask App Run
    app.run(host="0.0.0.0", port=8000)
