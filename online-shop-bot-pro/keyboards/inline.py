from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_settings_inline():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("✏️ Ismi", callback_data="edit_name"),
        InlineKeyboardButton("🖼 Logotip", callback_data="edit_logo"),
        InlineKeyboardButton("📞 WhatsApp", callback_data="edit_whatsapp"),
        InlineKeyboardButton("💬 Telegram", callback_data="edit_telegram"),
    )
    return kb

def product_inline_kb(product_id: int):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(text="ℹ️ Batafsil", callback_data=f"detail_{product_id}"),
        InlineKeyboardButton(text="📝 Tahrirlash", callback_data=f"edit_{product_id}"),
        InlineKeyboardButton(text="🗑 O‘chirish", callback_data=f"delete_{product_id}")
    )
    return kb

