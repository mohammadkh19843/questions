import json

from telebot import TeleBot
from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)

from config import BOT_TOKEN, WEBAPP_URL
from database import init_db, get_connection


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


def send_poll(
    chat_id,
    question,
    options,
    poll_type="quiz",
    correct_option_id=None,
    explanation="",
):
    """
    ارسال Poll یا Quiz واقعی به تلگرام.
    """

    if poll_type == "quiz":
        return bot.send_poll(
            chat_id=chat_id,
            question=question,
            options=options,
            type="quiz",
            correct_option_id=correct_option_id,
            is_anonymous=False,
            explanation=explanation or None,
        )

    return bot.send_poll(
        chat_id=chat_id,
        question=question,
        options=options,
        type="regular",
        is_anonymous=False,
        allows_multiple_answers=False,
    )


def publish_question(question_id, chat_id):
    """
    خواندن سؤال از دیتابیس و انتشار آن در تلگرام.
    """

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT *
            FROM questions
            WHERE id = ?
            """,
            (question_id,),
        ).fetchone()

    if row is None:
        raise ValueError("Question not found")

    options = json.loads(row["options_json"])

    if row["poll_type"] == "quiz" and row["correct_option_id"] is None:
        raise ValueError("Quiz does not have a correct option")

    result = send_poll(
        chat_id=chat_id,
        question=row["question"],
        options=options,
        poll_type=row["poll_type"],
        correct_option_id=row["correct_option_id"],
        explanation=row["analysis"],
    )

    return result


if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling(skip_pending=True)
