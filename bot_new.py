import sys
import asyncio
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
import os
from datetime import datetime 
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.enums import ParseMode
import logging
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand, BotCommandScopeChat,FSInputFile
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from bot_new_error import ErrorReporterMiddleware,StartStopNotifyMiddleware
from sqlalchemy import Column, Integer, String, select, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

#===local==settings===
LOG_FILE = "bot.log"
BOT_TOKEN = "8425142685:AAH_RIP1J4kbuqQtoS5M3a_QQNpfPCV-byI"
MAX_LOG_SIZE_MB=20

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# ======= CONFIG =======
DATABASE_URL = "sqlite+aiosqlite:///users.db"
OWNER_ID = [6646928202]  # Owner ID

# ========logging=======
# ✅ Log sozlamalari
def loggers(log_name):
    logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s:%(lineno)d) - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),  # Faylga yozish
        logging.StreamHandler(sys.stdout)  # Konsolga chiqarish
    ])
    logger = logging.getLogger(log_name)
    return logger
# =======logerr=set===
loggeradmin=loggers(log_name="Panel")
# register middleware for message processing (ErrorReporter)
dp.message.middleware(ErrorReporterMiddleware(bot, OWNER_ID))
# ======= Adminlarga habar jo`natish =======
start_stop_mw = StartStopNotifyMiddleware(bot, OWNER_ID)
# 🔹 Startup va Shutdown hodisalarini ro‘yxatga olish
dp.startup.register(start_stop_mw.startup)
dp.shutdown.register(start_stop_mw.shutdown)
# ======= SQLAlchemy setup =======
Base = declarative_base()
engine = create_async_engine(DATABASE_URL, echo=False)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# ======= Router =======
router = Router()

# ======= User modeli =======
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    role = Column(String, default="guest")

# ======= Rollar ierarxiyasi =======
ROLE_HIERARCHY: dict[str, list[str]] = {
    "owner": ["admin", "manager", "worker", "diller", "dastafka", "guest"],# dasturchi rejimi
    "admin": ["manager", "worker", "diller", "dastafka", "guest"],
    "manager": ["worker", "diller", "dastafka", "guest"],
    "worker": ["dastafka", "guest"],
    "diller": ["diller", "guest"],
    "dastafka": ["guest", "dastafka"],
    "guest": ["guest"]
}
# ======= Rollar ierarxiyasi darajaga qarab foydalanuvchi yaratish =======
def check_user_level_create(user: User) -> list[str]:
    if user.role == "owner":
        return ROLE_HIERARCHY["owner"]
    elif user.role == "admin":
        return ROLE_HIERARCHY["admin"]
    elif user.role == "manager":
        return ROLE_HIERARCHY["manager"]
    elif user.role == "worker":
        return ROLE_HIERARCHY["worker"]
    elif user.role == "diller":
        return ROLE_HIERARCHY["diller"]
    elif user.role == "dastafka":
        return ROLE_HIERARCHY["dastafka"]
    else:
        return ROLE_HIERARCHY["guest"]

