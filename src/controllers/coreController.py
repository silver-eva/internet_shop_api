from fastapi import APIRouter, status, Depends, Query, HTTPException
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from src.db.engine import get_session, db_execute
from src.db.models import Category, Characteristic, BaseModel

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, func
from sqlalchemy.inspection import Callable

from src.models.requests import ListRequest, CoreRequest
from src.models.responses import ListResponse, CoreResponse


async def add_or_update_core(db: AsyncSession, model: BaseModel, request: CoreRequest) -> None:
    result = await db_execute(
        db, 
        select(
            model
        ).where(
            model.name == request.name
        ), 
        with_result="one")

    if result:
        return HTTPException(status.HTTP_409_CONFLICT, f"{model.__tablename__} already exists")
    
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
    ).group_by(model.name, model.id)

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

class CoreController(APIRouter):
    def __init__(self):
        super().__init__(prefix="/core", tags=["Core"])

        self.add_api_route("/categoryes/list", self.list_category, methods=["GET"], description="List category", response_model=ListResponse)
        self.add_api_route("/categoryes/", self.add_or_update_category, methods=["PATCH"], description="Add or update category", response_model=None)

        self.add_api_route("/characteristics/list", self.list_characteristic, methods=["GET"], description="List characteristic", response_model=ListResponse)
        self.add_api_route("/characteristics/", self.add_or_update_characteristic, methods=["PATCH"], description="Add or update characteristic", response_model=None)

    async def list_category(self, request: ListRequest = Query(default=ListRequest()), db: AsyncSession = Depends(get_session)) -> ListResponse:
        return await list_core(db, Category, Category.updated_at.desc(), request)
    
    async def add_or_update_category(self, request: CoreRequest, db: AsyncSession = Depends(get_session)):
        return await add_or_update_core(db, Category, request)
    
    async def add_or_update_characteristic(self, request: CoreRequest, db: AsyncSession = Depends(get_session)):
        return await add_or_update_core(db, Characteristic, request)
    
    async def list_characteristic(self, request: ListRequest = Query(default=ListRequest()), db: AsyncSession = Depends(get_session)) -> ListResponse:
        return await list_core(db, Characteristic, Characteristic.name.asc(), request)