import os
import telebot
from flask import Flask, request, jsonify
import subprocess

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = telebot.TeleBot(BOT_TOKEN, threaded=True)
app = Flask(__name__)

# ---------------------- VIDEO EDIT FUNCTION ----------------------
def edit_video(input_path, output_path):
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vf", "crop=in_w:in_h-80:0:40,scale=1280:-1",
        "-af", "atempo=1.03",
        "-preset", "veryfast",
        output_path
    ]
    subprocess.run(cmd)

# ---------------------- TELEGRAM HANDLER -------------------------
@bot.message_handler(content_types=["video"])
def handle_video(message):
    bot.reply_to(message, "⏳ Editing… Please wait")
    file_info = bot.get_file(message.video.file_id)
    data = bot.download_file(file_info.file_path)

    with open("input.mp4", "wb") as f:
        f.write(data)

    edit_video("input.mp4", "edited.mp4")
    bot.send_video(message.chat.id, open("edited.mp4", "rb"))
    bot.reply_to(message, "✅ Done!")

# ---------------------- FLASK WEBHOOK ----------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_update = request.get_json()
        update = telebot.types.Update.de_json(json_update)
        bot.process_new_updates([update])
        return jsonify({"status": "ok"}), 200
    else:
        return "Unsupported", 403

@app.route("/", methods=["GET"])
def home():
    return "Bot Running", 200

# ---------------------- SET WEBHOOK ON STARTUP -------------------
with app.app_context():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)

# ---------------------- START APP --------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
