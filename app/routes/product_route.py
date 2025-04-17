from fastapi import APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import Depends
from fastapi_pagination import Page, add_pagination
from app.schemas.pagination_schema import PaginationParams
from app.schemas.product_schema import ProductResponse
from app.services.product_service import ProductService
from typing import Optional
from fastapi import Depends, File, Form, UploadFile

from app.utils import AuthUtils

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

@router.post("/{product_id}/add-to-cart")
async def add_to_cart(product_id: int, current_user_id: int = Depends(AuthUtils.get_current_user_id), db: Session = db_session):
    return ProductService(db).add_product_to_cart(product_id, current_user_id)

