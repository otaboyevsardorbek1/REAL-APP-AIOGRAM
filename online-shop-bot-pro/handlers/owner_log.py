import os
import datetime
from aiogram import Router, types, F,Dispatcher
from aiogram.filters import Command
from aiogram.types import FSInputFile
from loader import bot, config,loggers
import asyncio
from datetime import datetime
router_owner = Router()

log_admin=loggers(name="Bot Owner Log Handler")

@router_owner.message(Command("log"))
async def send_log(message: types.Message):
    chat_id=message.chat.id
    full_name=message.from_user.full_name

    if chat_id in config.ADMINS_ID:
        try:
            if not os.path.exists(config.LOG_FILE):
                return await message.answer("❌ Log fayli topilmadi!")
            log_admin.info(f"Log faylini yuborish: {full_name} <--> {chat_id}")
            info_message=await message.answer(f"Kutubturing {config.LOG_FILE} Jo`natishga tayyorlanmoqda.!")
            file_size_mb = os.path.getsize(config.LOG_FILE) / (1024 * 1024)  # MB ga o‘girish
            log_file = FSInputFile(config.LOG_FILE)
            await bot.send_chat_action(message.chat.id, "upload_document")
            await asyncio.sleep(1)
            await bot.delete_message(chat_id=chat_id,message_id=info_message.message_id)    
            await message.answer_document(log_file, caption=f"📂 `{config.LOG_FILE}` fayli\n📏 Hajmi: {file_size_mb:.2f} MB\n📅 Oxirgi yozilgan sana: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Log faylni tozalash
            with open(config.LOG_FILE, "w", encoding="utf-8") as file:
                file.write("")

            await message.answer(f"✅ `{config.LOG_FILE}` fayli yangilandi!")
        except Exception as err:
            log_admin.warning(f"❌ {config.LOG_FILE} faylni yuborib bo‘lmadi! Xato: {err}")
            await message.answer(f"❌ {config.LOG_FILE} faylni yuborib bo‘lmadi! Xato: {err}")
        return
    else:
        username = message.from_user.username  # Username (agar bo'lsa)
        log_admin.warning(f"Log fayilini: {full_name} <--> username: {username} olishga urindi")
        await message.answer("🚫 Siz bu buyruqni ishlata olmaysiz!")
        return

# async def check_log_file():
#     if os.path.exists(config.LOG_FILE):
#         file_size_mb = os.path.getsize(config.LOG_FILE) / (1024 * 1024)  # MB ga o‘girish
#         if file_size_mb >= config.MAX_LOG_SIZE_MB:
#             log_file = FSInputFile(config.LOG_FILE)
#             for chat_id in config.ADMINS_ID:
#                 await bot.send_document(chat_id=chat_id,file=log_file, caption=f"📂 `bot.log` hajmi: {file_size_mb:.2f} MB\n📅 Oxirgi yozilgan sana: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
#             with open(config.LOG_FILE, "w", encoding="utf-8") as file:
#                 file.write("")  # Log faylni tozalash
#             log_admin.info("✅ Log fayli tozalandi va adminga yuborildi!")