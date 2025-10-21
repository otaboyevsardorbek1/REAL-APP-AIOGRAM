# logger.py
import logging
import os
import sys
from aiogram.types import FSInputFile
# from loader import dp
import threading
from datetime import datetime
from typing import Optional
import requests
from logging import StreamHandler, Formatter
from config import config  # sizning global config obyekt
from config import config

class TelegramUploadOnMaxBytesHandler(logging.Handler):
    """
    Faylga yozadi, fayl hajmi max_bytes ga yetganda:
      1) faylni Telegramga sendDocument qilib yuboradi
      2) faylni truncate qiladi (ichini bo'shatadi)
    """
    def __init__(
        self,
        filename: str,
        max_bytes: int,
        bot_token: str,
        chat_id: int,
        caption_prefix: str = "📂 Log fayl maksimal hajmga yetdi",
        timeout: int = 30,
    ):
        super().__init__()
        self.filename = filename
        self.max_bytes = max_bytes
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.caption_prefix = caption_prefix
        self.timeout = timeout

        # Fayl katalogi mavjud bo‘lsin
        folder = os.path.dirname(self.filename)
        if folder:
            os.makedirs(folder, exist_ok=True)

        # Ichki file handler (oddiy append)
        self._file_handler = logging.FileHandler(self.filename, encoding="utf-8")
        self._file_handler.setFormatter(Formatter('%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s:%(lineno)d) - %(message)s'))

        # Thread-safe qilish uchun lock
        self._lock = threading.Lock()

    def emit(self, record: logging.LogRecord) -> None:
        with self._lock:
            try:
                # Avval faylga yozamiz
                self._file_handler.emit(record)
                self._file_handler.flush()

                # Hajmni tekshiramiz
                if os.path.getsize(self.filename) >= self.max_bytes:
                    self._upload_and_truncate()
            except Exception:
                # Handler ichida log yozish rekursiyaga olib kelmasin
                # Shunchaki jim o'tamiz yoki minimal print
                print("TelegramUploadOnMaxBytesHandler: emit() error", file=sys.stderr)

    def _upload_and_truncate(self):
        # Telegramga yuborish
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendDocument"
            caption = f"{self.caption_prefix}\n⏱ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            with open(self.filename, "rb") as f:
                files = {"document": (os.path.basename(self.filename), f)}
                data = {"chat_id": str(self.chat_id), "caption": caption}
                requests.post(url, data=data, files=files, timeout=self.timeout)
        except Exception:
            print("Telegramga log yuborishda xatolik.", file=sys.stderr)
        finally:
            # Faylni tozalaymiz (truncate)
            try:
                with open(self.filename, "w", encoding="utf-8") as wf:
                    wf.truncate(0)
            except Exception:
                print("Log faylni truncate qilishda xatolik.", file=sys.stderr)

    def close(self) -> None:
        try:
            self._file_handler.close()
        finally:
            super().close()


def loggers(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if config.debug else logging.INFO)

    # Duplicate handlerlarni oldini olish
    if logger.hasHandlers():
        return logger

    fmt = '%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s:%(lineno)d) - %(message)s'
    formatter = Formatter(fmt)

    # 1) Faylga yozish + limitga yetganda Telegramga yuborish
    if getattr(config, "log", None) and getattr(config.log, "file", None):
        max_bytes = int(config.log.max_size_mb) * 1024 * 1024
        # chat_id: agar alohida ko‘rsatmoqchi bo‘lsangiz .env ga LOG_TARGET_CHAT_ID qo‘shib qo‘yishingiz mumkin.
        chat_id: Optional[int] = None
        # Sizda adminlar ro‘yxati Settings da bo‘lsa, birinchisini ishlatamiz:
        try:
            # Settings strukturangizga mos ravishda moslang:
            # agar sizda config.admins_id bo'lsa: chat_id = config.admins_id[0]
            # bizda Settings klassida admins_id borligini nazarda tutamiz:
            chat_id = int(config.admins_id[0])  # birinchi admin
        except Exception:
            # Fallback: guruh yoki kanal id ishlatish mumkin
            chat_id = int(config.channel_id) if hasattr(config, "channel_id") else None

        if chat_id is None:
            print("⚠️ Telegramga log yuborish uchun chat_id topilmadi.", file=sys.stderr)
        else:
            tg_handler = TelegramUploadOnMaxBytesHandler(
                filename=config.log.file,
                max_bytes=max_bytes,
                bot_token=config.token,     # bot tokeningiz
                chat_id=chat_id,
                caption_prefix="📂 Log rotate",
                timeout=30,
            )
            tg_handler.setFormatter(formatter)
            logger.addHandler(tg_handler)

    # 2) Konsolga chiqarish (sizning qoidangiz bo‘yicha):
    #    - DEBUG=True bo‘lsa -> konsolga ham yozadi
    #    - DEBUG=False bo‘lsa -> faqat faylga (yuqoridagi handler)
    if config.debug and getattr(config.log, "to_console", True):
        sh = StreamHandler(sys.stdout)
        sh.setFormatter(formatter)
        logger.addHandler(sh)

    return logger

log_admin=loggers(name="Bot-log-send-admins-all-users-data-and-log")

async def check_log_file():
    if os.path.exists(config.log.file):
        file_size_mb = os.path.getsize(config.log.file) / (1024 * 1024)
        if file_size_mb >= config.log.max_size_mb:
            log_file = FSInputFile(config.log.file)
            for chat_id in config.admins_id:
                # Aslida, dp obyektingiz bo‘lsa, shu yerda faylni yuborishingiz mumkin:
                # await dp.bot.send_document(chat_id=chat_id, file=log_file, caption=f"...")
                print(f"📂 `bot.log` hajmi: {file_size_mb:.2f} MB\n📅 Oxirgi yozilgan sana: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nChat ID: {chat_id}")

            with open(config.log.file, "w", encoding="utf-8") as file:
                file.write("")  # Log faylni tozalash

            log_admin.info("✅ Log fayli tozalandi va adminga yuborildi!")
