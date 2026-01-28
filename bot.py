import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import yt_dlp

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello! I'm a Twitter Video Saver bot. Send me a link to a tweet with a video, and I'll download it for you."
    )

def download_video_sync(url):
    """Synchronous function to download video using yt-dlp."""
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': '%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename, info.get('title', 'Video')
        except Exception as e:
            logging.error(f"Error downloading video: {e}")
            return None, None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    if 'twitter.com' in message_text or 'x.com' in message_text:
        status_message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Found a Twitter link! Processing..."
        )
        
        try:
            # Simple extraction: find the first "word" that contains twitter.com or x.com
            url = next(token for token in message_text.split() if 'twitter.com' in token or 'x.com' in token)
        except StopIteration:
             await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=status_message.message_id,
                text="Couldn't find a valid link in your message."
            )
             return

        # Run blocking download in a separate thread
        filename, title = await asyncio.to_thread(download_video_sync, url)

        if filename and os.path.exists(filename):
            try:
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=status_message.message_id,
                    text="Uploading video..."
                )
                
                with open(filename, 'rb') as video_file:
                    await context.bot.send_video(
                        chat_id=update.effective_chat.id,
                        video=video_file,
                        caption=f"Here is your video: {title}"
                    )
                
                # Cleanup
                os.remove(filename)
                
                # Update status message to done (or delete it)
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=status_message.message_id,
                    text="Done!"
                )
            except Exception as e:
                logging.error(f"Error sending video: {e}")
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=status_message.message_id,
                    text="An error occurred while uploading the video."
                )
                if os.path.exists(filename):
                    os.remove(filename)
        else:
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=status_message.message_id,
                text="Failed to download video. It might be restricted or not found."
            )
    else:
        # Optional: Reply to non-link messages or just ignore
        pass

if __name__ == '__main__':
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token or bot_token == 'your_token_here':
        print("Error: TELEGRAM_BOT_TOKEN not set in .env file.")
    else:
        application = ApplicationBuilder().token(bot_token).build()
        
        start_handler = CommandHandler('start', start)
        message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
        
        # Start a dummy web server for health checks
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import threading

        class HealthCheckHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")

        def run_health_check_server():
            port = int(os.environ.get('PORT', 8000))
            server_address = ('0.0.0.0', port)
            httpd = HTTPServer(server_address, HealthCheckHandler)
            print(f"Health check server running on port {port}")
            httpd.serve_forever()

        threading.Thread(target=run_health_check_server, daemon=True).start()

        application.add_handler(start_handler)
        application.add_handler(message_handler)
        
        print("Bot is running...")
        # Error handler to log errors but keep bot alive if possible
        async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
            logging.error(f"Exception while handling an update: {context.error}")
            if isinstance(context.error, Conflict):
                logging.warning("Conflict error detected in error handler. Sleeping for 10s...")
                await asyncio.sleep(10)

        application.add_error_handler(error_handler)

        print("Bot is running...")
        
        # Retry loop for conflict handling (still needed if run_polling exits)
        import time
        from telegram.error import Conflict

        while True:
            try:
                # allowed_updates=None is default (all types)
                application.run_polling(allowed_updates=Update.ALL_TYPES, close_loop=False)
                print("Polling stopped cleanly.")
                break 
            except Conflict:
                print("Caught Conflict in main loop. Restarting polling in 10s...")
                time.sleep(10)
            except Exception as e:
                print(f"Caught unexpected error in main loop: {e}")
                time.sleep(5)
                # If it keeps crashing, we want to retry, not exit
                continue
