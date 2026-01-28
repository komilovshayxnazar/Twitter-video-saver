# Twitter (X) Video Saver Telegram Bot

A simple Telegram bot that downloads videos from Twitter (now X) tweets and sends them back to the user as a video file.

## Features
- Detects Twitter/X links in messages.
- Downloads the highest quality video using `yt-dlp`.
- Uploads the video directly to the chat.
- cleans up downloaded files automatically.

## Prerequisites
- Python 3.8 or higher
- A Telegram Bot Token (get one from [@BotFather](https://t.me/BotFather))
- `ffmpeg` (recommended for video processing)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/twitter-saver-bot.git
    cd twitter-saver-bot
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration:**
    Create a `.env` file in the root directory and add your bot token:
    ```env
    TELEGRAM_BOT_TOKEN=your_token_here
    ```

## Usage

1.  **Run the bot:**
    ```bash
    python3 bot.py
    ```

2.  **Interact:**
    - Open the bot in Telegram.
    - Send `/start`.
    - Paste a link to a tweet containing a video.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
