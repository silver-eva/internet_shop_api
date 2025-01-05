from pydantic import BaseModel, Field
from uuid import uuid4

from typing import Optional, List, Literal

class ListRequest(BaseModel):
    page: int = Field(default=1, gt=0)
    limit: int = Field(default=10, gt=0)
    keyword: Optional[str] = Field(default="", max_length=128)

class CoreRequest(BaseModel):
    id: Optional[str] = Field(..., default_factory=uuid4)
    name: Optional[str] = Field(default="", max_length=128)
    description: Optional[str] = Field(default="", max_length=256)

class CharacteristicRequest(CoreRequest):
    id: str = Field(default_factory=uuid4)
    value: str = Field(..., max_length=128)

class ItemRequest(CoreRequest):
    category_id: str = Field(..., default_factory=uuid4)
    price: float = Field(..., gt=0)
    characteristics: list[CharacteristicRequest] = Field(..., default_factory=list, max_length=10)

class ItemFilterRequest(ListRequest):
    category: Optional[str] = Field(..., default_factory=uuid4)
    min_price: Optional[float] = Field(gt=0, default=0)
    max_price: Optional[float] = Field(gt=0, default=0)
    characteristics: Optional[List[CharacteristicRequest]] = Field(default_factory=list)
    order_by: Optional[Literal["name", "price", "created_at", "updated_at"]] = Field(default="price")
    order_dir: Optional[Literal["asc", "desc"]] = Field(default="asc")
