from datetime import datetime

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Numeric)


class Receipt(Base):
    __tablename__ = 'receipts'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    total = Column(Numeric)
    payment_type = Column(String)
    payment_amount = Column(Numeric)
    change_given = Column(Numeric)

    user = relationship("User", back_populates="receipts")
    items = relationship("ReceiptItem", back_populates="receipt")


class ReceiptItem(Base):
    __tablename__ = 'receipt_items'

    id = Column(Integer, primary_key=True, index=True)
    receipt_id = Column(Integer, ForeignKey('receipts.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Numeric)
    total_price = Column(Numeric)

    receipt = relationship("Receipt", back_populates="items")
    product = relationship("Product")


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    login = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    receipts = relationship("Receipt", back_populates="user")
