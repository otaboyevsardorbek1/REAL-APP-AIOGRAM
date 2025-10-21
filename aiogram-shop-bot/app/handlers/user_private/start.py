import logging

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery

from config import BOT_NAME

from app.database.requests import select_item_id, select_news_id
from app.common.filters import ChatTypeFilter
import app.keyboards.reply as rp
import app.keyboards.builder as bd

router_start = Router()
router_start.message.filter(ChatTypeFilter(['private']))

logger = logging.getLogger(__name__)

# СТАРТ
@router_start.callback_query(F.data == 'back_main')
@router_start.message(F.text == '/start')
async def cmd_start(message: Message | CallbackQuery):
    logger.debug(
        f"Пользователь {message.from_user.username} ({message.from_user.id}) - запустил бота"
    )
    if isinstance(message, Message):
        await message.answer(
            f'Ты запустил бота {BOT_NAME}. Выбери действие',
            reply_markup=rp.main
        )
    else:
        await message.answer('')
        await message.message.answer(
            f'Ты запустил бота {BOT_NAME}. Выбери действие',
            reply_markup=rp.main
        )

# МАГАЗИН - КАТЕГОРИИ
@router_start.callback_query(F.data == 'back_shop')
@router_start.message(F.text == '🎂Магазин')
async def cmd_shop(message: Message | CallbackQuery):
    logger.debug(
        f"Пользователь {message.from_user.username} ({message.from_user.id}) - "
        "запустил панель магазина"
    )
    if isinstance(message, Message):
        await message.answer(
            'Вы запустили магазин. Выберите категорию товара',
            reply_markup=await bd.shop_categories()
        )
    else:
        await message.answer('')
        await message.message.answer(
            'Вы запустили магазин. Выберите категорию товара',
            reply_markup=await bd.shop_categories()
        )

# МАГАЗИН - ТОВАРЫ
@router_start.callback_query(F.data.startswith('category_'))
async def cmd_shop_category(callback: CallbackQuery):
    logger.debug(
        f"Пользователь {callback.from_user.username} ({callback.from_user.id}) - выбрал категорию"
    )
    number = int(callback.data.split('_')[-1])
    await callback.answer('')
    await callback.message.answer(
        'Вы выбрали категорию. Выберите товар',
        reply_markup=await bd.shop_items(number)
    )

# МАГАЗИН - ТОВАР
@router_start.callback_query(F.data.startswith('item_'))
async def cmd_shop_item(callback: CallbackQuery):
    logger.debug(
        f"Пользователь {callback.from_user.username} ({callback.from_user.id}) - выбрал осмотр предмета"
    )
    number = int(callback.data.split('_')[-1])
    item = await select_item_id(number)
    await callback.answer('')
    await callback.message.answer_photo(
        photo=item[4],
        caption=f'Название товара: <b>{item[1]}</b>\n'
        f'Описание товара: <b>{item[2]}</b>\n'
        f'Цена товара: <b>{item[3]}</b>'
    )

# НОВОСТИ - ВСЕ
@router_start.message(F.text == '🎞Новости')
async def cmd_news(message: Message):
    logger.debug(
        f"Пользователь {message.from_user.username} ({message.from_user.id}) - выбрал категории новостей"
    )
    await message.answer(
        "Новости бота",
        reply_markup=await bd.select_news()
    )

# НОВОСТИ - ПРОСМОТР
@router_start.callback_query(F.data.startswith('news_'))
async def cmd_news_id(callback: CallbackQuery):
    logger.debug(
        f"Пользователь {callback.from_user.username} ({callback.from_user.id}) - смотрит новости"
    )
    item = await select_news_id(callback.data.split('_')[-1])
    await callback.message.answer_photo(
        photo=item[3],
        caption=f"<b>{item[1]}</b>\n"
        f"{item[2]}"
    )
    
# О РАЗРАБОТЧИКЕ
@router_start.message(F.text == '❓О разработчике')
async def cmd_proger(message: Message):
    await message.answer(
        "Бота написал - @jemkatrst\n"
        "Окружение Visual Code\n"
        "Использовал Python (aiogram3), sqlite3 (aiosqlite)"
    )