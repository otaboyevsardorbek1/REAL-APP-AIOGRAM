# handlers/add_product.py
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
# from states import ProductState
from db.models import Product, Category, ProductImage, Characteristic
from loader import db  # db: SQLAlchemy session

router = Router()

class ProductState(StatesGroup):
    waiting_for_name = State()
    waiting_for_price = State()
    waiting_for_category = State()
    waiting_for_image = State()
    waiting_for_characteristics = State()

@router.message(Command("add"))
async def start_add_product(message: types.Message, state: FSMContext):
    await message.answer("📝 Mahsulot nomini kiriting:")
    await state.set_state(ProductState.waiting_for_name)

@router.message(ProductState.waiting_for_name)
async def set_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("💰 Narxni kiriting (masalan: 14999.99):")
    await state.set_state(ProductState.waiting_for_price)

@router.message(ProductState.waiting_for_price)
async def set_price(message: types.Message, state: FSMContext):
    try:
        price = float(message.text)
        await state.update_data(price=price)
    except ValueError:
        return await message.answer("❌ Iltimos, to‘g‘ri raqam kiriting.")
    
    # Kategoriya tugmalari
    categories = db.query(Category).all()
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for cat in categories:
        keyboard.add(KeyboardButton(cat.name))
    keyboard.add(KeyboardButton("➕ Yangi kategoriya qo‘shish"))

    await message.answer("🏷 Kategoriyani tanlang yoki yangi yarating:", reply_markup=keyboard)
    await state.set_state(ProductState.waiting_for_category)

@router.message(ProductState.waiting_for_category)
async def set_category(message: types.Message, state: FSMContext):
    category_name = message.text.strip()
    category = db.query(Category).filter_by(name=category_name).first()

    if not category:
        category = Category(name=category_name)
        db.add(category)
        db.commit()

    await state.update_data(category_id=category.id)
    await message.answer("📸 Mahsulot rasmi(ni) yuboring:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(ProductState.waiting_for_image)

@router.message(F.photo, ProductState.waiting_for_image)
async def set_image(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo_id=photo_id)
    await message.answer("🔤 Mahsulot tavsiflarini kiriting (masalan: Rang: Qora):")
    await state.set_state(ProductState.waiting_for_characteristics)

@router.message(ProductState.waiting_for_characteristics)
async def set_characteristics(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    tg_id = message.from_user.id

    # Mahsulot
    product = Product(
        tg_id=tg_id,
        name=user_data["name"],
        price=user_data["price"],
        category_id=user_data["category_id"]
    )
    db.add(product)
    db.commit()

    # Rasm
    db.add(ProductImage(product_id=product.id, file_id=user_data["photo_id"]))

    # Tavsif
    if ":" in message.text:
        key, value = message.text.split(":", 1)
        db.add(Characteristic(product_id=product.id, title=key.strip(), value=value.strip()))

    db.commit()
    await message.answer("✅ Mahsulot muvaffaqiyatli qo‘shildi!")
    await state.clear()
