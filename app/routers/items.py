from fastapi import APIRouter, Body, Path, status

from uuid import uuid4, UUID
from datetime import datetime

from models.app.request import ItemFilterRequest, ItemUpsertRequest, ReviewRequest
from models.app.response import ItemsPaginationResponse, ItemResponse

router = APIRouter()

@router.post("/filter", response_model=ItemsPaginationResponse)
async def filter_items(
    request: ItemFilterRequest=Body(default=ItemFilterRequest())
    ):
    return ItemsPaginationResponse(
        page=request.page,
        limit=request.limit,
        count=2,
        items = [
            {
                "id": str(uuid4()),
                "name": "Item 1",
                "price": 10.99,
                "category": "Category 1",
            },
            {
                "id": str(uuid4()),
                "name": "Item 2",
                "price": 10.99,
                "category": "Category 2",
            },
        ]
    )

@router.get("/{id}", response_model=ItemResponse)
async def get_item(
    id: UUID = Path()
    ):
    return ItemResponse(
        id=id,
        name="Item 1",
        description="Item 1 description",
        price=10.99,
        category={"id": str(uuid4()), "name": "Category 1", "description": "Category 1 description"},
        characteristics=[
            {"id": str(uuid4()), "name": "Characteristic 1", "value": "Value 1"},
            {"id": str(uuid4()), "name": "Characteristic 2", "value": "Value 2"},
        ],
        reviews=[
            {"id": str(uuid4()), "name": "Review 1", "description": "Review 1 description", "stars": 5, "created_at": datetime.now()},
            {"id": str(uuid4()), "name": "Review 2", "description": "Review 2 description", "stars": 4, "created_at": datetime.now()},
        ]
    )

@router.patch("/")
async def upsert_item(
    request: ItemUpsertRequest = Body(default=ItemUpsertRequest())
    ):
    return status.HTTP_204_NO_CONTENT

@router.post("/{id}/review", tags=["reviews"])
async def add_review(
    id: UUID = Path(),
    request: ReviewRequest = Body(default=ReviewRequest())
    ):
    return status.HTTP_204_NO_CONTENT
