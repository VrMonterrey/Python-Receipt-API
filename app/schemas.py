from pydantic import BaseModel
from typing import List, Literal, Optional
from datetime import datetime


class UserCreate(BaseModel):
    """
    Schema for creating a new user.
    \n- `username`: The desired username of the user.
    \n- `password`: The desired password for the user account.
    """
    username: str
    password: str


class UserOut(BaseModel):
    """
    Schema for outputting user details.
    \n- `id`: The unique identifier of the user.
    \n- `username`: The username of the user.
    """
    id: int
    username: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    """
    Schema for returning JWT token data.
    \n- `access_token`: The JWT access token for authentication.
    \n- `refresh_token`: The JWT refresh token for refreshing the session.
    \n- `token_type`: The type of token.
    """
    access_token: str
    refresh_token: str
    token_type: str


class ProductBase(BaseModel):
    """
    Base schema for a product.
    \n- `name`: The name of the product.
    \n- `price`: The price of a single unit of the product.
    """
    name: str
    price: float


class ProductCreate(ProductBase):
    """
    Schema for creating a product in a receipt.
    \n- `quantity`: The quantity of the product purchased.
    """
    quantity: int


class ProductOut(ProductBase):
    """
    Schema for outputting product details in a receipt.
    \n- `total`: The total cost for this product (price * quantity).
    """
    total: float


class Payment(BaseModel):
    """
    Schema for payment information.
    \n- `type`: The type of payment (cash or cashless).
    \n- `amount`: The total amount paid.
    """
    type: Literal["cash", "cashless"]
    amount: float


class ReceiptCreate(BaseModel):
    """
    Schema for creating a new receipt.
    \n- `products`: A list of products being purchased, including their name, price, and quantity.
    \n- `payment`: Information about the payment, including type and amount.
    """
    products: List[ProductCreate]
    payment: Payment


class ReceiptOut(BaseModel):
    """
    Schema for outputting receipt details.
    \n- `id`: The unique identifier of the receipt.
    \n- `products`: A list of products in the receipt, with total cost for each.
    \n- `total`: The total cost for all products in the receipt.
    \n- `rest`: The change to be given back to the customer.
    \n- `created_at`: The timestamp when the receipt was created.
    \n- `payment`: Information about the payment, including type and amount.
    """
    id: int
    products: List[ProductOut]
    total: float
    rest: float
    created_at: datetime
    payment: Payment


class ReceiptFilter(BaseModel):
    """
    Schema for filtering receipts.
    \n- `start_date`: Filter for receipts created after this date.
    \n- `end_date`: Filter for receipts created before this date.
    \n- `min_total`: Filter for receipts with a total amount greater than or equal to this value.
    \n- `payment_type`: Filter for receipts by payment type (cash or cashless).
    \n- `skip`: The number of records to skip for pagination.
    \n- `limit`: The maximum number of records to return.
    """
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_total: Optional[float] = None
    payment_type: Optional[Literal["cash", "cashless"]] = None
    skip: Optional[int] = 0
    limit: Optional[int] = 10