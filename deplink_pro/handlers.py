import os
import datetime
import html
from aiogram import Bot, types
from aiogram.filters import Command, CommandStart
from aiogram.utils.deep_linking import create_start_link, decode_payload
from aiogram.types import FSInputFile
from sqlalchemy import select
import json
from db import AsyncSessionLocal
from models import OrderLink
from utils import make_token, encode_payload, decode_payload, generate_qr_image
from dotenv import load_dotenv

load_dotenv()
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]

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
    caption_info=f"<a href='{link}'>QR kodini referal_linki</a>"
    await message.answer_photo(photo=FSInputFile(qrpath), caption=html.escape(caption_info))


async def handle_start(message: types.Message, command: CommandStart):
    # `/start` with payload
    payload = command.args or ''
    if not payload:
        return await message.reply(html.escape("Salom! Bu botga xush kelibsiz."))
    
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
 # demo deplink demo
async def generate_deeplink_pro(message: types.Message):
    """Foydalanuvchi uchun murakkab deep-link yaratish"""
    # Murakkab ma'lumot (JSON shaklida)
    payload = {
        "ref_id": message.from_user.id,
        "plan": "admin",
        "lang": f"{message.from_user.language_code}",
        "reg":"2024-09-23",
        "end":"2025-11-08"}

    # JSON stringga aylantiramiz
    payload_str = json.dumps(payload)

    # Deep link yaratamiz
    link = await create_start_link(Bot, payload_str, encode=True)
    await message.answer(f"Mana sizning murakkab deep-linkingiz:\n\n{link}")

# demo dep link pro get info
async def start_handler_pro(message: types.Message, command: CommandStart):
    """Foydalanuvchi deep-link orqali kirganda"""
    if command.args:
        try:
            # Base64 decode
            decoded = decode_payload(command.args)
            # JSON ni Python dict ga parse qilamiz
            data = json.loads(decoded)

            await message.answer(
                "<b>Siz deep-link orqali kirdingiz!</b>\n\n"
                f"<b>Ref ID:</b> {data.get('ref_id')}\n"
                f"<b>Tarif:</b> {data.get('plan')}\n"
                f"<b>Til:</b> {data.get('lang')}\n"
                f"<b>Ro'yxatdan o'tgan sana:</b> {data.get('reg')}\n"
                f"<b>Shartnoma tugash sanasi:</b/> {data.get('end')}"
            )
        except Exception as e:
            await message.answer(f"Xatolik: {e}")
    else:
        await message.answer("Salom! Bu oddiy /start buyrug‘i 🙂")