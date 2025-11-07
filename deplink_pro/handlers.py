# handlers.py (yangilangan - barcha matnlar html.escape orqali yuboriladi)
import os
import datetime
import html
from aiogram import Bot, types
from aiogram.filters import Command, CommandStart
from aiogram.types import FSInputFile
from sqlalchemy import select
from db import AsyncSessionLocal
from models import OrderLink
from utils import make_token, encode_payload, decode_payload, generate_qr_image
from dotenv import load_dotenv

load_dotenv()
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]

# NOTE:
# - All user visible plain-text messages are passed through html.escape(...)
# - We do not escape binary/photo sends (FSInputFile) because those are file uploads.
# - If you use explicit HTML formatting (e.g., <b>, <a href="...">), do NOT escape those parts.

async def handle_generate(message: types.Message):
    # only admin allowed
    uid = int(message.from_user.id)
    if uid not in ADMIN_IDS:
        await message.reply(html.escape("Siz admin emassiz."))
        return

    parts = message.text.strip().split()
    if len(parts) < 3:
        await message.reply(html.escape("Foydalanish: /generate <product_id> <order_log_id>"))
        return

    _, product_id, order_log_id = parts[0], parts[1], parts[2]
    token = make_token()
    unique_key = token
    # save to db
    async with AsyncSessionLocal() as session:
        ol = OrderLink(unique_key=unique_key, product_id=product_id, order_log_id=order_log_id, created_by=str(uid))
        session.add(ol)
        await session.commit()
        await session.refresh(ol)

    payload = encode_payload(unique_key)
    bot_username = (await message.bot.get_me()).username
    link = f"https://t.me/{bot_username}?start={payload}"
    # create QR
    qrfn = f"qr_{unique_key}.png"
    qrpath = generate_qr_image(link, qrfn, logo_path=None)
    # escape the message that includes the link (to avoid parse errors)
    await message.answer(html.escape(f"Link yaratildi: {link}"))
    await message.answer_photo(photo=FSInputFile(qrpath))


async def handle_start(message: types.Message, command: CommandStart):
    # `/start` with payload
    payload = command.args or ''
    if not payload:
        await message.reply(html.escape("Salom! Bu botga xush kelibsiz."))
        return

    unique_key = decode_payload(payload)
    async with AsyncSessionLocal() as session:
        q = select(OrderLink).where(OrderLink.unique_key == unique_key)
        res = await session.execute(q)
        ol = res.scalars().first()
        if not ol:
            await message.reply(html.escape("Link topilmadi yoki noto'g'ri."))
            return
        if ol.is_used:
            await message.reply(html.escape("Bu link allaqachon ishlatilgan."))
            return
        # mark used
        ol.is_used = True
        ol.used_at = datetime.datetime.utcnow()
        session.add(ol)
        await session.commit()
        # Escape the formatted message too
        await message.reply(html.escape(f"Sizning buyurtma: product_id={ol.product_id}, order_log_id={ol.order_log_id}. Link muvaffaqiyatli ishlatildi."))


async def handle_stats(message: types.Message):
    uid = str(message.from_user.id)
    async with AsyncSessionLocal() as session:
        q = select(OrderLink).where(OrderLink.created_by == uid).order_by(OrderLink.created_at.desc()).limit(50)
        res = await session.execute(q)
        rows = res.scalars().all()

    if not rows:
        await message.reply(html.escape("Sizning linklaringiz topilmadi."))
        return

    # Build safe text lines
    lines = []
    for r in rows:
        # convert each field to string and escape
        line = f"ID:{r.id} key:{r.unique_key} used:{r.is_used} product:{r.product_id} order:{r.order_log_id} created:{r.created_at}"
        lines.append(html.escape(line))

    # send as one message (Telegram has length limits; if too large consider sending in chunks or as a file)
    await message.reply("\n".join(lines))


async def handle_qr(message: types.Message):
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        return await message.reply(html.escape("Foydalanish: /qr <link>"))
    link = parts[1].strip()
    unique_key = make_token()
    qrfn = f"qr_{unique_key}.png"
    qrpath = generate_qr_image(link, qrfn, logo_path=None)
    await message.answer_photo(photo=FSInputFile(qrpath))
