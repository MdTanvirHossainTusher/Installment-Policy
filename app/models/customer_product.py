# from app.database import Base
# from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Float, DateTime, Table, Enum, text, func
# from sqlalchemy.orm import relationship
# import datetime
# import uuid
# from sqlalchemy.ext.declarative import declarative_base
# from app.models.base_entity import BaseEntity

# class Order(BaseEntity, Base):
#     __tablename__ = "orders"
    
#     id = None

#     customer_id = Column(Integer, ForeignKey("customers.id"), primary_key=True)
#     product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    
#     paid = Column(Float, nullable=False, default=0.0)
#     due = Column(Float, nullable=False, default=0.0)
#     total_quantity = Column(Integer, nullable=False, default=1)
#     buying_date = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now)

#     customer = relationship("Customer", back_populates="orders")
#     product = relationship("Product", back_populates="orders")
#     # carts = relationship("CartItem", back_populates="customer_product")


# class Cart(BaseEntity, Base):
#     __tablename__ = "carts"
    
#     customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    
#     customer = relationship("Customer", back_populates="carts")
#     items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")


# class CartItem(Base):
#     __tablename__ = "cart_items"
    
#     id = Column(Integer, primary_key=True, index=True)
#     cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
#     product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
#     quantity = Column(Integer, nullable=False, default=1)
    
#     cart = relationship("Cart", back_populates="items")
#     product = relationship("Product")