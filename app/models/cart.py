# from app.database import Base
# from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Float, DateTime, Table, Enum, text, func
# from sqlalchemy.orm import relationship
# import datetime
# import uuid
# from sqlalchemy.ext.declarative import declarative_base
# from app.models.base_entity import BaseEntity


# class Cart(BaseEntity, Base):
#     __tablename__ = "carts"
    
#     customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    
#     customer = relationship("Customer", back_populates="carts")
#     items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")