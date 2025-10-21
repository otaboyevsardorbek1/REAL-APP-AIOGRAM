from aiogram import types, Router
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from db import SessionLocal
from db.models import Category, Product, ProductImage
from keyboards.reply import biznes_keyboard, category_keyboard, back_keyboard, main_keyboard, product_keyboard
from aiogram.fsm.context import FSMContext
from .states import ProductAddState, CategoryAddState, ProductImageState
router = Router()

@router.message(lambda m: m.text == "💼 Biznes")
async def biznes_handler(message: types.Message):
    await message.answer("💼 Biznes bo'limi:", reply_markup=biznes_keyboard)

@router.message(lambda m: m.text == "📂 Kategoriyalar")
async def kategoriyalar_handler(message: types.Message):
    session = SessionLocal()
    tg_id = message.from_user.id
    categories = session.query(Category).filter_by(tg_id=tg_id).all()
    if not categories:
        await message.answer("🗂 Sizda hozircha kategoriyalar mavjud emas.", reply_markup=category_keyboard)
    else:
        text = "📂 Kategoriyalar ro‘yxati:\n\n"
        for cat in categories:
            text += f"🗂 {cat.name}\n"
        await message.answer(text, reply_markup=category_keyboard)
    session.close()

@router.message(lambda m: m.text == "➕ Kategoriya qo‘shish")
async def add_category_handler(message: types.Message, state: FSMContext):
    await message.answer("✏️ Yangi kategoriya nomini kiriting:")
    await state.set_state(CategoryAddState.name)

@router.message(CategoryAddState.name)
async def set_category_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("🖼 Kategoriya uchun emoji yoki rasm URL ni kiriting (ixtiyoriy, o'tkazib yuborish uchun 'yo‘q' deb yozing):")
    await state.set_state(CategoryAddState.icon)

@router.message(CategoryAddState.icon)
async def category_set_icon(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data.get("name")
    icon = None if message.text.lower() == "yo‘q" else message.text
    tg_id = message.from_user.id

    session = SessionLocal()
    exists = session.query(Category).filter_by(tg_id=tg_id, name=name).first()
    if exists:
        await message.answer("⚠️ Bu nomdagi kategoriya allaqachon mavjud.")
    else:
        new_category = Category(tg_id=tg_id, name=name, icon_url=icon)
        session.add(new_category)
        session.commit()
        await message.answer("✅ Kategoriya qo‘shildi.")
    session.close()
    await state.clear()

@router.message(lambda m: m.text == "📦 Tovarlar")
async def products_handler(message: types.Message):
    await message.answer("📦 Mahsulotlar bo‘limi:", reply_markup=product_keyboard)

@router.message(lambda m: m.text == "➕ Tovar qo‘shish")
async def add_product_handler(message: types.Message, state: FSMContext):
    await message.answer("📝 Tovar nomini kiriting:")
    await state.set_state(ProductAddState.name)

@router.message(ProductAddState.name)
async def set_product_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("💰 Tovar narxini kiriting:")
    await state.set_state(ProductAddState.price)

@router.message(ProductAddState.price)
async def set_product_price(message: types.Message, state: FSMContext):
    try:
        price = float(message.text)
        await state.update_data(price=price)
    except:
        await message.answer("❌ Narx noto‘g‘ri. Iltimos, raqam kiriting.")
        return

    session = SessionLocal()
    categories = session.query(Category).filter_by(tg_id=message.from_user.id).all()
    session.close()

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for c in categories:
        kb.add(KeyboardButton(c.name))
    kb.add(KeyboardButton("❌ Bekor qilish"))
    await message.answer("📂 Kategoriya tanlang:", reply_markup=kb)
    await state.set_state(ProductAddState.category)

@router.message(ProductAddState.category)
async def set_product_category(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await message.answer("❌ Bekor qilindi", reply_markup=main_keyboard)
        await state.clear()
        return

    data = await state.get_data()
    name, price = data["name"], data["price"]
    tg_id = message.from_user.id

    session = SessionLocal()
    category = session.query(Category).filter_by(tg_id=tg_id, name=message.text).first()
    if not category:
        await message.answer("❌ Bunday kategoriya mavjud emas.")
        await state.clear()
        return

    product = Product(name=name, price=price, category_id=category.id, tg_id=tg_id)
    session.add(product)
    session.commit()
    session.refresh(product)
    session.close()

    await message.answer(f"✅ Mahsulot qo‘shildi: <b>{name}</b>\nID: <code>{product.id}</code>", parse_mode="HTML", reply_markup=main_keyboard)
    await state.clear()

@router.message(Command("add_image"))
async def upload_product_image_start(message: types.Message, state: FSMContext):
    await message.answer("🆔 Mahsulot ID raqamini kiriting:")
    await state.set_state(ProductImageState.product_id)
    
@router.message(ProductImageState.product_id)
async def get_product_id(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Raqam kiriting.")
        return
    await state.update_data(product_id=int(message.text))
    await message.answer("📷 Endi rasmni yuboring:")
    await state.set_state(ProductImageState.image)

@router.message(ProductImageState.image)
async def upload_product_image(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer("❌ Iltimos, rasm yuboring.")
        return

    data = await state.get_data()
    product_id = data["product_id"]
    photo = message.photo[-1].file_id

    session = SessionLocal()
    product = session.query(Product).filter_by(id=product_id).first()
    if not product:
        await message.answer("❌ Mahsulot topilmadi.")
        session.close()
        await state.clear()
        return

    image = ProductImage(product_id=product_id, file_id=photo)
    session.add(image)
    session.commit()
    session.close()

    await message.answer("✅ Rasm saqlandi.", reply_markup=main_keyboard)
    await state.clear()

@router.message(lambda m: m.text == "⬅️ Orqaga")
async def back_handler(message: types.Message):
    await message.answer("🔙 Asosiy menyuga qaytdingiz.", reply_markup=main_keyboard)