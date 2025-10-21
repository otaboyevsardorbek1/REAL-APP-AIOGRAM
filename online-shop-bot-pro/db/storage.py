from sqlalchemy.orm import Session
from models import User, Product, ProductImage

def increase_storage(session: Session, product_id: int, size: int):
    product = session.query(Product).filter_by(id=product_id).first()
    if product:
        user = session.query(User).filter_by(tg_id=product.tg_id).first()
        if user:
            user.storage_used += size
            session.commit()

def decrease_storage(session: Session, product_id: int, size: int):
    product = session.query(Product).filter_by(id=product_id).first()
    if product:
        user = session.query(User).filter_by(tg_id=product.tg_id).first()
        if user:
            user.storage_used = max(0, user.storage_used - size)
            session.commit()
