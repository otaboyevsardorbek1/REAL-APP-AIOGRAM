import os
import sys
import subprocess
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
import asyncio

# .env faylidan bot tokenini yuklash
load_dotenv()
API_TOKEN = "7165919586:AAGd6cHXxxsnzguMvEn_QKenvZdcoRSqClg"

# Bot va Dispatcher yaratish
try:
    bot = Bot(
        token=API_TOKEN, 
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
except Exception as e:
    print(f"Bot yaratishda xato: {e}")
    sys.exit(1)

# Jarayonni qayta ishga tushirish usullari
def check_execv_support():
    try:
        python = sys.executable
        os.execv(python, [python, "-c", "print('test')"])
        return True
    except Exception as e:
        print(f"execv xatosi: {e}")
        return False

def check_subprocess_support():
    try:
        p = subprocess.Popen([sys.executable, "-c", "print('otaboyev_sardorbek')"])
        p.wait(timeout=5)
        return p.returncode == 0
    except Exception as e:
        print(f"subprocess xatosi: {e}")
        return False

def restart_with_execv():
    python = sys.executable
    os.execv(python, [python] + sys.argv)

def restart_with_subprocess():
    subprocess.Popen([sys.executable] + sys.argv)
    # sys.exit() o'rniga asyncio loop ni to'xtatamiz
    asyncio.get_event_loop().stop()

def select_restart_method():
    subprocess_ok = check_subprocess_support()
    execv_ok = check_execv_support()
    
    if execv_ok and subprocess_ok:
        return "both"
    elif execv_ok:
        return "execv"
    elif subprocess_ok:
        return "subprocess"
    else:
        return None

# /start komandasini ishlatish
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Salom! Men yordamchi botman. Dasturni qayta ishga tushurish uchun /restart buyrug'ini yuboring.")

# /restart komandasini ishlatish
@dp.message(Command("restart"))
async def cmd_restart(message: types.Message):
    method = select_restart_method()
    
    if method is None:
        await message.answer("Qayta ishga tushirish imkoniyati yo'q. Iltimos, tizim administratoriga murojaat qiling.")
        return

    # Foydalanuvchidan qayta ishga tushirish usulini tanlashni so'rash
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="execv")],
            [types.KeyboardButton(text="subprocess")],
            [types.KeyboardButton(text="both")]
        ],
        resize_keyboard=True
    )
    await message.answer("Qayta ishga tushirish usulini tanlang: execv, subprocess, yoki both", reply_markup=markup)

# Foydalanuvchi qayta ishga tushirish usulini tanlagandan so'ng
@dp.message(lambda message: message.text in ["execv", "subprocess", "both"])
async def handle_restart_choice(message: types.Message):
    user_choice = message.text.strip()

    if user_choice == "execv":
        await message.answer("Dastur `execv` usuli bilan qayta ishga tushiriladi...")
        # Xabarni yuborishni kutamiz
        await asyncio.sleep(1)
        restart_with_execv()
    elif user_choice == "subprocess":
        await message.answer("Dastur `subprocess` usuli bilan qayta ishga tushiriladi...")
        # Xabarni yuborishni kutamiz
        await asyncio.sleep(1)
        restart_with_subprocess()
    elif user_choice == "both":
        await message.answer("Ikkala usul ham ishlaydi. Tanlovingizni qiling.")
        # Bu yerda tanlovni tekshirib, tanlangan usulni bajarish mumkin
        restart_method = select_restart_method()
        if restart_method == "execv":
            await asyncio.sleep(1)
            restart_with_execv()
        elif restart_method == "subprocess":
            await asyncio.sleep(1)
            restart_with_subprocess()
        else:
            await message.answer("Noto'g'ri usul. Iltimos, qayta urinib ko'ring.")

# Botni ishga tushirish
async def main():
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        print("Bot to'xtatildi")
    except Exception as e:
        print(f"Xato: {e}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Dastur to'xtatildi")
    except Exception as e:
        print(f"Asosiy xato: {e}")