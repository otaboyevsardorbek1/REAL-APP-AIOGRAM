import os, asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from dotenv import load_dotenv
from db import init_db
from handlers import handle_generate, handle_start, handle_stats, handle_qr
from aiogram import F

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise RuntimeError("Botfatherdan olingan token topilmadi. Iltimos, .env faylida BOT_TOKEN o'zgaruvchisini sozlang.")

bot = Bot(BOT_TOKEN, parse_mode='HTML')
dp = Dispatcher()

# register handlers
dp.message.register(handle_generate, Command(commands=['generate']))
dp.message.register(handle_start, CommandStart(deep_link=True))
dp.message.register(handle_stats, Command(commands=['stats']))
dp.message.register(handle_qr, Command(commands=['qr']))

async def main():
    await init_db()
    print("Bot starting...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
