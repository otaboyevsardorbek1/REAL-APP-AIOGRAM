import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import TOKEN
from app.database.models import create_table
from app.common.middlewares import UserMiddleware

from app.handlers.user_private.start import router_start
from app.handlers.admin_private.admin import router_admin
from app.handlers.admin_private.category import router_category
from app.handlers.admin_private.item import router_item
from app.handlers.admin_private.news import router_news

logger = logging.getLogger(__name__)


async def main() -> None:
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] #%(levelname)-8s %(filename)s:%(lineno)d - %(name)s - %(message)s'
    )
    logger.info('Бот запустился')
    
    # Инициализируем бот и диспетчер
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    
    # Запуск базы данных
    await create_table()
    
    # Регистриуем роутеры
    logger.info('Подключаем роутеры')
    dp.include_router(router_start)
    dp.include_router(router_admin)
    dp.include_router(router_category)
    dp.include_router(router_item)
    dp.include_router(router_news)
    
    # Регистрируем миддлвари
    logger.info('Подключаем миддлвари')
    dp.update.outer_middleware(UserMiddleware())
    
    # Пропускаем накопившиеся апдейты и запускаем polling
    await dp.start_polling(bot)
    await bot.delete_webhook(True)
    
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    