# ======= Rollarga mos komandalar =======
COMMANDS_BY_ROLE = {
    "owner": [
        BotCommand(command="owner_panel", description="👑 Owner Panel"),
        BotCommand(command="profile", description="👤 Mening profilim"),
        BotCommand(command="admin_panel", description="⚙️ Admin Panel"),
        BotCommand(command="manager_panel", description="📋 Manager Panel"),
        BotCommand(command="users", description="📋 Foydalanuvchilar"),
        BotCommand(command="settings", description="⚙️ Sozlamalar"),
        BotCommand(command="broadcast", description="📢 E'lon yuborish"),
        BotCommand(command="status", description="📊 Statistika"),
        BotCommand(command="db_backup", description="💾 Ma'lumotlar bazasini zaxiralash"),
        BotCommand(command="db_restore", description="♻️ Ma'lumotlar bazasini tiklash"),
        BotCommand(command="log", description="📝 Log fayllarini ko‘rish"),
        BotCommand(command="help", description="❓ Yordam"),
    ],
    "admin": [
        BotCommand(command="admin_panel", description="⚙️ Admin Panel"),
        BotCommand(command="profile", description="👤 Mening profilim"),
        BotCommand(command="manager_panel", description="📋 Manager Panel"),
        BotCommand(command="users", description="📋 Foydalanuvchilar"),
        BotCommand(command="settings", description="⚙️ Sozlamalar"),
        BotCommand(command="status", description="📊 Mening ma'lumotlarim"),
        BotCommand(command="terms", description="📜 Foydalanuvchi shartlari"),
        BotCommand(command="support", description="🆘 Texnik yordam"),
        BotCommand(command="feedback", description="📝 Fikr-mulohazalar"),
        BotCommand(command="setrole", description="🎭 Rol berish"),
        BotCommand(command="owner", description="👤 Owner bilan bog'lanish."),
        BotCommand(command="help", description="❓ Yordam"),
    ],
    "manager": [
        BotCommand(command="manager_panel", description="📋 Manager Panel"),
        BotCommand(command="profile", description="👤 Mening profilim"),
        BotCommand(command="status", description="📊 Mening ma'lumotlarim"),
        BotCommand(command="terms", description="📜 Foydalanuvchi shartlari"),
        BotCommand(command="support", description="🆘 Texnik yordam"),
        BotCommand(command="feedback", description="📝 Fikr-mulohazalar"),
        BotCommand(command="setrole", description="🎭 Rol berish"),
        BotCommand(command="tasks", description="🧾 Vazifalar"),
        BotCommand(command="owner", description="👤 Owner bilan bog'lanish."),
        BotCommand(command="help", description="❓ Yordam"),
    ],
    "worker": [
        BotCommand(command="tasks", description="🧾 Vazifalar"),
        BotCommand(command="profile", description="👤 Mening profilim"),
        BotCommand(command="status", description="📊 Mening ma'lumotlarim"),
        BotCommand(command="terms", description="📜 Foydalanuvchi shartlari"),
        BotCommand(command="support", description="🆘 Texnik yordam"),
        BotCommand(command="feedback", description="📝 Fikr-mulohazalar"),
        BotCommand(command="setrole", description="🎭 Rol berish"),
        BotCommand(command="help", description="❓ Yordam"),
        BotCommand(command="owner", description="👤 Owner bilan bog'lanish."),
    ],
    "diller": [
        BotCommand(command="orders", description="🛒 Buyurtmalar"),
        BotCommand(command="profile", description="👤 Mening profilim"),
        BotCommand(command="status", description="📊 Mening ma'lumotlarim"),
        BotCommand(command="terms", description="📜 Foydalanuvchi shartlari"),
        BotCommand(command="support", description="🆘 Texnik yordam"),
        BotCommand(command="feedback", description="📝 Fikr-mulohazalar"),
        BotCommand(command="setrole", description="🎭 Rol berish"),
        BotCommand(command="owner", description="👤 Owner bilan bog'lanish."),
        BotCommand(command="help", description="❓ Yordam"),
    ],
    "dastafka": [
        BotCommand(command="deliveries", description="🚚 Yetkazmalar"),
        BotCommand(command="profile", description="👤 Mening profilim"),
        BotCommand(command="status", description="📊 Mening ma'lumotlarim"),
        BotCommand(command="terms", description="📜 Foydalanuvchi shartlari"),
        BotCommand(command="support", description="🆘 Texnik yordam"),
        BotCommand(command="feedback", description="📝 Fikr-mulohazalar"),
        BotCommand(command="setrole", description="🎭 Rol berish"),
        BotCommand(command="owner", description="👤 Owner bilan bog'lanish."),
        BotCommand(command="help", description="❓ Yordam"),
    ],
    "guest": [
        BotCommand(command="start", description="🔰 Boshlash"),
        BotCommand(command="profile", description="👤 Mening profilim"),
        BotCommand(command="status", description="📊 Mening ma'lumotlarim"),
        BotCommand(command="terms", description="📜 Foydalanuvchi shartlari"),
        BotCommand(command="support", description="🆘 Texnik yordam"),
        BotCommand(command="feedback", description="📝 Fikr-mulohazalar"),
        BotCommand(command="setrole", description="🎭 Rol berish"),
        BotCommand(command="owner", description="👤 Owner bilan bog'lanish."),
        BotCommand(command="help", description="❓ Yordam"),
    ]
}

# ======= Helper funksiyalar =======
async def get_or_create_user(user_id: int, full_name: str) -> User:
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            role = "owner" if user_id == OWNER_ID[0] else "guest"
            user = User(id=user_id, full_name=full_name, role=role)
            session.add(user)
            await session.commit()
        return user

