from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

import uuid
from datetime import datetime

from src.lib.config import config

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    __table_args__ = {"schema": config.db_schema}

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def as_dict(self, include: list[str] = None, exclude: list[str] = None):
        as_dict = {}
        columns: list[Table] = self.__table__.columns

        if include:
            for column in columns:
                if column.name in include:
                    as_dict[column.name] = getattr(self, column.name)
        elif exclude:
            for column in columns:
                if column.name not in exclude:
                    as_dict[column.name] = getattr(self, column.name)
        else:
            for column in columns:
                as_dict[column.name] = getattr(self, column.name)

        return as_dict

class User(BaseModel):
    __tablename__ = "user"

    name = Column(String, index=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    role = Column(String, nullable=False, default="viewer")

    items = relationship("Item", back_populates="owner")

class Item(BaseModel):
    __tablename__ = "item"

    title = Column(String, index=True)

    price = Column(DECIMAL, index=True, nullable=False, default=0.0)
    dimention = Column(String, index=True, nullable=False)
    single_piece = Column(Integer, index=True, nullable=False, default=0.0)

    additional = Column(String)
    
    description = Column(String, index=True)
    owner_id = Column(ForeignKey(User.id), nullable=False)

    owner = relationship("User", back_populates="items")