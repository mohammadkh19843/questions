import json

from telebot import TeleBot
from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)

from config import BOT_TOKEN, WEBAPP_URL
from database import init_db


bot = TeleBot(BOT_TOKEN)

init_db()


@bot.message_handler(commands=["start"])
def start(message):
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(
            "🗳️ ساخت سؤال",
            web_app=WebAppInfo(url=WEBAPP_URL),
        )
    )

    bot.send_message(
        message.chat.id,
        "🗳️ Questions\n\n"
        "از اینجا می‌توانی سؤال، گزینه‌ها و Quiz خودت را بسازی.",
        reply_markup=keyboard,
    )


@bot.message_handler(commands=["id"])
def get_chat_id(message):
    bot.send_message(
        message.chat.id,
        f"Chat ID:\n`{message.chat.id}`",
        parse_mode="Markdown",
    )


if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling(skip_pending=True)
