from app.database import Base
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.models.base_entity import BaseEntity

class Category(BaseEntity, Base):
    __tablename__ = "categories"
    name = Column(String(255), nullable=False, unique=True)
    products = relationship("Product", back_populates="category")
    

class Product(BaseEntity, Base):
    __tablename__ = "products"

    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    image_url = Column(String(255), nullable=True)
    is_available = Column(Boolean, default=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    category = relationship("Category", back_populates="products", uselist=False)

