# Telegram One-time Deep Link Bot (Aiogram v3, async SQLAlchemy, SQLite)

This repository contains a working example Telegram bot that implements:
- One-time (single-use) deep links: `/start <payload>` where payload maps to a DB record.
- `/generate <product_id> <order_log_id>` command for admins to create deep links and QR codes.
- `/stats` command for users to view their created links and usage.
- QR generation (logo optional) saved to `qr_codes/` and sent to users.

## Features
- Aiogram v3 (async polling)
- Async SQLAlchemy with SQLite (aiosqlite)
- `qrcode` + `Pillow` for QR generation
- Simple structure that you can extend (FastAPI admin, Postgres, etc.)

## Quickstart (local)
1. Copy `.env.example` to `.env` and set your `BOT_TOKEN` (and optionally `ADMIN_IDS` comma-separated).
2. Create virtualenv and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
3. Run the bot:
   ```bash
   python main.py
   ```
4. As admin (your Telegram ID in `ADMIN_IDS`), run:
   `/generate 123 555` — bot will reply with a start link and a QR image.

## Files
- `main.py` — entrypoint, loads env, starts polling.
- `db.py` — async SQLAlchemy engine & session utils and init_db()
- `models.py` — `OrderLink` model
- `handlers.py` — command handlers: /start, /generate, /stats, /qr
- `utils.py` — helper for generating start payloads and QR images
- `requirements.txt` — dependencies
- `.env.example` — example env variables

## Notes
- This bot uses SQLite for simplicity. For production, use PostgreSQL and a connection pool.
- The bot stores a `unique_key` in DB; the `/start` receives that key as payload and marks link used.
- Telegram limits start parameter length; this implementation stores details in DB and only sends a short token.

