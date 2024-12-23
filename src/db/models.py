from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Numeric, text, DDL, event
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from src.lib.config import config

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    __table_args__ = {"schema": config.db_schema}
    

    id = Column(UUID, primary_key=True, index=True, server_default=text("uuid_generate_v4()"))
    created_at = Column(DateTime, server_default=text("now()"))
    updated_at = Column(DateTime, server_default=text("now()"))

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


class ItemBase(BaseModel):
    __abstract__ = True

    name = Column(String, index=True)
    description = Column(String, index=True)

    
class User(BaseModel):
    __tablename__ = "user"

    name = Column(String, index=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    role = Column(String, nullable=False, default="viewer")

class Category(ItemBase):
    __tablename__ = "category"

    items = relationship("Item", back_populates="category", cascade="all, delete-orphan")

class Item(ItemBase):
    __tablename__ = "item"

    price = Column(Numeric, nullable=False)
    category_id = Column(ForeignKey(Category.id), nullable=False)

    category = relationship("Category", back_populates="items")
    characteristics = relationship("Characteristic", back_populates="items", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="items", cascade="all, delete-orphan")

class Characteristic(ItemBase):
    __tablename__ = "characteristic"

    value = Column(String, nullable=False)
    item_id = Column(ForeignKey(Item.id), nullable=False)

    items = relationship("Item", back_populates="characteristics")

class Review(BaseModel):
    __tablename__ = "review"

    stars = Column(Integer, nullable=False)
    item_id = Column(ForeignKey(Item.id), nullable=False)

    items = relationship("Item", back_populates="reviews")