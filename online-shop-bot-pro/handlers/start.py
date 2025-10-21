from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.reply import main_keyboard
from aiogram.filters import CommandStart
from db import SessionLocal
from db.models import User

router = Router()

class RegisterState(StatesGroup):
    name = State()
    logo = State()
    whatsapp = State()
    telegram = State()

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    session = SessionLocal()
    tg_id = message.from_user.id
    user = session.query(User).filter_by(tg_id=tg_id).first()
    session.close()

    if user:
        await message.answer("✅ Siz ro'yxatdan o'tgansiz!", reply_markup=main_keyboard)
    else:
        await message.answer("👋 Xush kelibsiz! Kompaniya nomini kiriting:")
        await state.set_state(RegisterState.name)
        await state.update_data(tg_id=tg_id)

@router.message(RegisterState.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("2. Kompaniyangiz logotipini yuboring (rasm):")
    await state.set_state(RegisterState.logo)

@router.message(RegisterState.logo, F.photo)
async def get_logo(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("📷 Iltimos, rasm yuboring.")
        return

    file_id = message.photo[-1].file_id
    await state.update_data(logo=file_id)
    await message.answer("3. WhatsApp raqamingizni kiriting:")
    await state.set_state(RegisterState.whatsapp)

@router.message(RegisterState.whatsapp)
async def get_whatsapp(message: Message, state: FSMContext):
    await state.update_data(whatsapp=message.text)
    await message.answer("4. Telegram username yoki raqam:")
    await state.set_state(RegisterState.telegram)

@router.message(RegisterState.telegram)
async def get_telegram(message: Message, state: FSMContext):
    data = await state.update_data(telegram=message.text)
    session = SessionLocal()
    new_user = User(**(await state.get_data()))
    session.add(new_user)
    session.commit()
    session.close()

    await message.answer("🎉 Ro'yxatdan muvaffaqiyatli o'tdingiz!", reply_markup=main_keyboard)
    await state.clear()
