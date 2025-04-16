from fastapi import APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import Depends
from app.schemas.category_schema import CategoryCreateRequest, CategoryUpdateRequest, CategoryResponse
from app.services.category_service import CategoryService
from fastapi_pagination import Page, add_pagination
from app.schemas.pagination_schema import PaginationParams
from app.utils import AuthUtils

router = APIRouter(prefix="/categories", tags=["Category APIs"])

add_pagination(router)

db_session = Depends(get_db)

@router.get("", response_model=Page[CategoryResponse])
async def get_all_categories(pagination: PaginationParams = Depends(), db: Session = db_session):
    return CategoryService(db).get_all_categories(pagination)


@router.get("/{category_id}")
async def get_category(category_id: int, db: Session = db_session):
    return CategoryService(db).get_category_by_id(category_id)

@router.post("")
async def create_category(category: CategoryCreateRequest, db: Session = db_session):
    return CategoryService(db).create_category(category)

@router.put("/{category_id}")
async def update_category(category_id: int, updated_category: CategoryUpdateRequest, db: Session = db_session):
    return CategoryService(db).update_category(category_id, updated_category)


@router.delete("/{category_id}")
async def delete_category(category_id: int, db: Session = db_session):
    return CategoryService(db).delete_category(category_id)

