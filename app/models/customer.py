from app.database import Base
from sqlalchemy import Boolean, Column, Integer, String, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base_entity import BaseEntity
from app.enums.roles import Roles
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid

class UserSession(Base):
    __tablename__ = "sessions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    
    customer = relationship("Customer", back_populates="sessions")

class Customer(BaseEntity, Base):
    __tablename__ = "customers"
    name = Column(String(50), nullable=True)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    mobile = Column(String(11), nullable=True)
    role = Column(Enum(Roles), nullable=False, default=Roles.USER)

    sessions = relationship("UserSession", back_populates="customer", cascade="all, delete-orphan")


