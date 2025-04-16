from fastapi import APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import Depends
from fastapi_pagination import Page, add_pagination
from app.models.pagination import PaginationParams
from app.utils import AuthUtils
from app.schemas.product_schema import ProductCreateRequest, ProductUpdateRequest, ProductResponse
from app.services.product_service import ProductService

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
async def create_product(customer: ProductCreateRequest, db: Session = db_session):
    return ProductService(db).create_product(customer)


@router.put("/{product_id}")
async def update_product(product_id: int, updated_product: ProductUpdateRequest, db: Session = db_session):
    return ProductService(db).update_product(product_id, updated_product)


@router.delete("/{product_id}")
async def delete_product(product_id: int, db: Session = db_session):
    return ProductService(db).delete_product(product_id)

