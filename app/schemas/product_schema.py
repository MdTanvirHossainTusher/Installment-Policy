from typing import Optional
from fastapi import Depends, FastAPI, File, Form, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

class ProductResponse(BaseModel):
    id: int
    name: str 
    description: str
    price: float
    quantity: int
    category_id: int
    category_name: str
    image_url: str