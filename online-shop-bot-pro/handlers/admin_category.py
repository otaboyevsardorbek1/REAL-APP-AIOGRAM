# handlers/admin_category.py
from aiogram import types
from aiogram.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loader import dp, db
from db.models import Category
from config import ADMIN_ID


class CategoryStates(StatesGroup):
    waiting_for_name = State()


@dp.message_handler(Command("kategoriya_qoshish"))
async def add_category(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ Sizga ruxsat yo‘q.")
    
    await message.answer("✍️ Yangi kategoriya nomini yuboring:")
    await CategoryStates.waiting_for_name.set()


@dp.message_handler(state=CategoryStates.waiting_for_name)
async def save_category(message: types.Message, state: FSMContext):
    name = message.text.strip()
    existing = db.query(Category).filter_by(name=name).first()

    if existing:
        await message.answer("⚠️ Bu nomli kategoriya allaqachon mavjud.")
    else:
        db.add(Category(name=name))
        db.commit()
        await message.answer(f"✅ Kategoriya qo‘shildi: <b>{name}</b>", parse_mode="HTML")
    
    await state.finish()
