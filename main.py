import os
import subprocess
from telebot import TeleBot, types
from fastapi import FastAPI, Request
import uvicorn

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # <-- ADD THIS

bot = TeleBot(BOT_TOKEN)
app = FastAPI()

def edit_video(input_path, output_path):
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", "crop=in_w:in_h-80:0:40,scale=1280:-1",
        "-af", "atempo=1.03",
        "-preset", "veryfast",
        output_path
    ]
    subprocess.run(cmd)

@bot.message_handler(content_types=['video'])
def video_handler(message):
    bot.send_message(message.chat.id, "⏳ Editing your video...")

    file_info = bot.get_file(message.video.file_id)
    downloaded = bot.download_file(file_info.file_path)

    input_path = "input.mp4"
    output_path = "edited.mp4"

    with open(input_path, "wb") as f:
        f.write(downloaded)

    edit_video(input_path, output_path)

    bot.send_video(message.chat.id, video=open(output_path, "rb"))
    bot.send_message(message.chat.id, "✅ Done!")

# ROOT PAGE
@app.get("/")
def home():
    return {"status": "ok", "message": "Bot Running"}

# TELEGRAM WEBHOOK HANDLER
@app.post(f"/{BOT_TOKEN}")
async def webhook(request: Request):
    json_data = await request.json()
    update = types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return {"ok": True}

if __name__ == "__main__":
    # Set webhook
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + BOT_TOKEN)

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
