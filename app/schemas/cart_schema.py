from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from pydantic.v1 import root_validator
from sqlalchemy import DateTime
from app.enums.roles import Roles
import re


class CartBase(BaseModel):
    pass

class CartItemUpdateRequest(CartBase):
    cart_item_quantity: Optional[int] = Field(1, gt=0, description='Quantity of the item in the cart')
    paid_amount: float = Field(..., gt=0, description='Amount paid for the item')
    total_installment: Optional[int] = Field(1, gt=0, description='Total number of installments')


class CartItemResponse(CartBase):
    id: int 
    customer_id: int
    product_id: int
    product_name: str
    product_price: float
    cart_item_quantity: int
    bill: float
    paid_amount: float
    due_amount: float
    next_installment_date: Optional[str] = None
    installment_count: int
    total_installment: int
