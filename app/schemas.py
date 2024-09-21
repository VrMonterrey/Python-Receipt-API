from pydantic import BaseModel
from typing import List, Literal, Optional
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class ProductBase(BaseModel):
    name: str
    price: float


class ProductCreate(ProductBase):
    quantity: int


class ProductOut(ProductBase):
    total: float


class Payment(BaseModel):
    type: Literal["cash", "cashless"]
    amount: float


class ReceiptCreate(BaseModel):
    products: List[ProductCreate]
    payment: Payment


class ReceiptOut(BaseModel):
    id: int
    products: List[ProductOut]
    total: float
    rest: float
    created_at: datetime
    payment: Payment


class ReceiptFilter(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_total: Optional[float] = None
    payment_type: Optional[Literal["cash", "cashless"]] = None
    skip: Optional[int] = 0
    limit: Optional[int] = 10
