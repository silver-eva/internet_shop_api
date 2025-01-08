from pydantic import BaseModel, Field, UUID4
from typing import List, Optional, Literal
from uuid import uuid4

class PaginationRequest(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1)
    keywords: Optional[str] = Field(default="", max_length=128)

class CharacteristicRequest(BaseModel):
    id: UUID4 = Field(default_factory=uuid4)
    value: str = Field(default="", max_length=128)

class CoreUpsertRequest(BaseModel):
    id: Optional[UUID4] | None = Field(None)
    name: str = Field(default_factory=str, max_length=128)
    description: str = Field(default_factory=str, max_length=256)

class ItemFilterRequest(PaginationRequest):
    category: Optional[UUID4] = Field(None, description="Category id [UUID]")
    characteristics: Optional[List[CharacteristicRequest]] = Field(
        default=[], 
        description="List of characteristics with char_id and char_value"
    )
    sort_dir: Literal["asc", "desc"] = Field(default="asc")
    sort_by: Literal["name", "created_at", "updated_at", "price"] = Field(default="price")
    min_price: Optional[int | None] = Field(gt=0, default=0)
    max_price: Optional[int | None] = Field(gt=0, default=0)

class ItemUpsertRequest(BaseModel):
    id: Optional[UUID4] = Field(default_factory=uuid4)
    name: Optional[str] = Field(default_factory=str, max_length=128)
    description: Optional[str] = Field(default_factory=str, max_length=256)
    price: Optional[float | int] = Field(gt=0, default=0)
    category: Optional[UUID4] = Field(default_factory=uuid4, description="Category id [UUID]")
    characteristics: Optional[List[CharacteristicRequest]] = Field(
        default=CharacteristicRequest, 
        description="List of characteristics with char_id and char_value"
    )

class ReviewRequest(BaseModel):
    name: Optional[str] = Field(default_factory=str, max_length=128)
    description: Optional[str] = Field(default_factory=str, max_length=256)
    stars: int = Field(default=1, ge=1, le=5)

class NewsUpsertRequest(BaseModel):
    id: Optional[UUID4] = Field(default_factory=uuid4)
    name: Optional[str] = Field(default_factory=str, max_length=128)
    description: Optional[str] = Field(default_factory=str, max_length=256)
