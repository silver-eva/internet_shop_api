from pydantic import BaseModel
from uuid import UUID

class Base(BaseModel):
    id: UUID

    class Config:
        from_attributes = True

class ItemBase(Base):
    name: str
    description: str

class ItemDependent(ItemBase):
    item_id: UUID