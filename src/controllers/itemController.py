from fastapi import APIRouter, Path, Depends, status, HTTPException
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from src.db.engine import get_session, db_execute
from src.db.models import Item, Category, Characteristic, ItemCharacteristic, ItemCategory, Review

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, delete

from src.models.requests import ItemRequest
from src.models.responses import ItemResponse, ItemCategoryResponse, CoreResponse, ReviewResponse


class ItemController(APIRouter):
    def __init__(self):
        super().__init__(prefix = "/items", tags = ["Items"])

        self.add_api_route("/", self.create_item, methods=["PATCH"], description="Create item", response_model=None)
        self.add_api_route("/{id}", self.get_item, methods=["GET"], description="Get item", response_model=ItemResponse)


    async def create_item(
            self, 
            item: ItemRequest,
            db: AsyncSession = Depends(get_session),
            ) -> None:

        category = await db_execute(db, select(Category).where(Category.id == item.category_id), with_result="one")
        if not category:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")
        
        if item.id:
            await db.execute(
                delete(ItemCharacteristic).where(ItemCharacteristic.item_id == item.id)
            )
            await db.execute(
                delete(ItemCategory).where(ItemCategory.item_id == item.id)
            )

        new_item = (await db.execute(
            insert(Item).values(
                id=item.id,
                name=item.name,
                description=item.description,
                price=item.price,
            ).on_conflict_do_update(
                index_elements=[Item.id],
                set_={
                    Item.name: item.name,
                    Item.description: item.description,
                    Item.price: item.price,
                    Item.updated_at: datetime.now()
                }
            ).returning(Item)
        )).scalar()

        await db.execute(
            insert(ItemCategory).values(
                item_id=new_item.id,
                category_id=item.category_id
            )
        )

        for characteristic in item.characteristics:
            if not await db.execute(select(Characteristic).where(Characteristic.id == characteristic.id)):
                raise HTTPException(status.HTTP_404_NOT_FOUND, f"Characteristic {characteristic.name} not found")
            await db.execute(
                insert(ItemCharacteristic).values(
                    item_id=new_item.id,
                    characteristic_id=characteristic.id,
                    value=characteristic.value
                )
            )

        await db.commit()
        return status.HTTP_201_CREATED
    
    async def get_item(
            self, 
            id: UUID = Path(),
            db: AsyncSession = Depends(get_session)
            ) -> ItemResponse:
        item = await db_execute(db, select(Item).where(Item.id == id), with_result="one")
        category = await db_execute(
            db, 
            select(
                Category
            ).select_from(ItemCategory).where(
                ItemCategory.item_id == id
            ),
            with_result="one"
        )
        reviews = await db_execute(
            db, 
            select(
                Review
            ).where(
                Review.item_id == id
            ),
            with_result="all"
        )
        characteristics = await db_execute(
            db, 
            select(
                Characteristic
            ).select_from(ItemCharacteristic).join(
                Characteristic, 
                Characteristic.id == ItemCharacteristic.characteristic_id
            ).where(
                ItemCharacteristic.item_id == id
            ),
            with_result="all"
        )

        result = ItemResponse(
            id=item.id,
            name=item.name,
            description=item.description,
            price=item.price,
            category=ItemCategoryResponse.model_validate(category),
            created_at=item.created_at,
            updated_at=item.updated_at,
            reviews=[ReviewResponse.model_validate(review) for review in reviews],
            characteristics=[CoreResponse.model_validate(characteristic) for characteristic in characteristics]
        )

        return result