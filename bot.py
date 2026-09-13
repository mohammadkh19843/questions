from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from config import BOT_TOKEN, WEBAPP_URL

bot = TeleBot(BOT_TOKEN)


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


if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling(skip_pending=True)
