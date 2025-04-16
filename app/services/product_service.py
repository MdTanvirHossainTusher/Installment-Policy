import uuid
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.enums.roles import Roles
from app.models.product import Category, Product
from fastapi import HTTPException
import logging
from dotenv import load_dotenv
from fastapi_pagination import Page
from app.models.pagination import PaginationParams
from sqlalchemy import desc, asc
from fastapi.security import HTTPBasicCredentials
from starlette import status
from app.schemas.product_schema import ProductResponse
from fastapi import UploadFile, File
import os
import shutil
from uuid import uuid4
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

class ProductService:

    def __init__(self, db: Session):
        self.db = db

    def convert_to_product_response(self, product: Product) -> ProductResponse:
        return ProductResponse(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price,
            quantity=product.quantity,
            category_id=product.category_id,
            category_name=self.db.query(Category).filter(Category.id == product.category_id).first().name,
            image_url=product.image_url
        )
    
    def get_all_products(self, pagination: PaginationParams):
        try:
            query = self.db.query(Product).filter(Product.deleted == False)

            if pagination.sort_by:
                if hasattr(Product, str(pagination.sort_by)):
                    sort_column = getattr(Product, str(pagination.sort_by))
                    if pagination.sort_dir and pagination.sort_dir.lower() == 'desc':
                        query = query.order_by(desc(sort_column))
                    else:
                        query = query.order_by(sort_column)
            else:
                query = query.order_by(asc(Product.id))

            total_items = query.count()
            size = int(pagination.size)
            total_pages = (total_items + size - 1) // size if size > 0 else 0
            page = int(pagination.page)
            query = query.offset((page - 1) * size).limit(size)

            products = query.all()
            product_responses = [self.convert_to_product_response(product) for product in products]

            return Page[ProductResponse](
                items=product_responses,
                total=total_items,
                page=page,
                size=size,
                pages=total_pages,
                has_next=page < total_pages,
                has_previous=page > 1
            )
        except SQLAlchemyError as e:
            logger.error(f"Error fetching products: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching products: {str(e)}")


    def get_product_by_id(self, product_id: int):
        try:
            product = self.db.query(Product).filter(Product.id == product_id, Product.deleted == False).first()
            if product is None:
                raise HTTPException(status_code=400, detail=f"Product with ID: {product_id} does not exist")

            return self.convert_to_product_response(product)

        except SQLAlchemyError as e:
            logger.error(f"Error retrieving product: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving product: {str(e)}"
            )
        
    def save_product_image(self, image_file: UploadFile) -> str:
        UPLOAD_DIR = os.getenv("PRODUCT_IMAGES_DIR", "app/static/uploads")
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        file_extension = os.path.splitext(image_file.filename)[1]
        unique_filename = f"{uuid4()}{file_extension}"

        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image_file.file, buffer)

        return f"{UPLOAD_DIR}/{unique_filename}"


    def create_product(self, product_data: dict):
        try:
            new_product = Product(
                name=product_data["name"],
                description=product_data["description"],
                price=product_data["price"],
                quantity=product_data["quantity"],
                category_id=product_data["category_id"],
                is_available=True
            )
            
            if product_data["image"]:
                image_url = self.save_product_image(product_data["image"])
                new_product.image_url = image_url

            self.db.add(new_product)
            self.db.commit()
            self.db.refresh(new_product)

            return self.convert_to_product_response(new_product)     
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error creating product: {str(e)}"
            )


    def update_product(self, product_id: int, updated_product: dict):
        try:
            product = self.db.query(Product).filter(Product.id == product_id, Product.deleted == False).first()
            if product is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"product with ID: {product_id} does not exist"
                )
            
            if updated_product["name"]: product.name = updated_product["name"]
            if updated_product["description"]: product.description = updated_product["description"]
            if updated_product["price"]: product.price = updated_product["price"]
            if updated_product["quantity"]: product.quantity = updated_product["quantity"]
            if updated_product["category_id"]: product.category_id = updated_product["category_id"]
            if updated_product["image"]:
                image_url = self.save_product_image(updated_product["image"])
                product.image_url = image_url           
            
            self.db.add(product)
            self.db.commit()
            self.db.refresh(product)

            return self.convert_to_product_response(product)

        except SQLAlchemyError as e:
            logger.error(f"Error updating product: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error updating product: {str(e)}"
            )

    def delete_product(self, product_id: int):
        try:
            product = self.db.query(Product).filter(Product.id == product_id, Product.deleted == False).first()
            if product is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"product with ID: {product_id} does not exist"
                )
            product.deleted = True
            self.db.commit()
            self.db.refresh(product)
            return {"message": "Product deleted successfully"}

        except SQLAlchemyError as e:
            logger.error(f"Error deleting product: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting product: {str(e)}"
            )


