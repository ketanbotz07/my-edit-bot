import os
import subprocess
import threading
from telebot import TeleBot
from fastapi import FastAPI
import uvicorn

# Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = TeleBot(BOT_TOKEN)


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


@bot.message_handler(content_types=['video'])
def video_handler(message):
    bot.reply_to(message, "⏳ Editing your video... Please wait...")

    file_info = bot.get_file(message.video.file_id)
    downloaded = bot.download_file(file_info.file_path)

    input_path = "input.mp4"
    output_path = "edited.mp4"

    with open(input_path, "wb") as f:
        f.write(downloaded)

    edit_video(input_path, output_path)

    bot.send_video(message.chat.id, video=open(output_path, "rb"))
    bot.reply_to(message, "✅ Done! Your edited video is ready!")


# ---------------------
# FASTAPI WEB SERVER
# ---------------------
app = FastAPI()

@app.get("/")
def home():
    return {"status": "ok", "message": "Bot Running"}


def run_bot():
    print("Bot started successfully!")
    bot.infinity_polling(skip_pending=True)


def run_web():
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(
        "main:app",       # IMPORTANT
        host="0.0.0.0",
        port=port,
        reload=False,     # MUST be disabled
        workers=1         # MUST be 1
    )


if name == "main":
    threading.Thread(target=run_bot, daemon=True).start()
    run_web()
