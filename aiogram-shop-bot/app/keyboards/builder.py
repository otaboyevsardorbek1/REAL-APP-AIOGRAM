from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.requests import (
    select_category_all,
    select_items_id,
    select_news_all
)


async def shop_categories():
    builder = InlineKeyboardBuilder()
    items = await select_category_all()
    for item in items:
        builder.add(
            InlineKeyboardButton(text=f'{item[1]}', callback_data=f'category_{item[0]}')
        )
    return builder.adjust(2).as_markup()
    
async def shop_items(number: int):
    builder = InlineKeyboardBuilder()
    items = await select_items_id(number)
    for item in items:
        builder.add(
            InlineKeyboardButton(text=f'{item[1]}', callback_data=f'item_{item[0]}')
        )
    builder.add(InlineKeyboardButton(text='Назад', callback_data='back_shop'))
    return builder.adjust(2).as_markup()
    
async def change_category():
    builder = InlineKeyboardBuilder()
    items = await select_category_all()
    for item in items:
        builder.add(
            InlineKeyboardButton(text=f'{item[1]}', callback_data=f'change_category_{item[0]}')
        )
    builder.add(InlineKeyboardButton(text="Отмена", callback_data="callback_back"))
    return builder.adjust(2).as_markup()

async def delete_category():
    builder = InlineKeyboardBuilder()
    items = await select_category_all()
    for item in items:
        builder.add(
            InlineKeyboardButton(text=f'{item[1]}', callback_data=f'delete_category_{item[0]}')
        )
    builder.add(InlineKeyboardButton(text="Отмена", callback_data="callback_back"))
    return builder.adjust(2).as_markup()

async def add_item():
    builder = InlineKeyboardBuilder()
    items = await select_category_all()
    for item in items:
        builder.add(
            InlineKeyboardButton(text=f'{item[1]}', callback_data=f'add_item_{item[0]}')
        )
    builder.add(InlineKeyboardButton(text="Отмена", callback_data="callback_back"))
    return builder.adjust(2).as_markup()

async def change_category():
    builder = InlineKeyboardBuilder()
    items = await select_category_all()
    for item in items:
        builder.add(
            InlineKeyboardButton(text=f'{item[1]}', callback_data=f'change_category_{item[0]}')
        )
    builder.add(InlineKeyboardButton(text="Отмена", callback_data="callback_back"))
    return builder.adjust(2).as_markup()

async def change_item(category: int):
    builder = InlineKeyboardBuilder()
    items = await select_items_id(category)
    for item in items:
        builder.add(
            InlineKeyboardButton(text=f'{item[1]}', callback_data=f'change_item_{item[0]}')
        )
    builder.add(InlineKeyboardButton(text="Отмена", callback_data="callback_back"))
    return builder.adjust(2).as_markup()

async def delete_item_ct():
    builder = InlineKeyboardBuilder()
    items = await select_category_all()
    for item in items:
        builder.add(
            InlineKeyboardButton(text=f'{item[1]}', callback_data=f'delete_item_{item[0]}')
        )
    builder.add(InlineKeyboardButton(text="Отмена", callback_data="callback_back"))
    return builder.adjust(2).as_markup()

async def delete_item_it(category: int):
    builder = InlineKeyboardBuilder()
    items = await select_items_id(category)
    for item in items:
        builder.add(
            InlineKeyboardButton(text=f'{item[1]}', callback_data=f'delete_item_{item[0]}')
        )
    builder.add(InlineKeyboardButton(text="Отмена", callback_data="callback_back"))
    return builder.adjust(2).as_markup()

async def select_news():
    builder = InlineKeyboardBuilder()
    items = await select_news_all()
    for item in items:
        builder.add(
            InlineKeyboardButton(text=f'{item[1]}', callback_data=f'news_{item[0]}')
        )
    return builder.adjust(2).as_markup()

async def change_news():
    builder = InlineKeyboardBuilder()
    items = await select_news_all()
    for item in items:
        builder.add(
            InlineKeyboardButton(text=f'{item[1]}', callback_data=f'change_news_{item[0]}')
        )
    builder.add(InlineKeyboardButton(text='Назад', callback_data='back_main'))
    return builder.adjust(2).as_markup()

async def delete_news_b():
    builder = InlineKeyboardBuilder()
    items = await select_news_all()
    for item in items:
        builder.add(
            InlineKeyboardButton(text=f'{item[1]}', callback_data=f'delete_news_{item[0]}')
        )
    builder.add(InlineKeyboardButton(text='Назад', callback_data='back_main'))
    return builder.adjust(2).as_markup()