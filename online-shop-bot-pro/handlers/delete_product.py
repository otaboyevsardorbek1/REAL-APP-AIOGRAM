from aiogram import types
from loader import dp, db
from db.models import Product

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("delete_"))
async def delete_product_callback(call: types.CallbackQuery):
    product_id = int(call.data.split("_")[1])

    product = db.query(Product).filter_by(id=product_id).first()

    if not product:
        return await call.answer("❗️ Mahsulot topilmadi", show_alert=True)

    db.delete(product)
    db.commit()
    await call.message.delete()
    await call.answer("🗑 Mahsulot o‘chirildi")
