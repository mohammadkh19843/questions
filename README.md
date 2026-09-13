# Questions

Telegram Bot + Mini App برای ساخت سؤال، Quiz و آماده‌سازی محتوای انتشار.

## تکنولوژی

- Python
- pyTelegramBotAPI
- FastAPI
- SQLite
- HTML / CSS / JavaScript

## ساختار

```text
qusetions/
├── bot.py
├── api.py
├── config.py
├── database.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── miniapp/
└── content/
```

## اجرا

### 1. ساخت محیط مجازی

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

### 2. نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

### 3. تنظیم Bot

فایل `.env.example` را به `.env` تغییر نام بده و مقدار `BOT_TOKEN` را قرار بده.

`WEBAPP_URL` باید آدرس HTTPS مربوط به Mini App باشد.

### 4. اجرای API

```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

### 5. اجرای Bot

در ترمینال دوم:

```bash
python bot.py
```

## خروجی محتوا

بعد از ذخیره هر سؤال، یک پوشه مثل زیر ساخته می‌شود:

```text
content/
└── CNT-000001/
    ├── question.json
    ├── analysis.md
    ├── post.md
    ├── telegram.json
    └── media/
```

مرحله بعدی پروژه: اضافه کردن انتشار مستقیم Native Telegram Poll/Quiz با `sendPoll` و سپس احراز امن `initData` تلگرام.
