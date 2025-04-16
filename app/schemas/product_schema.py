from typing import Optional
from fastapi import Depends, FastAPI, File, Form, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

class ProductCreateRequest(BaseModel):
    name: str = Form(...),
    description: Optional[str] = Form("Product description"),
    price: float = Form(...),
    quantity: int = Form(...),
    category_id: int = Form(...),
    image: UploadFile = File(...)


class ProductUpdateRequest(BaseModel):
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    quantity: Optional[int] = Form(...),
    category_id: Optional[int] = Form(...),
    image: Optional[UploadFile] = File(...)


class ProductResponse(BaseModel):
    name: str 
    description: str
    price: float
    quantity: int
    category_id: int
    category_name: str
    image: UploadFile