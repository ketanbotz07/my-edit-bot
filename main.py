import os
import subprocess
from telebot import TeleBot, types
from fastapi import FastAPI, Request
import uvicorn

# ---------------------
# BOT SETUP
# ---------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = TeleBot(BOT_TOKEN)
app = FastAPI()


# ---------------------
# VIDEO EDIT FUNCTION
# ---------------------
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


# ---------------------
# MESSAGE HANDLER
# ---------------------
@bot.message_handler(content_types=['video'])
def video_handler(message):
    bot.reply_to(message, "⏳ Editing your video... please wait...")

    file_info = bot.get_file(message.video.file_id)
    downloaded = bot.download_file(file_info.file_path)

    input_path = "input.mp4"
    output_path = "edited.mp4"

    with open(input_path, "wb") as f:
        f.write(downloaded)

    edit_video(input_path, output_path)

    bot.send_video(message.chat.id, video=open(output_path, "rb"))
    bot.reply_to(message, "✅ Done! Video edited.")


# ---------------------
# WEBHOOK ROUTES
# ---------------------
@app.post("/")
async def telegram_webhook(req: Request):
    data = await req.json()
    bot.process_new_updates([types.Update.de_json(data)])
    return {"ok": True}


@app.get("/")
def home():
    return {"status": "running", "bot": "ok"}


# ---------------------
# STARTUP EVENT
# ---------------------
@app.on_event("startup")
async def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    print("Webhook set successfully!")


# ---------------------
# MAIN
# ---------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
