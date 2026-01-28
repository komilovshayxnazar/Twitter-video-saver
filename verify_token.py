import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

async def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    print(f"Testing with token: {token[:10]}...")
    bot = Bot(token=token)
    try:
        me = await bot.get_me()
        print(f"Success! Bot username: @{me.username}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
