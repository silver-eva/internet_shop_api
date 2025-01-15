from pydantic import BaseModel, UUID4
from typing import List
from datetime import datetime

class PaginationResponse(BaseModel):
    page: int
    limit: int
    count: int

class Characteristic(BaseModel):
    id: UUID4
    name: str
    value: str

class ReviewResponse(BaseModel):
    id: UUID4
    name: str
    description: str
    stars: int
    created_at: datetime

class CategoryResponse(BaseModel):
    id: UUID4
    name: str
    description: str

class ItemResponse(BaseModel):
    id: UUID4
    name: str
    description: str
    price: float
    category: CategoryResponse
    characteristics: List[Characteristic|None]
    reviews: List[ReviewResponse| None]

class NewsResponse(BaseModel):
    id: UUID4
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    reviews: List[ReviewResponse|None]


class CoreResponse(BaseModel):
    id: UUID4
    name: str
    description: str

    class Config:
        from_attributes = True

class CorePaginationResponse(PaginationResponse):
    items: List[CoreResponse]

class ItemsPaginationResponse(PaginationResponse):
    items: List[ItemResponse]

class NewsPaginationResponse(PaginationResponse):
    items: List[NewsResponse]