import os
import subprocess
from flask import Flask, request
import telebot

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)


def edit_video(input_path, output_path):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-vf", "crop=in_w:in_h-80:0:40,scale=1280:-1",
        "-af", "atempo=1.03",
        "-preset", "veryfast",
        output_path
    ]
    subprocess.run(cmd)


@bot.message_handler(content_types=["video"])
def handle_video(message):
    bot.reply_to(message, "⏳ Editing your video...")

    file_info = bot.get_file(message.video.file_id)
    data = bot.download_file(file_info.file_path)

    with open("input.mp4", "wb") as f:
        f.write(data)

    edit_video("input.mp4", "edited.mp4")

    bot.send_video(message.chat.id, open("edited.mp4", "rb"))
    bot.reply_to(message, "✅ Done!")


@app.route("/", methods=["GET"])
def home():
    return "Bot is running OK!"


@app.route("/webhook", methods=["POST"])
def webhook():
    json_data = request.get_data().decode()
    update = telebot.types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return "OK", 200


# Run webhook instantly (Flask 3 compatible)
with app.app_context():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    print("Webhook set:", WEBHOOK_URL)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
