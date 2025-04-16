from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from pydantic.v1 import root_validator
from app.enums.roles import Roles
import re


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
    @root_validator
    def validate_mobile(cls, values):
        v = values.get("mobile")
        if v == "":
            raise ValueError("Mobile number can't be empty")
        if v is not None and not re.match(r'^01[0-9]{9}$', v):
            raise ValueError('Mobile number must be 11 digits and start with 01')
        return v
    
class EmailRequest(BaseModel):
    email: EmailStr = Field(..., description='Email address to send OTP to')

class OTPVerificationRequest(BaseModel):
    email: EmailStr = Field(..., description='Email address used for registration')
    otp: str = Field(..., description='One-time password sent to your email')

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description='Email address to login')
    password: str = Field(..., min_length=8, description='User password')


class CustomerResponse(CustomerBase):
    id: int 
    name: Optional[str] = None
    email: str
    mobile: Optional[str] = None
    role: Roles