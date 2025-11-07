from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from set_webhook_admin import dp, db
from db.models import Product, ProductImage, Characteristic

@dp.message_handler(commands=["my_products"])
async def show_my_products(message: types.Message, state: FSMContext):
    tg_id = message.from_user.id
    products = db.query(Product).filter_by(tg_id=tg_id).all()

    if not products:
        return await message.answer("🛍 Sizda hali mahsulotlar mavjud emas.")

    for product in products:
        text = f"📦 <b>{product.name}</b>\n"
        text += f"💵 Narxi: {product.price} so'm\n"
        text+="______________________________________\n"

        # Tavsiflar
        characteristics = db.query(Characteristic).filter_by(product_id=product.id).all()
        if characteristics:
            text += "🔍 Tavsiflar:\n"
            for c in characteristics:
                text += f"▫️ <b>{c.title}</b>: {c.value}\n"
        # O‘chirish tugmasi
        # delete tugmasi yoniga tahrirlashni qo‘shamiz
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("✏️ Tahrirlash", callback_data=f"edit_{product.id}"),
            InlineKeyboardButton("❌ O‘chirish", callback_data=f"delete_{product.id}")
        )
        # Rasmlar
        images = db.query(ProductImage).filter_by(product_id=product.id).all()
        if images:
            await message.answer_photo(
                photo=images[0].file_id,
                caption=text,
                parse_mode="HTML",
                reply_markup=markup
            )
        else:
            await message.answer(text, parse_mode="HTML", reply_markup=markup)
