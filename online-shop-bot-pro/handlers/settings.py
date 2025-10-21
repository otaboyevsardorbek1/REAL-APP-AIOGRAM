from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.inline import get_settings_inline
from db import SessionLocal
from db.models import User

router = Router()

class UpdateState(StatesGroup):
    name = State()
    logo = State()
    whatsapp = State()
    telegram = State()

@router.message(lambda m: m.text == "⚙️ Sozlamalar")
async def settings_handler(message: types.Message):
    session = SessionLocal()
    tg_id = message.from_user.id
    user = session.query(User).filter_by(tg_id=tg_id).first()

    if not user:
        await message.answer("🚫 Siz hali ro'yxatdan o'tmagansiz. /start buyrug'idan foydalaning.")
        session.close()
        return

    text = (
        f"⚙️ <b>Sozlamalar:</b>\n"
        f"👤 Kompaniya: <code>{user.name}</code>\n"
        f"📷 Logotip: {'✅' if user.logo else '❌'}\n"
        f"📞 WhatsApp: <code>{user.whatsapp or '—'}</code>\n"
        f"💬 Telegram: <code>{user.telegram or '—'}</code>"
    )

    if user.logo:
        await message.answer_photo(user.logo, caption=text, parse_mode="HTML", reply_markup=get_settings_inline())
    else:
        await message.answer(text, parse_mode="HTML", reply_markup=get_settings_inline())
    session.close()

@router.callback_query(lambda c: c.data.startswith("edit_"))
async def inline_edit_handler(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data
    await state.update_data(tg_id=callback.from_user.id)

    if action == "edit_name":
        await callback.message.answer("✏️ Yangi kompaniya nomini kiriting:")
        await state.set_state(UpdateState.name)
    elif action == "edit_logo":
        await callback.message.answer("🖼 Yangi logotip rasmini yuboring:")
        await state.set_state(UpdateState.logo)
    elif action == "edit_whatsapp":
        await callback.message.answer("📞 Yangi WhatsApp raqamingizni kiriting:")
        await state.set_state(UpdateState.whatsapp)
    elif action == "edit_telegram":
        await callback.message.answer("💬 Yangi Telegram username yoki raqamni kiriting:")
        await state.set_state(UpdateState.telegram)

    await callback.answer()

@router.message(UpdateState.name)
async def update_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    session = SessionLocal()
    user = session.query(User).filter_by(tg_id=data["tg_id"]).first()
    user.name = message.text
    session.commit()
    session.close()
    await message.answer("✅ Kompaniya nomi yangilandi.")
    await state.clear()

@router.message(UpdateState.logo)
async def update_logo(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer("📷 Iltimos rasm yuboring.")
        return
    data = await state.get_data()
    session = SessionLocal()
    user = session.query(User).filter_by(tg_id=data["tg_id"]).first()
    user.logo = message.photo[-1].file_id
    session.commit()
    session.close()
    await message.answer("✅ Logotip yangilandi.")
    await state.clear()

@router.message(UpdateState.whatsapp)
async def update_whatsapp(message: types.Message, state: FSMContext):
    data = await state.get_data()
    session = SessionLocal()
    user = session.query(User).filter_by(tg_id=data["tg_id"]).first()
    user.whatsapp = message.text
    session.commit()
    session.close()
    await message.answer("✅ WhatsApp yangilandi.")
    await state.clear()

@router.message(UpdateState.telegram)
async def update_telegram(message: types.Message, state: FSMContext):
    data = await state.get_data()
    session = SessionLocal()
    user = session.query(User).filter_by(tg_id=data["tg_id"]).first()
    user.telegram = message.text
    session.commit()
    session.close()
    await message.answer("✅ Telegram yangilandi.")
    await state.clear()