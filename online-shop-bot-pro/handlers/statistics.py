from aiogram import types
from aiogram.filters import Command
from main import dp, db
from db.models import Product, Category
from sqlalchemy import func

@dp.message_handler(Command("statistika"))
async def user_statistics(message: types.Message):
    tg_id = message.from_user.id

    # Mahsulotlar soni
    total_count = db.query(Product).filter_by(tg_id=tg_id).count()

    # Umumiy narx yig‘indisi
    total_price = db.query(func.sum(Product.price)).filter_by(tg_id=tg_id).scalar() or 0

    # So‘nggi mahsulot
    last_product = (
        db.query(Product)
        .filter_by(tg_id=tg_id)
        .order_by(Product.created_at.desc())
        .first()
    )

    # Javob tayyorlash
    text = f"📊 <b>Statistika</b>\n\n"
    text += f"📦 Mahsulotlar soni: <b>{total_count}</b>\n"
    text += f"💰 Umumiy qiymati: <b>{total_price:.2f}</b>\n"

    if last_product:
        text += f"\n🕒 So‘nggi mahsulot:\n"
        text += f"📝 Nomi: {last_product.name}\n"
        text += f"💵 Narxi: {last_product.price}\n"
        text += f"📅 Qo‘shilgan: {last_product.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"

    await message.answer(text, parse_mode="HTML")
