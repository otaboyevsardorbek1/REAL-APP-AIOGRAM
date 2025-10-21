from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Asosiy tugmalar
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="💼 Biznes"),
            KeyboardButton(text="⚙️ Sozlamalar")
        ]
    ],
    resize_keyboard=True
)

# Biznes bo‘limi
biznes_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📂 Kategoriyalar"),
            KeyboardButton(text="📦 Tovarlar")
        ],
        [
            KeyboardButton(text="⬅️ Orqaga")
        ]
    ],
    resize_keyboard=True
)

# Kategoriya menyusi
category_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="➕ Qo‘shish"),
            KeyboardButton(text="📄 Bce")
        ],
        [
            KeyboardButton(text="⬅️ Orqaga")
        ]
    ],
    resize_keyboard=True
)

# Orqaga tugmasi
back_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="⬅️ Orqaga")
        ]
    ],
    resize_keyboard=True
)

# Sozlamalar menyusi
settings_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="✏️ Ismi"),
            KeyboardButton(text="🖼 Logotip")
        ],
        [
            KeyboardButton(text="📞 WhatsApp"),
            KeyboardButton(text="💬 Telegram")
        ],
        [
            KeyboardButton(text="⬅️ Orqaga")
        ]
    ],
    resize_keyboard=True
)

# Tovarlar menyusi
product_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="➕ Tovar qo‘shish"),
            KeyboardButton(text="📋 Mahsulotlar")
        ],
        [
            KeyboardButton(text="⬅️ Orqaga")
        ]
    ],
    resize_keyboard=True
)
