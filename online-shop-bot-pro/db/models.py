# db/models.py
from sqlalchemy import Column, BigInteger, Integer, String, Text, Boolean, ForeignKey, Numeric, TIMESTAMP, UniqueConstraint
from sqlalchemy.orm import relationship
from db import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    tg_id = Column(BigInteger, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    logo = Column(Text)
    whatsapp = Column(String(20))
    telegram = Column(String(100))
    is_active = Column(Boolean, default=True)
    sub_start = Column(TIMESTAMP)
    sub_end = Column(TIMESTAMP)
    storage_used = Column(BigInteger, default=0)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    products = relationship("Product", back_populates="user", cascade="all, delete")


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, ForeignKey("users.tg_id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    icon_url = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint('tg_id', 'name', name='uq_tg_category'),)


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, ForeignKey("users.tg_id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"))
    name = Column(String(100), nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("User", back_populates="products")
    images = relationship("ProductImage", cascade="all, delete")
    characteristics = relationship("Characteristic", cascade="all, delete")


class ProductImage(Base):
    __tablename__ = "product_images"
    id = Column(BigInteger, primary_key=True)
    product_id = Column(BigInteger, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    url = Column(Text, nullable=False)
    size = Column(BigInteger, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


class Characteristic(Base):
    __tablename__ = "characteristics"
    id = Column(BigInteger, primary_key=True)
    product_id = Column(BigInteger, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    character_title = Column(Text, nullable=False)
    character_value = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


class Admin(Base):
    __tablename__ = "admins"
    id = Column(BigInteger, primary_key=True)
    tg_id = Column(BigInteger, unique=True, nullable=False)
