import os
import subprocess
from flask import Flask, request
import telebot

# Read secrets from environment
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # set this in Koyeb
# Note: we will set webhook via Telegram API manually after deploy
# Keep webhook endpoint at "/" (root)

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable not set")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ---------- Handlers ----------
@bot.message_handler(commands=['start'])
def cmd_start(msg):
    bot.reply_to(msg, "Bot running (webhook). Send a video and I'll edit it.")

@bot.message_handler(content_types=['video'])
def handle_video(msg):
    bot.reply_to(msg, "⏳ Editing your video... please wait.")

    file_info = bot.get_file(msg.video.file_id)
    downloaded = bot.download_file(file_info.file_path)

    input_path = "input.mp4"
    output_path = "edited.mp4"

    with open(input_path, "wb") as f:
        f.write(downloaded)

    # simple ffmpeg edit — change as you like
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", "crop=in_w:in_h-80:0:40,scale=1280:-1",
        "-af", "atempo=1.03",
        "-preset", "veryfast",
        output_path
    ]
    # run and wait
    subprocess.run(cmd, check=False)

    # send result
    with open(output_path, "rb") as out_f:
        bot.send_video(msg.chat.id, out_f)

    # cleanup
    try:
        os.remove(input_path)
        os.remove(output_path)
    except Exception:
        pass

# ---------- Webhook endpoint ----------
@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json(force=True)
    update = telebot.types.Update.de_json(data)
    bot.process_new_updates([update])
    return "OK", 200

@app.route('/', methods=['GET'])
def index():
    return "Bot is running", 200

# Do NOT run polling here — webhook only
if __name__ == "__main__":
    # Local test only (not used in Koyeb)
    app.run(host="0.0.0.0", port=8000)
