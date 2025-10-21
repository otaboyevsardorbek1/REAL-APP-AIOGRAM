import asyncio
from aiogram import Dispatcher,types,Bot
from loader import dp, bot,loggers,check_log_file
from handlers import register_all_handlers
from config import config
import time
date_now = time.strftime("%Y-%m-%d", time.localtime())
time_now = time.strftime("%H:%M:%S", time.localtime())

# bot ishga tushganda adminlarga habar yuborish
async def on_startup_notify(dp: Dispatcher):
    for admin in config.ADMINS_ID:
        try:
            text = (f"✅Bot ishga tushdi!✅\n"
                    f"📅Mon: {date_now}\n"
                    f"⏰Vaqt: {time_now}\n"
                    f"Bot: {config.BOT_USERNAME}")
            await bot.send_message(
                admin, text=text, disable_notification=True
            )
        except Exception as error:
            text=(f"Bunday admin yo`q:{admin}\nXato: {error}")
            await bot.send_message(chat_id=admin,text=text)

# Bot ishdan chiqsa yoki to‘xtab qolsa adminga xabar yuborish
async def on_shutdown_notify(dp: Dispatcher):
    for admin in config.ADMINS_ID:
        try:
            text = ("Bot ishdan chiqdi\n"
                    f"📅Mon: {date_now}\n"
                    f"⏰Vaqt: {time_now}\n"
                    "Sababini /log buyrug‘i orqali ko‘rib olishingiz mumkin!")
            await bot.send_message(
                admin, text=text, disable_notification=True
            )
        except Exception as error:
            text = f"Bunday admin yo‘q: {admin}\nXato: {error}"
            await bot.send_message(chat_id=admin, text=text)
    await bot.session.close()
            
async def ERROR_TO_ADMIN_SEND(update: types.Update, exception: Exception):
    try:
       for chat_id in config.ADMINS_ID:
            await bot.send_message(chat_id, f"Xato yuz berdi: {exception}\nUpdate: {update}")
    except Exception as e:
        await bot.send_message(chat_id, f"Xato yuborishda muammo: {e}")

async def nofactins_admin():
    # Error handlerni botga qo'shish

    dp.error.handlers.append(ERROR_TO_ADMIN_SEND)
    dp.startup.handlers.append(on_startup_notify(dp=dp))
    dp.shutdown.handlers.append(on_shutdown_notify(dp=dp))

def init_db():
    from db import Base, engine
    from db import models
    Base.metadata.create_all(bind=engine)
    print("Database initialized!")

bot_start=loggers(name="BOT-ISHGA-TUSHDI")
async def main():
    try:
        init_db()  # Ma'lumotlar bazasini yaratish
        await check_log_file() # Log faylni tekshirish va tozalash
        await nofactins_admin()  # Adminlarga xabar yuborish va error handlerni qo'shish
        bot_start.info("Bot ishga tushirilmoqda...")
        await bot.set_my_commands([
            types.BotCommand(command="/start", description="Botni ishga tushirish"),
            types.BotCommand(command="/settings", description="Bot sozlamalari"),
            types.BotCommand(command="/maintenance_on", description="Texnik rejimni yoqish"),
            types.BotCommand(command="/maintenance_off", description="Texnik rejimni o'chirish"),
        ])  # Bot komandalarini sozlash
        register_all_handlers(dp)  # Barcha handlerlarni ro'yxatdan o'tkazish
        await dp.start_polling(bot)  # Botni ishga tushirish
        bot_start.info("Bot ishga tushdi!")
    except Exception as e:
        bot_start.error(f"Bot ishga tushishda xato: {e}")
        await dp.stop_polling()
        raise e
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())