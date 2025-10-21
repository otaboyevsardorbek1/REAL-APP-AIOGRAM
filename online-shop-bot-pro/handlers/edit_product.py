from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from loader import dp, db
from db.models import Product,Characteristic

# --- STATES ---
class EditProduct(StatesGroup):
    waiting_for_field = State()
    waiting_for_new_value = State()

# Boshlanish: Tahrirlash menyusi
@dp.callback_query_handler(lambda c: c.data and c.data.startswith("edit_"))
async def edit_product_menu(call: types.CallbackQuery, state: FSMContext):
    product_id = int(call.data.split("_")[1])
    await state.update_data(product_id=product_id)

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("✏️ Nomi", callback_data="edit_name"),
        InlineKeyboardButton("💰 Narxi", callback_data="edit_price"),
        InlineKeyboardButton("🔍 Tavsiflari", callback_data="edit_characteristics"),
    )
    await call.message.answer("Qaysi qismni tahrirlashni xohlaysiz?", reply_markup=markup)
    await call.answer()
    await EditProduct.waiting_for_field.set()

# Maydon tanlanganida
@dp.callback_query_handler(state=EditProduct.waiting_for_field)
async def ask_new_value(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(field=call.data)
    if call.data == "edit_characteristics":
        await call.message.answer("Yangi tavsiflarni kiriting (kalit:qiymat shaklida):")
    elif call.data == "edit_price":
        await call.message.answer("Yangi narxni kiriting:")
    elif call.data == "edit_name":
        await call.message.answer("Yangi nomni kiriting:")
    await call.answer()
    await EditProduct.waiting_for_new_value.set()

# Yangi qiymat qabul qilish
@dp.message_handler(state=EditProduct.waiting_for_new_value)
async def save_new_value(message: types.Message, state: FSMContext):
    data = await state.get_data()
    product = db.query(Product).filter_by(id=data["product_id"]).first()

    if data["field"] == "edit_name":
        product.name = message.text
    elif data["field"] == "edit_price":
        try:
            product.price = float(message.text)
        except ValueError:
            return await message.answer("❗️ Narx noto‘g‘ri formatda. Raqam kiriting.")
    elif data["field"] == "edit_characteristics":
        # Avvalgi tavsiflarni o‘chirish
        product.characteristics.clear()
        db.commit()
        for line in message.text.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                product.characteristics.append(
                    Characteristic(title=key.strip(), value=value.strip())
                )

    db.commit()
    await message.answer("✅ Mahsulot muvaffaqiyatli tahrirlandi.")
    await state.finish()
