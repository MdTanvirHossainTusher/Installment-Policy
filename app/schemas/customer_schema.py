from typing import Optional

from pydantic import BaseModel, Field, EmailStr
from pydantic.v1 import root_validator
from app.enums.roles import Roles


class CustomerBase(BaseModel):
    pass

class CustomerCreateRequest(CustomerBase):
    email: EmailStr = Field(..., description='Enter a valid email address')
    password: str = Field(..., min_length=8, description='Password must be at least 8 characters long')


class CustomerUpdateRequest(CustomerBase):
    name: Optional[str] = Field(None, min_length=2, max_length=50, description='Customer name')
    password: Optional[str] = Field(None, min_length=8, description='Customer password')
    mobile: Optional[str] = Field(None, pattern=r'^01[0-9]{9}$', 
                                  description='Customer mobile number (must be 11 digits starting with 01)')


class CustomerResponse(CustomerBase):
    id: int 
    name: Optional[str] = None
    email: str
    mobile: Optional[str] = None
    role: Roles