async def set_user_commands(bot: Bot, user: User):
    commands = COMMANDS_BY_ROLE.get(user.role, COMMANDS_BY_ROLE["guest"])
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeChat(chat_id=user.id))

# ======= /start =======
@router.message(F.text == "/start")
async def cmd_start(message: types.Message, bot: Bot):
    user = await get_or_create_user(message.from_user.id, message.from_user.full_name)
    await set_user_commands(bot, user)
    await message.answer(f"👋 Salom, {user.full_name}!\nSizning rol: <b>{user.role}</b>")
# ======= /owner =======
@router.message(F.text == "/owner")
async def cmd_start(message: types.Message, bot: Bot):
    user = await get_or_create_user(message.from_user.id, message.from_user.full_name)
    await set_user_commands(bot, user)
    ower_str=''
    ower_str+='Dasturchi: Otaboyev sardorbek Davronbek o`g`li\n'
    ower_str+='tg_chanel: @otaboyev_sardorbek_blog\n'
    ower_str+='tg_group: @otaboyev_sardorbek_support\n'
    ower_str+='tg_username: @otaboyev_sardorbek\n'
    ower_str+='Email:otaboyevsardorbek295@gmail.com\n'
    if user.id not in OWNER_ID:
        await message.answer(ower_str)
    else:
       return await message.answer(f"\n{user.full_name}!\nDaraja:<b>{user.role}</b> \n {ower_str}")

# ======= /setrole =======
@router.message(F.text.startswith("/setrole"))
async def cmd_set_role(message: types.Message, bot: Bot):
    args = message.text.split()
    history = message.chat.id

    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.id == message.from_user.id))
        current_user = result.scalar_one_or_none()

        if not current_user:
            return await message.answer("🚫 Avval /start ni bosib ro‘yxatdan o‘ting.")

        if len(args) != 3:
            role_info = check_user_level_create(current_user)
            info = (
                "🚫 Siz bu roldagi foydalanuvchini yaratishingiz mumkin.\n"
                f"🔍 Sizning rol: \n\n {current_user.role}\n"
                f"Yaratish mumkin bo‘lgan rollar: {role_info}\n"
                f"❌ Format: /setrole [user_id] [rol] \n"
                f"Foydalanuvchini maʼlumotlarini olish uchun /users buyrug‘ini yuboring."
            )
            return await message.answer(info)

        try:
            target_user_id = int(args[1])
        except ValueError:
            return await message.answer("❌ user_id faqat raqam bo‘lishi kerak!")

        new_role = args[2].lower()
        if new_role not in COMMANDS_BY_ROLE:
            return await message.answer("❌ Noto‘g‘ri rol nomi!")

        if new_role not in ROLE_HIERARCHY.get(current_user.role, []):
            role_info = check_user_level_create(current_user)
            info = (
                "🚫 Siz bu roldagi foydalanuvchini yaratishingiz mumkin emas.\n"
                f"🔍 Sizning rol: {current_user.role}\n"
                f"Yaratish mumkin bo‘lgan rollar: {role_info}"
            )
            return await message.answer(info)

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(
                text="✅ Ha, tasdiqlayman",
                callback_data=f"confirm_setrole:{message.from_user.id}:{target_user_id}:{new_role}"
            ),
            types.InlineKeyboardButton(
                text="❌ Yo‘q, bekor qilish",
                callback_data="cancel_setrole"
            ),
        ]
    ])

    await message.answer(
        f"🔔 Siz <b>{target_user_id}</b> foydalanuvchi rolini <b>{new_role}</b> ga o‘zgartirmoqchisiz.\n"
        f"Tasdiqlaysizmi?",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


# ======= Tasdiqlash =======
@router.callback_query(F.data.startswith("confirm_setrole"))
async def confirm_setrole_callback(callback: types.CallbackQuery, bot: Bot):
    _, admin_id, target_user_id, new_role = callback.data.split(":")
    admin_id = int(admin_id)
    target_user_id = int(target_user_id)

    # Faqat shu admin bosganini tekshiramiz
    if callback.from_user.id != admin_id:
        return await callback.answer("❌ Siz bu amalni tasdiqlay olmaysiz!", show_alert=True)

    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.id == target_user_id))
        target_user = result.scalar_one_or_none()

        if not target_user:
            target_user = User(
                id=target_user_id,
                full_name=f"{target_user_id} <--> {admin_id} <--> Qo‘shildi!",
                role=new_role
            )
            session.add(target_user)
        else:
            target_user.role = new_role

        await session.commit()

    try:
        await set_user_commands(bot, target_user)
        await bot.send_message(target_user_id, f"🔔 Sizning rolingiz {new_role} ga o‘zgartirildi.")
    except Exception:
        pass

    await callback.message.edit_text(
        f"✅ Foydalanuvchi <b>{target_user_id}</b> roli <b>{new_role}</b> ga o‘zgartirildi.",
        parse_mode="HTML"
    )


