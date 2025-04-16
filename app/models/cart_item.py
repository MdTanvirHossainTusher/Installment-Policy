# from app.database import Base
# from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Float, DateTime, Table, Enum, text, func
# from sqlalchemy.orm import relationship
# import datetime
# import uuid
# from sqlalchemy.ext.declarative import declarative_base
# from app.models.base_entity import BaseEntity

# class CartItem(Base):
#     __tablename__ = "cart_items"
    
#     id = Column(Integer, primary_key=True, index=True)
#     cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
#     product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
#     quantity = Column(Integer, nullable=False, default=1)
    
#     cart = relationship("Cart", back_populates="items")
#     product = relationship("Product")