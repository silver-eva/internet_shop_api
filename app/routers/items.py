from fastapi import APIRouter, Body, Path, status, Depends, HTTPException

from uuid import uuid4, UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, delete, or_

from models.app.request import ItemFilterRequest, ItemUpsertRequest, ReviewRequest
from models.app.response import ItemsPaginationResponse, ItemResponse

from models.db import Item, Characteristic, Category, ItemCharacteristic, Review
from lib.db.engine import get_db, db_execute

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
    id: UUID = Path(),
    db: AsyncSession = Depends(get_db)
    ):
    item_category_query = select(
        Item, 
        Category
    ).join(
        Category,
        Item.category_id == Category.id 
    ).where(
        Item.id == id
    )

    reviews_query = select(
        Review
    ).where(
        Review.item_id == id
    ).order_by(
        Review.created_at.desc()
    )

    characteristics_query = select(
        Characteristic,
        ItemCharacteristic.value
    ).select_from(ItemCharacteristic).join(
        Characteristic,
        Characteristic.id == ItemCharacteristic.characteristic_id
    ).where(
        ItemCharacteristic.item_id == id
    )

    item, category = await db_execute(db, item_category_query, with_result="raw_one")

    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")
    
    reviews = await db_execute(db, reviews_query, with_result="all")
    characteristics = await db_execute(db, characteristics_query, with_result="raw_all")

    response = ItemResponse(
        id=id,
        name=item.name,
        description=item.description,
        price=item.price,
        category={"id": category.id, "name": category.name, "description": category.description},
        characteristics=[
            {"id": char.id, "name": char.name, "value": value}
            for char, value in characteristics
        ],
        reviews=[
            {"id": review.id, "name": review.name, "description": review.description, "stars": review.stars, "created_at": review.created_at}
            for review in reviews
        ]
    )
    return response

@router.patch("/", status_code=status.HTTP_204_NO_CONTENT)
async def upsert_item(
    request: ItemUpsertRequest = Body(default=ItemUpsertRequest()),
    db: AsyncSession = Depends(get_db)
    ):
    if request.id:
        await db.execute(
            delete(ItemCharacteristic).where(ItemCharacteristic.item_id == request.id)
        )
    else:
        request.id = str(uuid4())

    query = insert(Item).values(
        id=request.id,
        name=request.name,
        description=request.description,
        price=request.price,
        category_id=request.category
    ).on_conflict_do_update(
        index_elements=[Item.id],
        set_={
            Item.name: request.name,
            Item.description: request.description,
            Item.price: request.price,
            Item.category_id: request.category
        },
        where=(Item.id == request.id)
    ).returning(Item.id)

    item_id = (await db.execute(query)).scalar()

    for characteristic in request.characteristics:
        await db.execute(
            insert(ItemCharacteristic).values(
                item_id=item_id,
                characteristic_id=characteristic.id,
                value=characteristic.value
            )
        )
    
    await db.commit()

@router.post("/{id}/review", tags=["reviews"])
async def add_review(
    id: UUID = Path(),
    request: ReviewRequest = Body(default=ReviewRequest())
    ):
    return status.HTTP_204_NO_CONTENT
