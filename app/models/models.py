from app.database import Base
from sqlalchemy import Boolean, Column, Integer, String, Enum, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from app.models.base_entity import BaseEntity
from app.enums.roles import Roles
from datetime import datetime, timedelta
from sqlalchemy.sql import func
import uuid
from sqlalchemy import func

class Customer(BaseEntity, Base):
    __tablename__ = "customers"
    name = Column(String(50), nullable=True)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    mobile = Column(String(11), nullable=True)
    role = Column(Enum(Roles), nullable=False, default=Roles.USER)
    
    sessions = relationship("UserSession", back_populates="customer", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")
    carts = relationship("Cart", back_populates="customer", cascade="all, delete-orphan")


class UserSession(Base):
    __tablename__ = "sessions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    
    customer = relationship("Customer", back_populates="sessions")

class Category(BaseEntity, Base):
    __tablename__ = "categories"
    name = Column(String(255), nullable=False, unique=True)

    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")


class Product(BaseEntity, Base):
    __tablename__ = "products"
    
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    image_url = Column(String(255), nullable=True)
    is_available = Column(Boolean, default=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    category = relationship("Category", back_populates="products")



class Cart(BaseEntity, Base):
    __tablename__ = "carts"
    
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    
    customer = relationship("Customer", back_populates="carts")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="cart", cascade="all, delete-orphan") # pore add


class CartItem(BaseEntity, Base):
    __tablename__ = "cart_items"
    
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    price = Column(Float, nullable=False)
    paid = Column(Float, nullable=False, default=0.0)
    due = Column(Float, nullable=False, default=0.0)
    cart_item_quantity = Column(Integer, nullable=False, default=1)
    bill = Column(Float, nullable=False, default=0.0)
    next_installment_date = Column(DateTime(timezone=True), nullable=True)
    
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")


class Order(BaseEntity, Base):
    __tablename__ = "orders"
    
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    total_bill = Column(Float, nullable=False, default=0.0)
    total_paid = Column(Float, nullable=False, default=0.0)
    total_due = Column(Float, nullable=False, default=0.0)
    ordered_quantity = Column(Integer, nullable=False, default=1)
    order_date = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    
    customer = relationship("Customer", back_populates="orders")
    cart = relationship("Cart", back_populates="orders") # pore add

