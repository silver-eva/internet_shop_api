from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Literal

class Item(BaseModel):
    title: str = Field(..., min_length=3, max_length=50)
    price: float = Field(..., gt=0)
    dimention: Literal["m","kg","t", "m2"] = Field(..., min_length=1, max_length=50)
    single_piece: int = Field(..., gt=0)
    additional: dict = Field({}) # json serializable
    description: str = Field("",)

    class Config:
        from_attributes = True

class ItemRequest(Item):
    pass

class ItemResponse(Item):
    id: UUID
    updated_at: datetime
    created_at: datetime
    owner_id: UUID

    class Config:
        from_attributes = True

