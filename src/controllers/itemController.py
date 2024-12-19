from fastapi import APIRouter, status, Query, Path, Depends, Body
from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_session
# from src.db.models import Item
from src.db.service.item import insert_item, list_items

from src.models.itemModels import ItemRequest, ItemResponse
    


class ItemController(APIRouter):
    def __init__(self):
        super().__init__(prefix = "/items", tags = ["Items"])

        self.add_api_route(
            "/",
            self.get_items,
            methods=["GET"],
            status_code=status.HTTP_200_OK,
            response_model=list, #TODO: [Item]
            summary="Get all items",
            description="Get all items"
        )

        self.add_api_route(
            "/{id}",
            self.get_item,
            methods=["GET"],
            status_code=status.HTTP_200_OK,
            response_model=ItemResponse, #TODO: Item
            summary="Get item by id",
            description="Get item by id"
        )

        self.add_api_route(
            "/",
            self.create_item,
            methods=["POST"],
            status_code=status.HTTP_201_CREATED,
            summary="Create item",
            description="Create item"
        )

        self.add_api_route(
            "/{id}",
            self.update_item,
            methods=["PUT"],
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Update item by id",
            description="Update item by id"
        )

        self.add_api_route(
            "/{id}",
            self.delete_item,
            methods=["DELETE"],
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Delete item by id",
            description="Delete item by id"
        )

    async def get_items(
            self, 
            limit: int = Query(default=10),
            page: int = Query(default=1),
            db: AsyncSession = Depends(get_session)) -> list:
        return await list_items(db, page, limit)
    
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
            lang: Literal["ua", "en", "ru"] = Query(default="ua"),
            curency: Literal["uah", "usd"] = Query(default="uah"),
            db: AsyncSession = Depends(get_session),
            ) -> None:
        
        return await insert_item(db, item, lang, curency)
    
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