from pydantic import BaseModel, Field
from uuid import uuid4

class ListRequest(BaseModel):
    page: int = Field(default=1, gt=0)
    limit: int = Field(default=10, gt=0)
    keyword: str = Field(default="")
    
class CategoryListRequest(ListRequest):
    pass

class CategoryRequest(BaseModel):
    id: str = Field(..., default_factory=uuid4)
    name: str = Field(..., max_length=128)
    description: str = Field(..., max_length=256)
