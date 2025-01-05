from uuid import UUID
from fastapi import APIRouter, Query, Path, Body, status, Depends, HTTPException
from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import delete, select, func, or_

from models.app.request import PaginationRequest, CoreUpsertRequest
from models.app.response import CorePaginationResponse, CoreResponse

from models.db import Category, Characteristic

from lib.db.engine import get_db, db_execute

router = APIRouter()

_parameters_map_to_model = {
    "category": Category,
    "characteristic": Characteristic
}

@router.get("/{parameter}/list", response_model=CorePaginationResponse, status_code=status.HTTP_200_OK)
async def list_items(
    parameter: Literal["category", "characteristic"] = Path(),
    request: PaginationRequest = Query(default=PaginationRequest()),
    db: AsyncSession = Depends(get_db)
    ):
    
    model: Category | Characteristic = _parameters_map_to_model[parameter]
    offset = (request.page - 1) * request.limit
    
    query = select(model).add_columns(
        func.count(model.id).over().label("count")
    ).where(
        or_(
            model.name.icontains(request.keywords),
            model.description.icontains(request.keywords)
        )
    ).order_by(
        model.name.desc()
    ).group_by(model.name, model.id).limit(request.limit).offset(offset)

    items: list[Category | Characteristic] = await db_execute(db, query, with_result="raw_all")
    _, count = items[0]

    return CorePaginationResponse(
        page=request.page,
        limit=request.limit,
        count=count,
        items = [CoreResponse.model_validate(item) for item, _ in items]
    )

@router.patch("/{parameter}/", status_code=status.HTTP_204_NO_CONTENT)
async def upsert_item(
    parameter: Literal["category", "characteristic"] = Path(),
    request: CoreUpsertRequest = Body(default_factory=CoreUpsertRequest),
    db: AsyncSession = Depends(get_db)
    ):
    model: Category | Characteristic = _parameters_map_to_model[parameter]

    if not request.id:
        if await db_execute(db, select(model).where(model.name == request.name), with_result="one"):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Name already exists")
    
    await db_execute(
        db,
        insert(model).values(
            id=request.id,
            name=request.name,
            description=request.description
        ).on_conflict_do_update(
            index_elements=[model.id],
            set_={
                model.name: request.name,
                model.description: request.description
            },
            where=(model.id == request.id)
        )
    )

    return 

@router.delete("/{parameter}/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    parameter: Literal["category", "characteristic"] = Path(),
    id: UUID = Path(),
    db: AsyncSession = Depends(get_db)
    ):
    model: Category | Characteristic = _parameters_map_to_model[parameter]
    
    return await db_execute(db, delete(model).where(model.id == id))

