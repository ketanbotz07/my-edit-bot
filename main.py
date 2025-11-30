import os
import subprocess
from fastapi import FastAPI, Request
from telebot import TeleBot, types
import asyncio


# ----------------------
# BOT SETUP
# ----------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = TeleBot(BOT_TOKEN, threaded=False)


# FFmpeg function


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




# Handler
@bot.message_handler(content_types=['video'])
def handle_video(message):
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




# ----------------------
# FASTAPI SERVER + WEBHOOK
# ----------------------
app = FastAPI()


@app.get("/")
def home():
return {"status": "running", "message": "Telegram Bot Active"}


@app.post(f"/{BOT_TOKEN}")
async def telegram_webhook(request: Request):
json_data = await request.json()
update = types.Update.de_json(json_data)
bot.process_new_updates([update])
return {"ok": True}




# ----------------------
# SET WEBHOOK ON STARTUP
# ----------------------
@app.on_event("startup")
def set_webhook():
print("Webhook set successfully! =>", url)
