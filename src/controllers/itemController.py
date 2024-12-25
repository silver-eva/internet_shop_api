from fastapi import APIRouter, Query, Path, Depends, Body, status, HTTPException
from typing import Literal
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from src.db.engine import get_session, db_execute
from src.db.models import Item, Category, Characteristic

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select
# from src.db.service.item import insert_item, list_items

from src.models.itemModels import ItemRequest



class ItemController(APIRouter):
    def __init__(self):
        super().__init__(prefix = "/items", tags = ["Items"])

        # self.add_api_route("/list/{category}", self.get_items, methods=["GET"], description="List items")
        self.add_api_route("/", self.create_item, methods=["POST"], description="Create item", response_model=None)

    async def get_items(
            self,
            category: str = Path(...),
            filter: str = Query(default=""),
            limit: int = Query(default=10, gt=0),
            page: int = Query(default=1, gt=0),
            db: AsyncSession = Depends(get_session)
            ) -> list[Item]:
        
        # TODO: Item with category(Category model), reviews (List[Review]), characteristics (List[Characteristic])

        offset = (page - 1) * limit
        query = select(Item).limit(limit).offset(offset)

        # filter by category
        query = query.where(Item.category == category)

        # filter by other filters
        for key, value in filter.items():
            query = query.where(getattr(Item, key) == value)

        items = await db_execute(db, query, with_result="all")

        return items
    
    async def get_item(
            self, 
            id: int = Path(), 
            lang: Literal["ua", "en", "ru"] = Query(default="ua"),
            curency: Literal["uah", "usd"] = Query(default="uah"),
            db: AsyncSession = Depends(get_session)
            ) -> dict:
        return {}
    
    async def create_item(
            self, 
            item: ItemRequest,
            db: AsyncSession = Depends(get_session),
            ) -> None:

        category = (await db.execute(
            select(
                Category
            ).where(
                Category.id == item.category_id
            )
        )).scalar_one_or_none()

        if not category:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")

        new_item = (await db.execute(
            insert(Item).values(
                id=item.id,
                name=item.name,
                description=item.description,
                price=item.price,
                category_id=category.id,
            ).on_conflict_do_update(
                index_elements=[Item.id],
                set_={
                    Item.name: item.name,
                    Item.description: item.description,
                    Item.price: item.price,
                    Item.category_id: category.id,
                    Item.updated_at: datetime.now()
                }
            ).returning(Item)
        )).scalar_one_or_none()

        if new_item is None:
            raise HTTPException("Item not created", status_code=status.HTTP_400_BAD_REQUEST)

        for characteristic in item.characteristics:
            await db.execute(
                insert(Characteristic).values(
                    value=characteristic.value,
                    item_id=new_item.id,
                    name = characteristic.name,
                    description = characteristic.description
                ).on_conflict_do_update(
                    index_elements=[Characteristic.name],
                    set_={
                        Characteristic.name: characteristic.name,
                        Characteristic.description: characteristic.description,
                        Characteristic.value: characteristic.value,
                        Characteristic.item_id: new_item.id,
                        Characteristic.updated_at: datetime.now()
                    }
                )
            )

        await db.commit()
        return status.HTTP_201_CREATED
    
    async def update_item(
            self, 
            id: int = Path(), 
            item: dict = Body(default={}),
            lang: Literal["ua", "en", "ru"] = Query(default="ua"),
            curency: Literal["uah", "usd"] = Query(default="uah"),
            ) -> None:
        return None
    
    async def delete_item(
            self, 
            id: int = Path(),
            lang: Literal["ua", "en", "ru"] = Query(default="ua"),
            curency: Literal["uah", "usd"] = Query(default="uah"),
            ) -> None:
        return None