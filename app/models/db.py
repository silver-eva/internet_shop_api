from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from lib.db.engine import Base
from lib.config import DB_SCHEMA

class Category(Base):
    __tablename__ = "categories"
    __table_args__ = {"schema": DB_SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    name = Column(String(255), nullable=False, unique=False)
    description = Column(Text, nullable=True)

    items = relationship("Item", back_populates="category")


class Characteristic(Base):
    __tablename__ = "characteristics"
    __table_args__ = {"schema": DB_SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    name = Column(String(255), nullable=False, unique=False)
    description = Column(Text, nullable=True)

    items = relationship("ItemCharacteristic", back_populates="characteristic")


class Item(Base):
    __tablename__ = "items"
    __table_args__ = {"schema": DB_SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("app.categories.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    category = relationship("Category", back_populates="items")
    characteristics = relationship("ItemCharacteristic", back_populates="item")
    reviews = relationship("Review", back_populates="item")


class ItemCharacteristic(Base):
    __tablename__ = "item_characteristics"
    __table_args__ = (
        UniqueConstraint("item_id", "characteristic_id"),
        {"schema": DB_SCHEMA}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    item_id = Column(UUID(as_uuid=True), ForeignKey("app.items.id"), nullable=False)
    characteristic_id = Column(UUID(as_uuid=True), ForeignKey("app.characteristics.id"), nullable=False)
    value = Column(String(255), nullable=False)

    item = relationship("Item", back_populates="characteristics")
    characteristic = relationship("Characteristic")


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = {"schema": DB_SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    item_id = Column(UUID(as_uuid=True), ForeignKey("app.items.id"), nullable=True)
    news_id = Column(UUID(as_uuid=True), ForeignKey("app.news.id"), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    stars = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    item = relationship("Item", back_populates="reviews")
    news = relationship("News", back_populates="reviews")


class News(Base):
    __tablename__ = "news"
    __table_args__ = {"schema": DB_SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    reviews = relationship("Review", back_populates="news")
