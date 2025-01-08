from fastapi import APIRouter, Body, Path, status, Depends, HTTPException

from uuid import uuid4, UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, delete, or_, asc, desc, func, and_

from models.app.request import ItemFilterRequest, ItemUpsertRequest, ReviewRequest
from models.app.response import (
    ItemsPaginationResponse, 
    ItemResponse, 
    CategoryResponse, 
    Characteristic as CharacteristicResponse,
    ReviewResponse
)

from models.db import Item, Characteristic, Category, ItemCharacteristic, Review
from lib.db.engine import get_db, db_execute

router = APIRouter()

@router.post("/filter", response_model=ItemsPaginationResponse)
async def filter_items(
    request: ItemFilterRequest=Body(default=ItemFilterRequest()),
    db: AsyncSession = Depends(get_db)
    ):
    sort_dir_map = {
        "asc": asc,
        "desc": desc
    }
    offset = (request.page - 1) * request.limit
    where_opts = []
    
    if request.category:
        where_opts.append(Item.category_id == request.category)
    if request.min_price:
        where_opts.append(Item.price >= request.min_price)
    if request.max_price:
        where_opts.append(Item.price <= request.max_price)
    if request.characteristics:
        for characteristic in request.characteristics:
            where_opts.append(and_(ItemCharacteristic.value == characteristic.value, ItemCharacteristic.characteristic_id == characteristic.id))
    if request.keywords:
        where_opts.append(
            or_(
                Item.name.icontains(request.keywords),
                Item.description.icontains(request.keywords)
            )
        )

    filter_subq = select(
        Item.id
    ).join(
        ItemCharacteristic, Item.id == ItemCharacteristic.item_id
    ).filter(
        and_(*where_opts)
    ).subquery()

    query = select(
        func.count(Item.id).over().label("count"), 
        Item, 
        Category, 
        func.array_agg(
            func.jsonb_build_object(
                "id", Characteristic.id,
                "name", Characteristic.name,
                "value", ItemCharacteristic.value
            ).distinct()
        ).label("characteristics"),
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
        Category,
        Item.category_id == Category.id
    ).outerjoin(
        ItemCharacteristic,
        Item.id == ItemCharacteristic.item_id
    ).outerjoin(
        Characteristic,
        ItemCharacteristic.characteristic_id == Characteristic.id
    ).outerjoin(
        Review,
        Item.id == Review.item_id
    ).where(
        Item.id.in_(filter_subq)
    ).order_by(
        sort_dir_map[request.sort_dir](request.sort_by)
    ).limit(request.limit).offset(offset).group_by(
        Item.id, Category.id
    )
    
    items: list[Item] = await db_execute(db, query, with_result="raw_all")

    count = 0
    if items:
        count, *_ = items[0]

    response_items = []
    for _, item, category, characteristcs, reviews in items:
        characteristcs_response = []
        reviews_response = []
        for characteristic in characteristcs:
            if not all([characteristic.get(key) for key in characteristic.keys()]): 
                continue
            characteristc_response = CharacteristicResponse.model_validate(characteristic)
            characteristcs_response.append(characteristc_response)

        for review in reviews:
            if not all([review.get(key) for key in review.keys()]): 
                continue
            review_response = ReviewResponse.model_validate(review)
            reviews_response.append(review_response)

        response_items.append(
            ItemResponse(
                id=item.id,
                name=item.name,
                description=item.description,
                price=item.price,
                category=CategoryResponse(
                    id=category.id,
                    name=category.name,
                    description=category.description
                ),
                characteristics=characteristcs_response if characteristcs_response else [],
                reviews=reviews_response if reviews_response else []
            )
        )

    return ItemsPaginationResponse(
        page=request.page,
        limit=request.limit,
        count=count,
        items = response_items
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
    request: ReviewRequest = Body(default=ReviewRequest()),
    db: AsyncSession = Depends(get_db)
    ):
    return status.HTTP_204_NO_CONTENT
