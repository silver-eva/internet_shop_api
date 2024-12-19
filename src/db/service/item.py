from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select

from src.db.models import Item
from src.db.session import db_execute
from src.models.itemModels import ItemRequest, ItemResponse

from src.lib.config import moc_user_id

import json

async def insert_item(db: AsyncSession, item: ItemRequest):
    query = insert(Item).values(
        title=item.title,
        price=item.price,
        dimention=item.dimention,
        single_piece=item.single_piece,
        additional=json.dumps(item.additional),
        description=item.description,
        owner_id=moc_user_id
    ).returning(Item)
    return await db_execute(db, query, with_result="one")

async def list_items(db: AsyncSession, page: int, limit: int) -> list[ItemResponse]:
    offset = (page - 1) * limit if page > 1 else 0
    query = select(Item).limit(limit).offset(offset)
    items: list[Item] = await db_execute(db, query, with_result="all")
    ready_items = []
    for item in items:
        ready_item = item.as_dict(exclude=["additional"])
        ready_items.append(
            ItemResponse(
                additional=json.loads(item.additional),
                **ready_item
            )
        )
    return ready_items


