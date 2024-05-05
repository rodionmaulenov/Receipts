from datetime import datetime
from decimal import Decimal
from typing import List

from pydantic import BaseModel, condecimal


class UserBase(BaseModel):
    username: str
    login: str


class UserCreate(UserBase):
    password: str


class UserInDB(UserBase):
    id: int
    hashed_password: str

    class Config:
        from_attributes = True


class ProductDisplay(BaseModel):
    name: str
    price: condecimal(decimal_places=2)
    quantity: condecimal(decimal_places=2)
    total: condecimal(decimal_places=2)


class PaymentInfo(BaseModel):
    type: str  # 'cash' or 'cashless'
    amount: condecimal(decimal_places=2)


class ReceiptDisplay(BaseModel):
    id: int
    products: List[ProductDisplay]
    payment: PaymentInfo
    total: Decimal
    rest: Decimal
    created_at: datetime


class ProductInfo(BaseModel):
    name: str
    price: condecimal(decimal_places=2)
    quantity: condecimal(decimal_places=2)


class ReceiptCreate(BaseModel):
    products: List[ProductInfo]
    payment: PaymentInfo


class Token(BaseModel):
    access_token: str
    token_type: str
