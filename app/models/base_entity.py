import datetime
from app.database import Base
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql.expression import text


class BaseEntity:
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now, server_default=text('now()'))
    created_by = Column(String(255), nullable=False, default="system")
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now, onupdate=datetime.datetime.now, 
        server_default=text('now()'))
    updated_by = Column(String(255), nullable=False, default="system")
    deleted = Column(Boolean, default=False)
