import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set in Replit Secrets")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! Send me a Twitter/X link with a video."
    )

def download_video_sync(url):
    ydl_opts = {
        'format': 'best[ext=mp4]',
        'outtmpl': '%(id)s.%(ext)s',
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info), info.get("title", "Video")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "twitter.com" not in text and "x.com" not in text:
        return

    msg = await update.message.reply_text("Downloading...")
    try:
        url = next(w for w in text.split() if "twitter.com" in w or "x.com" in w)
        filename, title = await asyncio.to_thread(download_video_sync, url)

        with open(filename, "rb") as f:
            await update.message.reply_video(f, caption=title)

        os.remove(filename)
        await msg.edit_text("Done ✅")
    except Exception as e:
        logging.exception(e)
        await msg.edit_text("Failed ❌")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