# ======= Bekor qilish =======
@router.callback_query(F.data == "cancel_setrole")
async def cancel_setrole_callback(callback: types.CallbackQuery):
    await callback.message.edit_text("❌ Amal bekor qilindi.")

# ======= /users =======
@router.message(F.text == "/users")
async def cmd_list_users(message: types.Message, bot: Bot):
    async with async_session_maker() as session:
        db_user = await session.get(User, message.from_user.id)
        if not db_user or db_user.role not in ROLE_HIERARCHY:
            return await message.answer("🚫 Sizda bu buyruqdan foydalanish huquqi yo‘q.")
    await show_users_page(bot, message.chat.id, 1)

# ======= Sahifalash =======
async def show_users_page(bot: Bot, chat_id: int, page: int):
    per_page = 10
    offset = (page - 1) * per_page

    async with async_session_maker() as session:
        total_result = await session.execute(select(func.count(User.id)))
        total_users = total_result.scalar()
        total_pages = max((total_users + per_page - 1) // per_page, 1)

        result = await session.execute(
            select(User).order_by(User.id).limit(per_page).offset(offset)
        )
        users = result.scalars().all()

    if not users:
        return await bot.send_message(chat_id, "📭 Bu sahifada foydalanuvchi yo‘q.")

    text = [f"📋 <b>Foydalanuvchilar ro‘yxati</b>\nSahifa: {page}/{total_pages}\n"]
    for u in users:
        text.append(f"🆔 <code>{u.id}</code> | {u.full_name} | 🎭 {u.role}")

    buttons = []
    if page > 1:
        buttons.append(InlineKeyboardButton(text="⬅ Oldingi", callback_data=f"users_page:{page-1}"))
    if page < total_pages:
        buttons.append(InlineKeyboardButton(text="Keyingi ➡", callback_data=f"users_page:{page+1}"))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons] if buttons else [])
    await bot.send_message(chat_id, "\n".join(text), reply_markup=keyboard)

# ======= Callback handler =======
@router.callback_query(F.data.startswith("users_page:"))
async def paginate_users(callback: types.CallbackQuery, bot: Bot):
    async with async_session_maker() as session:
        db_user = await session.get(User, callback.from_user.id)
        if not db_user or db_user.role not in ROLE_HIERARCHY:
            return await callback.answer("🚫 Sizga ruxsat berilmagan!", show_alert=True)

    page = int(callback.data.split(":")[1])
    await callback.message.delete()
    await show_users_page(bot, callback.message.chat.id, page)

# ======= Panel komandalar =======
@router.message(F.text == "/owner_panel")
async def owner_panel(message: types.Message):
    await message.answer("👑 Owner Panel — barcha huquqlar sizda!")

@router.message(F.text == "/admin_panel")
async def admin_panel(message: types.Message):
    await message.answer("⚙️ Admin Panel — manager va pastdagilarni boshqarishingiz mumkin.")

@router.message(F.text == "/manager_panel")
async def manager_panel(message: types.Message):
    await message.answer("📋 Manager Panel — mahsulot qo‘shish/o‘chirish va workerlarni boshqarish.")

@router.message(F.text == "/tasks")
async def tasks(message: types.Message):
    await message.answer("🧾 Vazifalar paneli — Worker vazifalari.")

@router.message(F.text == "/orders")
async def orders(message: types.Message):
    await message.answer("🛒 Buyurtmalar paneli — Diller vazifalari.")

@router.message(F.text == "/deliveries")
async def deliveries(message: types.Message):
    await message.answer("🚚 Yetkazmalar paneli — Dastafka vazifalari.")

