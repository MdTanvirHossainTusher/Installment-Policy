from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from pydantic.v1 import root_validator
from sqlalchemy import DateTime
from app.enums.roles import Roles
import re


class CartBase(BaseModel):
    pass

class CartItemUpdateRequest(CartBase):
    cart_item_quantity: int = Field(..., gt=0, description='Quantity of the item in the cart')
    paid_amount: float = Field(..., gt=0, description='Amount paid for the item')
    # due_amount: float = Field(..., gt=0, description='Amount due for the item')

class CartItemResponse(CartBase):
    id: int 
    customer_id: int
    product_id: int
    product_price: float
    cart_item_quantity: int
    bill: float
    paid_amount: float
    due_amount: float
    next_installment_date: Optional[str] = None
    # created_by: str
    # updated_by: Optional[str] = None