from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Numeric, text
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

    name = Column(String, index=True, nullable=False, unique=False)
    description = Column(String, index=True)

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

    password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    role = Column(String, nullable=False, default="viewer")

class Category(BaseModel):
    __tablename__ = "category"

    items = relationship("ItemCategory", back_populates="categories")

class Item(BaseModel):
    __tablename__ = "item"

    price = Column(Numeric, nullable=False)

    category = relationship("ItemCategory", back_populates="items")
    characteristics = relationship("ItemCharacteristic", back_populates="items")
    reviews = relationship("Review", back_populates="items", cascade="all, delete-orphan")

class ItemCategory(BaseModel):
    __tablename__ = "item_category"

    name = Column(String, nullable=True)

    item_id = Column(ForeignKey(Item.id), nullable=False)
    category_id = Column(ForeignKey(Category.id), nullable=False)

    items = relationship("Item", back_populates="category")
    categories = relationship("Category", back_populates="items")

class Characteristic(BaseModel):
    __tablename__ = "characteristic"

    items = relationship("ItemCharacteristic", back_populates="characteristics")

class ItemCharacteristic(BaseModel):
    __tablename__ = "item_characteristic"

    name = Column(String, nullable=True)

    item_id = Column(ForeignKey(Item.id), nullable=False)
    characteristic_id = Column(ForeignKey(Characteristic.id), nullable=False)
    value = Column(String, nullable=False)

    items = relationship("Item", back_populates="characteristics")
    characteristics = relationship("Characteristic", back_populates="items")

class Review(BaseModel):
    __tablename__ = "review"

    name = Column(String, nullable=True)

    stars = Column(Integer, nullable=False)
    item_id = Column(ForeignKey(Item.id), nullable=False)

    items = relationship("Item", back_populates="reviews")