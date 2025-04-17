from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.enums.roles import Roles
from app.models.models import Cart, CartItem, Customer, Product, Category
from fastapi import HTTPException
import logging
from dotenv import load_dotenv
from fastapi_pagination import Page
from app.schemas.cart_schema import CartItemResponse, CartItemUpdateRequest
from app.schemas.pagination_schema import PaginationParams
from sqlalchemy import desc, asc
from app.schemas.product_schema import ProductResponse
from fastapi import UploadFile
import os
import shutil
from uuid import uuid4
from dotenv import load_dotenv
from datetime import datetime, timedelta

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

    def add_product_to_cart(self, product_id: int, customer_id: int):
        try:
            product = self.db.query(Product).filter(Product.id == product_id, Product.deleted == False).first()
            if product is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Product with ID: {product_id} does not exist"
                )
            existing_product = self.db.query(CartItem)\
                .join(Cart, CartItem.cart_id == Cart.id)\
                .filter(
                    CartItem.product_id == product_id, 
                    CartItem.deleted == False, 
                    Cart.customer_id == customer_id
                ).first()

            if existing_product:
                raise HTTPException(
                    status_code=400,
                    detail=f"Product with ID: {product_id} already exists in the cart of customer ID: {customer_id}"
                )
            
            cart = self.db.query(Cart).filter(Cart.customer_id == customer_id, Cart.deleted == False).first()

            if cart is None:
                new_cart = Cart(customer_id=customer_id)
                self.db.add(new_cart)
                self.db.commit()
                self.db.refresh(new_cart)
            else:
                new_cart = cart
            
            cart_item = CartItem(
                cart_id=new_cart.id, 
                product_id=product.id,
                price=product.price,
                paid=product.price*1,
                due=0.0,
                cart_item_quantity=1,
                bill=product.price,
                next_installment_date=None,
                isntallment_count=0,
                total_installment=1,
                created_by=self.db.query(Customer).filter(Customer.id == customer_id).first().name,
                updated_by=self.db.query(Customer).filter(Customer.id == customer_id).first().name
            )
            
            self.db.add(cart_item)
            self.db.commit()
            self.db.refresh(cart_item)

            return CartItemResponse(
                id=cart_item.id,
                customer_id=customer_id,
                product_id=product.id,
                product_price=product.price,
                cart_item_quantity=cart_item.cart_item_quantity,
                bill=cart_item.bill,
                paid_amount=cart_item.paid,
                due_amount=cart_item.due,
                next_installment_date=str(cart_item.next_installment_date),
                installment_count=cart_item.isntallment_count,
                total_installment=cart_item.total_installment
            );

        except SQLAlchemyError as e:
            logger.error(f"Error adding product to cart: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error adding product to cart: {str(e)}"
            )
        

    def update_cart_item(self, cart_item_id: int, updated_cart_item: CartItemUpdateRequest, customer_id: int):
        try:
            cart_item = self.db.query(CartItem).filter(CartItem.id == cart_item_id, CartItem.deleted == False).first()
            if cart_item is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cart item with ID: {cart_item_id} does not exist"
                )
            
            cart = self.db.query(Cart).filter(Cart.id == cart_item.cart_id).first()
            if cart.customer_id != customer_id:
                raise HTTPException(
                    status_code=403,
                    detail="You do not have permission to update this cart item"
                )

            is_first_installment = cart_item.isntallment_count == 0
            
            has_total_installment_field = 'total_installment' in updated_cart_item.model_fields_set
            
            if has_total_installment_field:
                if not is_first_installment:
                    raise HTTPException(
                        status_code=400,
                        detail="You cannot update the total installment after first installment"
                    )
                cart_item.total_installment = updated_cart_item.total_installment
            
            has_quantity_field = 'cart_item_quantity' in updated_cart_item.model_fields_set
            
            if has_quantity_field:
                if not is_first_installment:
                    raise HTTPException(
                        status_code=400,
                        detail="You cannot update the quantity of the product after first installment"
                    )
                cart_item.cart_item_quantity = updated_cart_item.cart_item_quantity
            
            total_price = cart_item.price * cart_item.cart_item_quantity
            
            min_payment_per_installment = total_price / cart_item.total_installment
            
            if updated_cart_item.paid_amount < min_payment_per_installment:
                raise HTTPException(
                    status_code=400,
                    detail=f"You must pay at least {min_payment_per_installment} of the total product price"
                )
            
            if updated_cart_item.paid_amount > total_price:
                raise HTTPException(
                    status_code=400,
                    detail="Paid amount cannot be greater than the total product price"
                )
            
            if cart_item.isntallment_count == cart_item.total_installment:
                raise HTTPException(
                    status_code=400,
                    detail="You have already completed all installments for this product. Thank you!"
                )
            
            if is_first_installment:
                cart_item.paid = updated_cart_item.paid_amount
            else:
                cart_item.paid = cart_item.paid + updated_cart_item.paid_amount
            
            cart_item.bill = total_price
            cart_item.due = cart_item.bill - cart_item.paid
            
            next_date = datetime.now() + timedelta(days=30)
            cart_item.next_installment_date = next_date
            
            cart_item.isntallment_count += 1
            
            self.db.add(cart_item)
            self.db.commit()
            self.db.refresh(cart_item)
            
            print(f"Date set: {next_date}, Retrieved date: {cart_item.next_installment_date}")
            
            return CartItemResponse(
                id=cart_item.id,
                customer_id=customer_id,
                product_id=cart_item.product_id,
                product_price=cart_item.price,
                cart_item_quantity=cart_item.cart_item_quantity,
                bill=cart_item.bill,
                paid_amount=cart_item.paid,
                due_amount=cart_item.due,
                next_installment_date=str(cart_item.next_installment_date),
                installment_count=cart_item.isntallment_count,
                total_installment=cart_item.total_installment
            )
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating cart item: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error updating cart item: {str(e)}"
            )
        

        
    def delete_cart_item(self, cart_item_id: int, customer_id: int):
        try:
            cart_item = self.db.query(CartItem).filter(CartItem.id == cart_item_id, CartItem.deleted == False).first()
            if cart_item is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cart item with ID: {cart_item_id} does not exist"
                )
            
            cart = self.db.query(Cart).filter(Cart.id == cart_item.cart_id).first()
            if cart.customer_id != customer_id:
                raise HTTPException(
                    status_code=403,
                    detail="You do not have permission to delete this cart item"
                )
            if cart_item.due > 0:
                raise HTTPException(
                    status_code=400,
                    detail="You cannot delete a cart item with due amount"
                )
            
            cart_item.deleted = True
            self.db.commit()
            self.db.refresh(cart_item)

            existing_product = self.db.query(CartItem)\
                .join(Cart, CartItem.cart_id == Cart.id)\
                .filter(
                    CartItem.deleted == False, 
                    Cart.customer_id == customer_id
                ).first()
            
            if not existing_product:
                cart.deleted = True
                self.db.commit()
                self.db.refresh(cart)

            return {"message": "Cart item deleted successfully"}

        except SQLAlchemyError as e:
            logger.error(f"Error deleting cart item: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting cart item: {str(e)}"
            )

