from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from config import config  # <-- bu yerda `config` obyektni chaqiryapmiz
from db import SessionLocal
from looger.loger import loggers,check_log_file

bot = Bot(token=config.token, default=DefaultBotProperties(parse_mode="HTML"))
storage=MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)


# SQLAlchemy sessiyasi
def get_db():
    """SQLAlchemy sessiyasini olish uchun yordamchi funksiya."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
 