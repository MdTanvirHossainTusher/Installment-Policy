from app.database import Base
from sqlalchemy import Boolean, Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from app.models.base_entity import BaseEntity
from app.enums.roles import Roles

class Customer(BaseEntity, Base):
    __tablename__ = "customers"
    name = Column(String(50), nullable=True)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    mobile = Column(String(11), nullable=True)
    role = Column(Enum(Roles), nullable=False, default=Roles.USER)


