from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class CoreResponse(BaseModel):
    id: UUID
    name: str
    description: str
    updated_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class ListResponse(BaseModel):
    page: int
    limit: int
    total: int
    items: list[CoreResponse]

class RewiewResponse(CoreResponse):
    name: str | None
    stars: int

class ItemCategoryResponse(CoreResponse):
    id: UUID
    name: str

class ItemForListResponse(CoreResponse):
    category: ItemCategoryResponse
    price: float


class ItemResponse(ItemForListResponse):
    price: float
    characteristics: list[CoreResponse]
    reviews: list[RewiewResponse]

class ItemListResponse(ListResponse):
    items: list[ItemForListResponse]

class ReviewResponse(CoreResponse):
    name: str | None
    stars: int