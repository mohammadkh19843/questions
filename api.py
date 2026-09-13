import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from database import init_db, insert_question, get_connection
from bot import publish_question


app = FastAPI(title="Questions API")

CONTENT_DIR = Path("content")
CONTENT_DIR.mkdir(exist_ok=True)

init_db()


class TelegramUser(BaseModel):
    id: int | None = None
    first_name: str | None = None
    username: str | None = None


class QuestionCreate(BaseModel):
    question: str = Field(min_length=1, max_length=300)
    options: list[str] = Field(min_length=2, max_length=10)
    type: str = Field(pattern="^(regular|quiz)$")
    correct_option_id: int | None = None
    analysis: str = ""
    post_text: str = ""
    telegram_user: TelegramUser | None = None


def next_content_id() -> str:
    numbers = []

    for path in CONTENT_DIR.glob("CNT-*"):
        try:
            numbers.append(int(path.name.split("-")[1]))
        except (IndexError, ValueError):
            pass

    number = max(numbers, default=0) + 1

    return f"CNT-{number:06d}"


@app.get("/api/health")
def health():
    return {"ok": True}


@app.post("/api/questions")
def create_question(data: QuestionCreate):
    options = [x.strip() for x in data.options]

    if any(not x for x in options):
        raise HTTPException(
            status_code=400,
            detail="همه گزینه‌ها باید پر شوند.",
        )

    if len(set(options)) != len(options):
        raise HTTPException(
            status_code=400,
            detail="گزینه‌های تکراری مجاز نیستند.",
        )

    if data.type == "quiz":
        if data.correct_option_id is None:
            raise HTTPException(
                status_code=400,
                detail="برای Quiz باید پاسخ صحیح انتخاب شود.",
            )

        if not 0 <= data.correct_option_id < len(options):
            raise HTTPException(
                status_code=400,
                detail="شماره پاسخ صحیح نامعتبر است.",
            )
    else:
        data.correct_option_id = None

    content_id = next_content_id()

    folder = CONTENT_DIR / content_id
    media = folder / "media"

    media.mkdir(parents=True)

    question_json = {
        "id": content_id,
        "type": data.type,
        "question": data.question.strip(),
        "options": [
            {
                "id": i,
                "text": text,
                "correct": data.correct_option_id == i,
            }
            for i, text in enumerate(options)
        ],
        "analysis": data.analysis.strip(),
        "status": "DRAFT",
    }

    telegram_json = {
        "question": data.question.strip(),
        "options": options,
        "type": data.type,
        "is_anonymous": False,
        "allows_multiple_answers": False,
    }

    if data.type == "quiz":
        telegram_json["correct_option_id"] = data.correct_option_id

    (folder / "question.json").write_text(
        json.dumps(
            question_json,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    analysis = (
        data.analysis.strip()
        or "تحلیل هنوز تکمیل نشده است."
    )

    (folder / "analysis.md").write_text(
        f"# تحلیل {content_id}\n\n{analysis}\n",
        encoding="utf-8",
    )

    post = (
        data.post_text.strip()
        or data.question.strip()
    )

    (folder / "post.md").write_text(
        f"# پست {content_id}\n\n{post}\n",
        encoding="utf-8",
    )

    (folder / "telegram.json").write_text(
        json.dumps(
            telegram_json,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    insert_question(
        (
            content_id,
            data.question.strip(),
            json.dumps(
                options,
                ensure_ascii=False,
            ),
            data.type,
            data.correct_option_id,
            data.analysis.strip(),
            data.post_text.strip(),
            data.telegram_user.id
            if data.telegram_user
            else None,
            "DRAFT",
        )
    )

    return {
        "success": True,
        "content_id": content_id,
    }


@app.post("/api/questions/{content_id}/publish")
def publish_question_api(content_id: str):
    """
    انتشار سؤال بر اساس content_id در تلگرام.
    """

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT *
            FROM questions
            WHERE content_id = ?
            """,
            (content_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="سؤال پیدا نشد.",
        )

    if row["telegram_user_id"] is None:
        raise HTTPException(
            status_code=400,
            detail="شناسه کاربر تلگرام برای این سؤال ثبت نشده است.",
        )

    if row["status"] == "PUBLISHED":
        raise HTTPException(
            status_code=400,
            detail="این سؤال قبلاً منتشر شده است.",
        )

    try:
        poll = publish_question(
            question_id=row["id"],
            chat_id=row["telegram_user_id"],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"خطا در انتشار تلگرام: {exc}",
        )

    with get_connection() as conn:
        conn.execute(
            """
            UPDATE questions
            SET status = ?
            WHERE content_id = ?
            """,
            ("PUBLISHED", content_id),
        )
        conn.commit()

    return {
        "success": True,
        "content_id": content_id,
        "status": "PUBLISHED",
        "telegram_message_id": poll.message_id,
    }


app.mount(
    "/",
    StaticFiles(
        directory="miniapp",
        html=True,
    ),
    name="miniapp",
)
