from fastapi import APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import Depends
from fastapi_pagination import Page, add_pagination
from app.models.pagination import PaginationParams
from app.utils import AuthUtils
from app.schemas.product_schema import ProductResponse
from app.services.product_service import ProductService
from typing import Optional
from fastapi import Depends, FastAPI, File, Form, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter(prefix="/products", tags=["Product APIs"])

add_pagination(router)

db_session = Depends(get_db)

@router.get("", response_model=Page[ProductResponse])
async def get_all_products(pagination: PaginationParams = Depends(), db: Session = db_session):
    return ProductService(db).get_all_products(pagination)


@router.get("/{product_id}")
async def get_product(product_id: int, db: Session = db_session):
    return ProductService(db).get_product_by_id(product_id)

@router.post("")
async def create_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    quantity: int = Form(...),
    category_id: int = Form(...),
    image: UploadFile = File(...),
    db: Session = db_session
):
    product_data = {
        "name": name,
        "description": description,
        "price": price,
        "quantity": quantity,
        "category_id": category_id,
        "image": image
    }
    return ProductService(db).create_product(product_data)

@router.put("/{product_id}")
async def update_product(
    product_id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    quantity: Optional[int] = Form(None),
    category_id: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = db_session
):
    product_data = {
        "name": name,
        "description": description,
        "price": price,
        "quantity": quantity,
        "category_id": category_id,
        "image": image
    }
    return ProductService(db).update_product(product_id, product_data)

@router.delete("/{product_id}")
async def delete_product(product_id: int, db: Session = db_session):
    return ProductService(db).delete_product(product_id)

