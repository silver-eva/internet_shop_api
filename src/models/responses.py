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
