from fastapi import APIRouter, Body, Path, status, Query

from uuid import uuid4, UUID
from datetime import datetime

from models.app.request import PaginationRequest, ReviewRequest, NewsUpsertRequest
from models.app.response import NewsPaginationResponse, NewsResponse

router = APIRouter()

@router.get("/", response_model=NewsPaginationResponse, description="List news")
async def list_news(
    request: PaginationRequest = Query(default=PaginationRequest())
):
    return NewsPaginationResponse(
        page=request.page,
        limit=request.limit,
        count=2,
        items = [
            {
                "id": str(uuid4()),
                "name": "News 1",
                "updated_at": datetime.now(),
            },
            {
                "id": str(uuid4()),
                "name": "News 2",
                "updated_at": datetime.now(),
            }
        ]
    )

@router.get("/{id}", response_model=NewsResponse, description="Get news by id")
async def get_news(
    id: UUID = Path()
    ):
    return NewsResponse(
        id=str(uuid4()),
        name="News 1",
        description="News 1 description",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        reviews=[
            {"id": str(uuid4()), "name": "Review 1", "description": "Review 1 description", "stars": 5, "created_at": datetime.now()},
            {"id": str(uuid4()), "name": "Review 2", "description": "Review 2 description", "stars": 4, "created_at": datetime.now()},
        ]
    )

@router.patch("/", description="Upsert news")
async def upsert_news(
    request: NewsUpsertRequest = Body(default=NewsUpsertRequest())
):
    return status.HTTP_204_NO_CONTENT

@router.post("/{id}/review", tags=["reviews"], description="Add review")
async def add_review(
    id: UUID = Path(),
    request: ReviewRequest = Body(default=ReviewRequest())
    ):
    return status.HTTP_204_NO_CONTENT
