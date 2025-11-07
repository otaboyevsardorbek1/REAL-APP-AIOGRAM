from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Text 
from sqlalchemy.sql import expression
from db import Base
from sqlalchemy.dialects.sqlite import DATETIME

class OrderLink(Base):
    __tablename__ = "Order_referral_links"
    id = Column(Integer, primary_key=True, index=True)
    unique_key = Column(String(128), unique=True, nullable=False, index=True)
    product_id = Column(String(64), nullable=True)
    order_log_id = Column(String(64), nullable=True)
    created_by = Column(String(64), nullable=True)
    is_used = Column(Boolean, server_default=expression.false(), default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    used_at = Column(DateTime, nullable=True)
    meta = Column(Text, nullable=True)  # optional JSON metadata
