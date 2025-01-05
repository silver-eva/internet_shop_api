from fastapi import APIRouter, status, Depends, Query, HTTPException, Path ,Body
from datetime import datetime
from typing import Literal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from src.db.engine import get_session, db_execute
from src.db.models import Category, Characteristic, BaseModel

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, func, or_, delete
from sqlalchemy.inspection import Callable

from src.models.requests import ListRequest, CoreRequest
from src.models.responses import ListResponse, CoreResponse

CORE_PARAMS = Literal["category", "characteristic"]

async def add_or_update_core(db: AsyncSession, model: BaseModel, request: CoreRequest) -> None:
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
                model.updated_at: datetime.now(),
                model.description: request.description
            },
            where=(model.id == request.id)
        )
    )

    return status.HTTP_204_NO_CONTENT

async def list_core(
        db: AsyncSession,
        model: BaseModel,
        order: Callable,
        request: ListRequest = Query(default=ListRequest()),
):

    offset = (request.page - 1) * request.limit

    query = select(model).offset(offset).limit(
        request.limit
    ).order_by(order).add_columns(
        func.count(model.id).over().label("total")
    ).group_by(model.name, model.id).where(
        or_(
            model.name.icontains(request.keyword),
            model.description.icontains(request.keyword)
        )
    )

    core = await db_execute(db, query, with_result="raw_all")

    total_count = 0
    if core:
        _, total_count = core[0]

    response = ListResponse(
        page=request.page,
        limit=request.limit,
        total=total_count,
        items=[CoreResponse.model_validate(core) for core, _ in core]
    )
    return response

async def remove_core(db, model, id):
    await db_execute(db, delete(model).where(model.id == id))
    return status.HTTP_204_NO_CONTENT

class CoreController(APIRouter):
    def __init__(self):
        super().__init__(prefix="/core", tags=["Core"])
        self.param_map = {
            "category": Category,
            "characteristic": Characteristic
        }

        self.add_api_route("/list/{param}", self.list_param, methods=["GET"], description="List parameters", response_model=ListResponse)
        self.add_api_route("/{param}/", self.add_or_update_param, methods=["PATCH"], description="Add or update Item parameter", response_model=None)
        self.add_api_route("/{param}/{id}", self.remove_param, methods=["DELETE"], description="Remove Item parameter", response_model=None)

    async def list_param(
            self, 
            param: CORE_PARAMS = Path(), 
            request: ListRequest = Query(default=ListRequest()), 
            db: AsyncSession = Depends(get_session)
            ) -> ListResponse:
        
        return await list_core(db, self.param_map[param], self.param_map[param].name.asc(), request)
    
    async def add_or_update_param(
            self, 
            param: CORE_PARAMS = Path(), 
            request: CoreRequest = Body(default=CoreRequest()), 
            db: AsyncSession = Depends(get_session)
        ):
        return await add_or_update_core(db, self.param_map[param], request)
    
    async def remove_param(
            self, 
            param: CORE_PARAMS = Path(), 
            id: UUID = Path(), 
            db: AsyncSession = Depends(get_session)
        ):
        return await remove_core(db, self.param_map[param], id)
    