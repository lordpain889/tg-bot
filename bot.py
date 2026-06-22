import asyncio
import logging
import os

from dotenv import load_dotenv
from openai import APIConnectionError, APIError, OpenAI, RateLimitError
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise ValueError("TELEGRAM_TOKEN and OPENAI_API_KEY must be set in the .env file")

client = OpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = "You are a helpful assistant."
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))
OPENAI_RETRY_ATTEMPTS = int(os.getenv("OPENAI_RETRY_ATTEMPTS", "3"))


def get_history(context: ContextTypes.DEFAULT_TYPE) -> list[dict[str, str]]:
    if "history" not in context.user_data:
        context.user_data["history"] = []
    return context.user_data["history"]


def trim_history(history: list[dict[str, str]]) -> None:
    if MAX_HISTORY_MESSAGES > 0 and len(history) > MAX_HISTORY_MESSAGES:
        del history[:-MAX_HISTORY_MESSAGES]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome = (
        "Welcome! I'm a chatbot powered by OpenAI GPT.\n\n"
        "Send me a message and I'll respond.\n"
        "Use /clear to reset our conversation history."
    )
    await update.message.reply_text(welcome)


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["history"] = []
    await update.message.reply_text("Conversation history cleared.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.text is None:
        return
    user_message = update.message.text
    history = get_history(context)

    history.append({"role": "user", "content": user_message})
    trim_history(history)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, *history]

    try:
        response = None
        for attempt in range(1, max(1, OPENAI_RETRY_ATTEMPTS) + 1):
            try:
                response = client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=messages,
                )
                break
            except (RateLimitError, APIConnectionError, APIError) as exc:
                if attempt >= max(1, OPENAI_RETRY_ATTEMPTS):
                    raise
                wait_seconds = 0.8 * attempt
                logger.warning("OpenAI temporary error (%s). Retrying in %.1fs...", exc.__class__.__name__, wait_seconds)
                await asyncio.sleep(wait_seconds)

        if response is None:
            raise RuntimeError("OpenAI response is unavailable after retries.")
        assistant_message = response.choices[0].message.content or "I don't have a response right now."
        history.append({"role": "assistant", "content": assistant_message})
        trim_history(history)
        await update.message.reply_text(assistant_message)
    except Exception:
        logger.exception("OpenAI API error")
        if history:
            history.pop()
        await update.message.reply_text("Sorry, I encountered an error. Please try again.")


def main() -> None:
    application = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("clear", clear))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot started")
    application.run_polling()


if __name__ == "__main__":
    main()
