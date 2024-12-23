from pydantic import Field, BaseModel
from src.models.base import ItemBase, ItemDependent
from uuid import uuid4

class Category(ItemBase):
    pass

class Characteristic(ItemDependent):
    value: str  

class Review(ItemDependent):
    stars: int

class Item(ItemBase):
    category: Category
    characteristics: list[Characteristic]
    reviews: list[Review]

    price: float = Field(..., gt=0)

class CharacteristicRequest(BaseModel):
    name: str = Field(..., max_length=128)
    description: str = Field(..., max_length=256)
    value: str = Field(..., max_length=128)


class ItemRequest(BaseModel):
    category_id: str = Field(...)
    id: str = Field(..., default_factory=uuid4)
    name: str = Field(..., max_length=128)
    description: str = Field(..., max_length=256)
    characteristics: list[CharacteristicRequest] = Field(...)
    price: float = Field(..., gt=0)
     
