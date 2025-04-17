from fastapi import APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import Depends
from fastapi_pagination import Page, add_pagination
from app.schemas.cart_schema import CartItemUpdateRequest
from app.schemas.pagination_schema import PaginationParams
from app.schemas.product_schema import ProductResponse
from app.services.product_service import ProductService
from typing import Optional
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