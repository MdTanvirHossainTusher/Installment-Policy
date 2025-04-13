import datetime
from app.database import Base
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship, declared_attr
# from sqlalchemy.ext.declarative import declared_attr

class BaseEntity:
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now, server_default=text('now()'))
    created_by = Column(String(255), nullable=False, default="system")
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now, onupdate=datetime.datetime.now, 
        server_default=text('now()'))
    updated_by = Column(String(255), nullable=False, default="system")
    deleted = Column(Boolean, default=False)
