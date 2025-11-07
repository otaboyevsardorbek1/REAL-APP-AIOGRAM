import logging
import sys
import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, Update
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from fastapi import FastAPI, Request
from aiogram import Router  # routerni import qilish kerak

# -------- ENV & Config --------
BOT_TOKEN = os.getenv("BOT_TOKEN", "7552988744:AAHZYsxPA_QZvvRGY0Jch-4cCEDI0meuR5E")
ADMIN_ID = [6646928202]
WEBHOOK_PATH = "/webhook"
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "https://kun.uz")
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
LOG_FILE = "bot.log"

# -------- Logging --------
def setup_logger(name: str) -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s:%(lineno)d) - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(name)

logger = setup_logger("admin_panel_bot")

# -------- Bot & Dispatcher --------
MAINTENANCE_MODE = False
storage = MemoryStorage()

# Botni yaratish
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)

# Routerni yaratish
router = Router()

# Admin panel menu and commands
admin_panel_menu = """
/admin - Admin paneliga kirish
/maintenance_on - Texnik rejimni yoqish
/maintenance_off - Texnik rejimni o‘chirish
/settings - Bot sozlamalari
"""

admin_panel_commands = [
    "/maintenance_on", "/maintenance_off", "/settings",
    "/set_webhook", "/delete_webhook", "/webhook_info"
]

# Middleware for maintenance mode
class MaintenanceMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: types.TelegramObject, data):
        global MAINTENANCE_MODE

        if not isinstance(event, Message):
            return await handler(event, data)

        user_id = event.from_user.id
        user_text = (event.text or "").strip()

        logger.info(f"[Middleware] User {user_id} sent message: [{user_text}]")

        if MAINTENANCE_MODE:
            if not (user_id in ADMIN_ID and user_text in admin_panel_commands):
                return await self._send_maintenance_message(event)

        return await handler(event, data)

    async def _send_maintenance_message(self, event: Message):
        """Send maintenance message in different languages"""
        msg = "🛠 Maintenance work is underway. Please try again later."
        await event.answer(msg)

# -------- Handlers --------
@router.message(F.text == "/admin")
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_ID:
        return await message.answer("❌ Sizda bu bo‘limga kirish huquqi yo‘q.")
    await message.answer(admin_panel_menu)

@router.message(F.text == "/maintenance_on")
async def enable_maintenance(message: Message):
    global MAINTENANCE_MODE
    if message.from_user.id in ADMIN_ID:
        MAINTENANCE_MODE = True
        await message.answer("🛠 Texnik rejim YOQILDI.")

@router.message(F.text == "/maintenance_off")
async def disable_maintenance(message: Message):
    global MAINTENANCE_MODE
    if message.from_user.id in ADMIN_ID:
        MAINTENANCE_MODE = False
        await message.answer("✅ Texnik rejim O‘CHIRILDI.")

@router.message(F.text == "/start")
async def start_handler(message: Message):
    await message.answer(f"👋 Salom \n{admin_panel_menu}")

@router.message(F.text == "/settings")
async def settings_handler(message: Message):
    if message.from_user.id not in ADMIN_ID:
        return await message.answer("❌ Ushbu bo‘lim faqat admin uchun.")
    if not MAINTENANCE_MODE:
        return await message.answer("⚠️ Sozlamalar faqat texnik rejimda mavjud.")
    settings_text = (
        "🧪 Sozlamalar:\n"
        "/set_webhook - webhookni sozlash\n"
        "/delete_webhook - webhookni olib tashlash\n"
        "/webhook_info - Webhook holatini ko‘rish"
    )
    await message.answer(settings_text)

@router.message(F.text == "/set_webhook")
async def set_webhook_handler(message: Message):
    if message.from_user.id in ADMIN_ID:
        await bot.set_webhook(WEBHOOK_URL)
        await message.answer(f"✅ Webhook o'rnatildi: {WEBHOOK_URL}")

@router.message(F.text == "/delete_webhook")
async def delete_webhook_handler(message: Message):
    if message.from_user.id in ADMIN_ID:
        await bot.delete_webhook()
        await message.answer("🗑 Webhook o'chirildi")

@router.message(F.text == "/webhook_info")
async def webhook_info_handler(message: Message):
    if message.from_user.id in ADMIN_ID:
        info = await bot.get_webhook_info()
        text = (
            f"🌐 Webhook URL: {info.url or '❌ O‘rnatilmagan'}\n"
            f"⏳ Pending Updates: {info.pending_update_count}\n"
            f"📡 IP Address: {info.ip_address or '❌ Yo‘q'}\n"
            f"🔒 Has Custom Certificate: {info.has_custom_certificate}\n"
            f"⚡ Max Connections: {info.max_connections or 'default'}\n"
            f"📂 Allowed Updates: {info.allowed_updates or 'default'}"
        )
        await message.answer(text)

@router.message(F.text == "/me")
async def me_handler(message: Message):
    data = {
        "id": message.from_user.id,
        "username": message.from_user.username,
        "full_name": message.from_user.full_name
    }
    await message.answer(text=str(data))

app = FastAPI()

@app.post(WEBHOOK_PATH)
async def process_webhook(update: dict, request: Request):
    telegram_update = Update.model_validate(update)
    await dp.feed_update(bot, telegram_update)
    return {"status": "ok"}

# -------- Runner --------
async def main():
    dp.include_router(router)
    dp.message.middleware(MaintenanceMiddleware())

    await bot.set_my_commands([
        types.BotCommand(command="/start", description="Botni ishga tushirish"),
        types.BotCommand(command="/settings", description="Bot sozlamalari"),
        types.BotCommand(command="/maintenance_on", description="Texnik rejimni yoqish"),
        types.BotCommand(command="/maintenance_off", description="Texnik rejimni o'chirish"),
        types.BotCommand(command="/admin", description="Admin paneli"),
        types.BotCommand(command="/set_webhook", description="Webhookni o'rnatish"),
        types.BotCommand(command="/delete_webhook", description="Webhookni o'chirish"),
        types.BotCommand(command="/webhook_info", description="Webhook holati"),
    ])

    # Webhookni o‘rnatilmagan bo‘lsa, pollingni boshlaymiz:
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
