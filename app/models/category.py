# from app.database import Base
# from sqlalchemy import Boolean, Column, Integer, String
# from sqlalchemy.orm import relationship
# from app.models.base_entity import BaseEntity

# class Category(BaseEntity):
#     __tablename__ = "categories"

#     category_id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(255), nullable=False)
    
#     products = relationship("Product", back_populates="category")