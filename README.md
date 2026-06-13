# Telegram GPT Bot

A Telegram bot that responds to messages using the OpenAI GPT API. Conversation history is kept per user for the duration of the bot session.

## Features

- Replies to text messages via OpenAI GPT
- Maintains conversation history per user session
- `/start` — welcome message
- `/clear` — reset conversation history

## Prerequisites

- Python 3.10 or newer
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- An OpenAI API key from [OpenAI](https://platform.openai.com/)

## Setup

1. **Clone or download this project**, then open a terminal in the project folder.

2. **Create a virtual environment** (recommended):

   ```bash
   python -m venv venv
   ```

   Activate it:

   - Windows (PowerShell): `.\venv\Scripts\Activate.ps1`
   - Windows (cmd): `venv\Scripts\activate.bat`
   - macOS/Linux: `source venv/bin/activate`

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:

   Copy the example file and fill in your keys:

   ```bash
   copy .env.example .env
   ```

   Edit `.env`:

   ```
   TELEGRAM_TOKEN=your_telegram_bot_token_here
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4o-mini
   ```

   `OPENAI_MODEL` is optional; it defaults to `gpt-4o-mini`.

5. **Run the bot**:

   ```bash
   python bot.py
   ```

6. Open Telegram, find your bot, send `/start`, and begin chatting.

## Commands

| Command  | Description                          |
|----------|--------------------------------------|
| `/start` | Show the welcome message             |
| `/clear` | Clear your conversation history      |

## Notes

- Conversation history is stored in memory and is lost when the bot restarts.
- Keep your `.env` file private and never commit it to version control.
