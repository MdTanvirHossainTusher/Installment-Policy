from fastapi import APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import Depends
from fastapi_pagination import Page, add_pagination
from app.schemas.cart_schema import CartItemResponse, CartItemUpdateRequest
from app.schemas.pagination_schema import PaginationParams
from app.schemas.product_schema import ProductResponse
from app.services.product_service import ProductService
from typing import List, Optional
from fastapi import Depends, File, Form, UploadFile

from app.utils import AuthUtils

router = APIRouter(prefix="/carts", tags=["Cart APIs"])

add_pagination(router)
db_session = Depends(get_db)

@router.put("/cart-item/{cart_item_id}")
async def update_cart_item(
    cart_item_id: int,
    cart_item: CartItemUpdateRequest,
    current_user_id: int = Depends(AuthUtils.get_current_user_id),
    db: Session = db_session
):
    return ProductService(db).update_cart_item(cart_item_id, cart_item, current_user_id)


@router.delete("/cart-item/{cart_item_id}")
async def delete_cart_item(
    cart_item_id: int,
    current_user_id: int = Depends(AuthUtils.get_current_user_id),
    db: Session = db_session
):
    return ProductService(db).delete_cart_item(cart_item_id, current_user_id)


@router.get("/items", response_model=Page[CartItemResponse])
async def get_all_carts(
    current_user_id: int = Depends(AuthUtils.get_current_user_id),
    pagination: PaginationParams = Depends(), 
    db: Session = Depends(get_db)
):
    return ProductService(db).get_all_cart_items(current_user_id, pagination)

@router.get("/cart-item/{cart_id}", response_model=CartItemResponse)
async def get_cart(
    cart_id: int,
    current_user_id: int = Depends(AuthUtils.get_current_user_id),
    db: Session = Depends(get_db)
):
    return ProductService(db).get_cart_item_by_id(cart_id, current_user_id)