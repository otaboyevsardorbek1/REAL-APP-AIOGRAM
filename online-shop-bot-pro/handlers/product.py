# handlers/product.py
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import dp, db
from db.models import Product, Category, ProductImage, Characteristic
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.markdown import hbold
from keyboards.inline import product_inline_kb

class EditProductStates(StatesGroup):
    waiting_for_new_name = State()

class ProductStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_price = State()
    waiting_for_category = State()
    waiting_for_image = State()
    waiting_for_characteristics = State()


@dp.message_handler(Command("mahsulotlar"))
async def list_products(message: types.Message):
    user_id = message.from_user.id
    products = db.query(Product).filter_by(tg_id=user_id).order_by(Product.created_at.desc()).all()

    if not products:
        return await message.answer("❌ Sizda hozircha hech qanday mahsulot yo‘q.")

    for product in products:
        category = db.query(Category).filter_by(id=product.category_id).first()
        image = db.query(ProductImage).filter_by(product_id=product.id).first()
        chars = db.query(Characteristic).filter_by(product_id=product.id).all()

        text = f"<b>{product.name}</b>\n"
        text += f"{hbold('Narx')}: {int(product.price):,} so‘m\n"
        text += f"{hbold('Kategoriya')}: {category.name if category else 'Nomaʼlum'}\n"
        text += f"{hbold('Yaratilgan')}: {product.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
        if chars:
            text += f"{hbold('Tavsiflar')}:\n"
            for char in chars:
                text += f"🔹 {char.key}: {char.value}\n"

        if image:
            await message.answer_photo(photo=image.file_id, caption=text, parse_mode="HTML")
        else:
            await message.answer(text, parse_mode="HTML")
    await message.answer("📦 Mahsulotlar ro'yxati tugadi.")

@dp.callback_query_handler(lambda c: c.data.startswith("delete_"))
async def delete_product_handler(callback_query: types.CallbackQuery):
    product_id = int(callback_query.data.split("_")[1])
    product = db.query(Product).filter_by(id=product_id).first()

    if not product:
        return await callback_query.message.edit_text("❌ Mahsulot topilmadi.")

    db.delete(product)
    db.commit()
    await callback_query.answer("🗑 Mahsulot o‘chirildi.", show_alert=True)
    await callback_query.message.delete()

@dp.callback_query_handler(lambda c: c.data.startswith("edit_"))
async def edit_product_start(callback_query: types.CallbackQuery, state: FSMContext):
    product_id = int(callback_query.data.split("_")[1])
    product = db.query(Product).filter_by(id=product_id).first()

    if not product:
        return await callback_query.message.answer("❌ Mahsulot topilmadi.")

    await state.update_data(product_id=product_id)
    await callback_query.message.answer(f"✏️ Yangi nomini yuboring:\n(Hozirgi: {product.name})")
    await EditProductStates.waiting_for_new_name.set()

@dp.message_handler(state=EditProductStates.waiting_for_new_name)
async def update_product_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    product_id = data.get("product_id")
    product = db.query(Product).filter_by(id=product_id).first()

    if not product:
        await state.finish()
        return await message.answer("❌ Mahsulot topilmadi.")

    product.name = message.text
    db.commit()
    await message.answer("✅ Mahsulot nomi yangilandi.")
    await state.finish()

@dp.callback_query_handler(lambda c: c.data.startswith("detail_"))
async def product_detail_handler(callback_query: types.CallbackQuery):
    product_id = int(callback_query.data.split("_")[1])
    product = db.query(Product).filter_by(id=product_id).first()

    if not product:
        return await callback_query.message.edit_text("❌ Mahsulot topilmadi.")

    category = db.query(Category).filter_by(id=product.category_id).first()
    image = db.query(ProductImage).filter_by(product_id=product.id).first()
    chars = db.query(Characteristic).filter_by(product_id=product.id).all()

    text = f"<b>{product.name}</b>\n"
    text += f"💰 Narxi: {int(product.price):,} so‘m\n"
    text += f"🏷 Kategoriya: {category.name if category else 'Nomaʼlum'}\n"
    text += f"📅 Qo‘shilgan: {product.created_at.strftime('%Y-%m-%d %H:%M')}\n"

    if chars:
        text += "\n🧾 Xarakteristikalar:\n"
        for char in chars:
            text += f"🔹 {char.key}: {char.value}\n"

    await callback_query.answer()
    
    if image:
        await callback_query.message.answer_photo(photo=image.file_id, caption=text, parse_mode="HTML")
    else:
        await callback_query.message.answer(text, parse_mode="HTML")


from datetime import datetime

@dp.message_handler(Command("mahsulot_qoshish"))
async def start_product(message: types.Message, state: FSMContext):
    await message.answer("📦 Mahsulot nomini yuboring:")
    await ProductStates.waiting_for_name.set()

@dp.message_handler(state=ProductStates.waiting_for_name)
async def product_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("💰 Mahsulot narxini yuboring (masalan: 125000):")
    await ProductStates.waiting_for_price.set()

@dp.message_handler(state=ProductStates.waiting_for_price)
async def product_price(message: types.Message, state: FSMContext):
    try:
        price = float(message.text.strip())
    except ValueError:
        return await message.answer("❌ Narx noto‘g‘ri. Son kiriting.")
    
    await state.update_data(price=price)

    categories = db.query(Category).all()
    if not categories:
        return await message.answer("🚫 Hech qanday kategoriya yo‘q. Admin bilan bog‘laning.")

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for cat in categories:
        keyboard.add(KeyboardButton(cat.name))

    await message.answer("🏷 Kategoriya tanlang:", reply_markup=keyboard)
    await ProductStates.waiting_for_category.set()

@dp.message_handler(state=ProductStates.waiting_for_category)
async def product_category(message: types.Message, state: FSMContext):
    category = db.query(Category).filter_by(name=message.text.strip()).first()
    if not category:
        return await message.answer("❌ Noto‘g‘ri kategoriya. Qayta urinib ko‘ring.")

    await state.update_data(category_id=category.id)
    await message.answer("🖼 Endi mahsulot uchun rasm yuboring:", reply_markup=ReplyKeyboardRemove())
    await ProductStates.waiting_for_image.set()

@dp.message_handler(content_types=types.ContentType.PHOTO, state=ProductStates.waiting_for_image)
async def product_image(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await state.update_data(image_file_id=file_id)
    await message.answer("📝 Mahsulot tavsiflarini yuboring:\n\n"
                         "Har bir tavsifni yangi qatorda va <b>kalit:qiymat</b> tarzida yozing.\n\n"
                         "Masalan:\n"
                         "Rang: Qora\nXotira: 128GB\nKafolat: 1 yil", parse_mode="HTML")
    await ProductStates.waiting_for_characteristics.set()

@dp.message_handler(state=ProductStates.waiting_for_characteristics)
async def product_characteristics(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = message.from_user.id

    product = Product(
        tg_id=user_id,
        category_id=data["category_id"],
        name=data["name"],
        price=data["price"],
        created_at=datetime.utcnow()
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    # Save image
    img = ProductImage(product_id=product.id, file_id=data["image_file_id"])
    db.add(img)

    # Parse characteristics
    lines = message.text.strip().split('\n')
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            char = Characteristic(product_id=product.id, key=key.strip(), value=value.strip())
            db.add(char)

    db.commit()

    await message.answer("✅ Mahsulot muvaffaqiyatli saqlandi!")
    await state.finish()
