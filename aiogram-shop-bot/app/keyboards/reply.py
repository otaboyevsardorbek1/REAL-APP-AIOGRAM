from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='🎂Магазин'),
            KeyboardButton(text='🎞Новости'),
        ],
        [
            KeyboardButton(text='❓О разработчике')
        ]
    ],
    resize_keyboard=True
)

admin_panel = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Категории'),
            KeyboardButton(text='Товары'),
            KeyboardButton(text='Новости')
        ]
    ],
    resize_keyboard=True
)

admin_category = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Добавить категорию'),
            KeyboardButton(text='Изменить категорию'),
            KeyboardButton(text='Удалить категорию'),
        ]
    ],
    resize_keyboard=True
)

admin_item = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Добавить товар'),
            KeyboardButton(text='Изменить товар'),
            KeyboardButton(text='Удалить товар'),
        ]
    ],
    resize_keyboard=True
)

admin_news = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Добавить новости'),
            KeyboardButton(text='Изменить новости'),
            KeyboardButton(text='Удалить новости'),
        ]
    ],
    resize_keyboard=True
)

change_item_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Название товара'),
            KeyboardButton(text='Описание товара')
        ],
        [
            KeyboardButton(text='Цена товара'),
            KeyboardButton(text='Изображение товара')
        ]
    ],
    resize_keyboard=True
)

change_news_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Название новости'),
            KeyboardButton(text='Описание новости'),
            KeyboardButton(text='Изображение новости')
        ]
    ],
    resize_keyboard=True
)