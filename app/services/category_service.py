from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.enums.roles import Roles
from app.models.product import Category
from fastapi import HTTPException
from app.schemas.category_schema import CategoryResponse, CategoryCreateRequest, CategoryUpdateRequest
import logging
from dotenv import load_dotenv
from fastapi_pagination import Page
from app.models.pagination import PaginationParams
from sqlalchemy import desc, asc

logger = logging.getLogger(__name__)

load_dotenv()

class CategoryService:

    def __init__(self, db: Session):
        self.db = db

    def convert_to_category_response(self, category: Category) -> CategoryResponse:
        return CategoryResponse(
            id=category.id,
            name=category.name
        )
        

    def get_all_categories(self, pagination: PaginationParams):
        try:
            query = self.db.query(Category).filter(Category.deleted == False)

            if pagination.sort_by:
                if hasattr(Category, str(pagination.sort_by)):
                    sort_column = getattr(Category, str(pagination.sort_by))
                    if pagination.sort_dir and pagination.sort_dir.lower() == 'desc':
                        query = query.order_by(desc(sort_column))
                    else:
                        query = query.order_by(sort_column)
            else:
                query = query.order_by(asc(Category.id))

            total_items = query.count()
            size = int(pagination.size)
            total_pages = (total_items + size - 1) // size if size > 0 else 0
            page = int(pagination.page)
            query = query.offset((page - 1) * size).limit(size)

            categories = query.all()
            category_responses = [self.convert_to_category_response(category) for category in categories]

            return Page[CategoryResponse](
                items=category_responses,
                total=total_items,
                page=page,
                size=size,
                pages=total_pages,
                has_next=page < total_pages,
                has_previous=page > 1
            )
        except SQLAlchemyError as e:
            logger.error(f"Error fetching categories: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching categories: {str(e)}")


    def get_category_by_id(self, category_id: int):
        try:
            category = self.db.query(Category).filter(Category.id == category_id, Category.deleted == False).first()
            if category is None:
                raise HTTPException(status_code=400, detail=f"Category with ID: {category_id} does not exist")
            return self.convert_to_category_response(category)

        except SQLAlchemyError as e:
            logger.error(f"Error retrieving Category: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving Category: {str(e)}"
            )


    def create_category(self, category: CategoryCreateRequest):
        try:
            input_value = category.name.strip()
            existing_category = self.db.query(Category).filter(Category.name == input_value, Category.deleted == False).first()
            if existing_category:
                raise HTTPException(
                    status_code=400,
                    detail=f"Category with name {existing_category.name} already exists"
                )
            new_category = Category()
                
            new_category.name=input_value
            
            self.db.add(new_category)
            self.db.commit()
            self.db.refresh(new_category)
            return self.convert_to_category_response(new_category)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating Category: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error creating Category: {str(e)}"
            )


    def update_category(self, category_id: int, updated_category: CategoryUpdateRequest):
        try:            
            category = self.db.query(Category).filter(Category.id == category_id, Category.deleted == False).first()
            if category is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Category with ID: {category_id} does not exist"
                )
            
            if updated_category.name is not None: category.name = updated_category.name

            self.db.add(category)
            self.db.commit()
            self.db.refresh(category)

            return self.convert_to_category_response(category)

        except SQLAlchemyError as e:
            logger.error(f"Error updating Category: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error updating Category: {str(e)}"
            )

    def delete_category(self, category_id: int):
        try:
            category = self.db.query(Category).filter(Category.id == category_id, Category.deleted == False).first()
            if category is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Category with ID: {category_id} does not exist"
                )
            category.deleted = True
            self.db.commit()
            self.db.refresh(category)
            return {"message": "Category deleted successfully"}

        except SQLAlchemyError as e:
            logger.error(f"Error deleting Category: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting Category: {str(e)}"
            )
