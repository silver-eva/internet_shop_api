from fastapi import APIRouter, Body, Path, status, Query, Depends

from uuid import uuid4, UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, func, or_

from models.db import News, Review
from lib.db.engine import get_db, db_execute

from models.app.request import PaginationRequest, ReviewRequest, NewsUpsertRequest
from models.app.response import NewsPaginationResponse, NewsResponse, ReviewResponse

router = APIRouter()

async def _list_news_helper(
        request: PaginationRequest = Query(default=PaginationRequest()),
        db: AsyncSession = Depends(get_db),
        news_id: UUID = None
    ):
    where_opts = []
    if news_id:
        where_opts.append(News.id == news_id)
        request.limit = 1
        request.page = 1
    else:
        where_opts = [
            News.name.icontains(request.keywords),
            News.description.icontains(request.keywords)
        ]

    query = select(
        func.count(News.id).over().label("count"),
        News,
        func.array_agg(
            func.jsonb_build_object(
                "id", Review.id,
                "name", Review.name,
                "description", Review.description,
                "stars", Review.stars,
                "created_at", Review.created_at
            ).distinct()
        ).label("reviews")
    ).outerjoin(
        Review,
        Review.news_id == News.id
    ).order_by(
        News.updated_at.desc()
    ).limit(
        request.limit
    ).offset(
        (request.page - 1) * request.limit
    ).group_by(
        News.id
    ).where(
        or_(
            *where_opts
        )
    )

    return await db_execute(db, query, with_result="raw_all")

@router.get("/", response_model=NewsPaginationResponse, description="List news")
async def list_news(
    request: PaginationRequest = Query(default=PaginationRequest()),
    db: AsyncSession = Depends(get_db)
):
    news = await _list_news_helper(request, db)
    count = 0
    if news:
        count, *_ = news[0]

    items = []
    for _, news_, reviews in news:
        reviews_response = []
        for review in reviews:
            if not all([review.get(key) for key in review.keys()]): 
                continue
            review_response = ReviewResponse.model_validate(review)
            reviews_response.append(review_response)

        items.append(
            NewsResponse(
                id=news_.id,
                name=news_.name,
                description=news_.description,
                created_at=news_.created_at,
                updated_at=news_.updated_at,
                reviews=reviews_response
            )
        )

    return NewsPaginationResponse(
        page=request.page,
        limit=request.limit,
        count=count,
        items = items
    )

@router.get("/{id}", response_model=NewsResponse, description="Get news by id")
async def get_news(
    id: UUID = Path(),
    db: AsyncSession = Depends(get_db)
    ):
    news = await _list_news_helper(news_id=id, db=db)
    if not news:
        return status.HTTP_404_NOT_FOUND
    
    _, news, reviews = news[0]
    
    reviews_response = []
    for review in reviews:
        if not all([review.get(key) for key in review.keys()]): 
            continue
        review_response = ReviewResponse.model_validate(review)
        reviews_response.append(review_response)

    return NewsResponse(
        id=news.id,
        name=news.name,
        description=news.description,
        created_at=news.created_at,
        updated_at=news.updated_at,
        reviews=reviews_response
    )

@router.patch("/", description="Upsert news", status_code=status.HTTP_204_NO_CONTENT)
async def upsert_news(
    request: NewsUpsertRequest = Body(default=NewsUpsertRequest()),
    db: AsyncSession = Depends(get_db)
):
    if request.id:
        pass
    else:
        request.id = str(uuid4())

    query = insert(News).values(
        id=request.id,
        name=request.name,
        description=request.description
    ).on_conflict_do_update(
        index_elements=[News.id],
        set_={
            News.name: request.name,
            News.description: request.description,
            News.updated_at: func.now()
        },
        where=(News.id == request.id)
    ).returning(News.id)

    item_id = (await db.execute(query)).scalar()
    print(item_id)

    await db.commit()

@router.post("/{id}/review", tags=["reviews"], description="Add review")
async def add_review(
    id: UUID = Path(),
    request: ReviewRequest = Body(default=ReviewRequest()),
    db: AsyncSession = Depends(get_db)
    ):
    await db.execute(
        insert(Review).values(
            news_id=id,
            name=request.name,
            description=request.description,
            stars=request.stars
        )
    )

    await db.commit()
    return status.HTTP_204_NO_CONTENT