# ======= /help =======
@router.message(F.text == "/help")
async def cmd_help(message: types.Message):
    await message.answer("⚙️ Yordam:\n\n"
                         "1. /start - Botni ishga tushirish\n"
                         "2. /setrole - Foydalanuvchiga rol berish\n"
                         "3. /users - Foydalanuvchilar ro‘yxati\n"
                         "4. /help - Yordam ko‘rsatmasi\n"
                         "5. /terms - Foydalanuvchi shartlari\n"
                         "6. /support - Texnik yordam\n")


@router.message(F.text == "/status")
async def get_user_profile_photo(message: Message):
    user = message.from_user
    bot_username=bot.get_me()
    # Foydalanuvchining profil rasmlarini olish
    photos = await bot.get_user_profile_photos(user_id=user.id, limit=1)

    # Foydalanuvchi haqida ma'lumot tayyorlash
    caption = (
        f"🆔 ID: <code>{user.id}</code>\n"
        f"👤 Ism: <b>{user.full_name}</b>\n"
        f"🔗 Username: @{user.username if user.username else '❌'}\n"
        f"🌐 Til kodi: {user.language_code if user.language_code else '❌'}\n"
        f"⭐ Telegram Premium: {'✅' if getattr(user, 'is_premium', False) else '❌'}"
    )

    if photos.total_count > 0:
        # Eng so‘nggi profil rasmi va eng katta o‘lchamdagi variant
        photo = photos.photos[0][-1]

        await bot.send_photo(
            chat_id=message.chat.id,
            photo=photo.file_id,
            caption=caption,
            parse_mode=ParseMode.HTML
        )
    else:
        await message.answer(
            text=f"{bot_username}\n\n" + caption,
            parse_mode=ParseMode.HTML
        )
# ✅ Bot log faylini yuborish va tozalash
@dp.message(Command("log"))
async def send_log(message: types.Message):
    chat_id=message.chat.id
    if chat_id in OWNER_ID:
        try:
            if not os.path.exists(LOG_FILE):
                return await message.answer("❌ Log fayli topilmadi!")
            info_messgae=await message.answer(f"Kutubturing {LOG_FILE} Jo`natishga tayyorlanmoqda.!")
            file_size_mb = os.path.getsize(LOG_FILE) / (1024 * 1024)  # MB ga o‘girish
            log_file = FSInputFile(LOG_FILE)
            await bot.send_chat_action(message.chat.id, "upload_document")
            await asyncio.sleep(1)
            await bot.delete_message(chat_id=chat_id,message_id=info_messgae.message_id)    
            await message.answer_document(log_file, caption=f"📂 `{LOG_FILE}` fayli\n📏 Hajmi: {file_size_mb:.2f} MB\n📅 Oxirgi yozilgan sana: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Log faylni tozalash
            with open(LOG_FILE, "w", encoding="utf-8") as file:
                file.write("")

            await message.answer(f"✅ `{LOG_FILE}` fayli yangilandi!")
        except Exception as err:
            
            await message.answer(f"❌ {LOG_FILE} faylni yuborib bo‘lmadi! Xato: {err}")
    else:
        await message.answer("🚫 Siz bu buyruqni ishlata olmaysiz!")

 
# ✅ Log fayl hajmini tekshirish va avtomatik yuborish
async def check_log_file():
    if os.path.exists(LOG_FILE):
        file_size_mb = os.path.getsize(LOG_FILE) / (1024 * 1024)  # MB ga o‘girish
        if file_size_mb >= MAX_LOG_SIZE_MB:
            log_file = FSInputFile(LOG_FILE)
            for chat_id in OWNER_ID:
                await bot.send_document(chat_id=chat_id,file=log_file, caption=f"📂 `bot.log` hajmi: {file_size_mb:.2f} MB\n📅 Oxirgi yozilgan sana: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            with open(LOG_FILE, "w", encoding="utf-8") as file:
                file.write("")  # Log faylni tozalash

# ======= Main =======
async def main():
   try:
       await check_log_file()
       dp.include_router(router)

       async with engine.begin() as conn:
           await conn.run_sync(Base.metadata.create_all)

       await bot.delete_webhook(drop_pending_updates=True)
       print("✅ Bot ishga tushdi")
       await dp.start_polling(bot)
   except (KeyboardInterrupt):
       print("Dasturni to`xtatdingiz.!")
   finally:
       print("Dasturni yangilash uchun to`xtatdingizmi.!")

if __name__ == "__main__":
    asyncio.run(main())
