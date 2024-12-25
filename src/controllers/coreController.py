from fastapi import APIRouter, status, Depends, Query, HTTPException
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from src.db.engine import get_session, db_execute
from src.db.models import Category, Characteristic

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, or_, func

from src.models.requests import CategoryListRequest, CategoryRequest
from src.models.responses import CategoryResponse, ListResponse


class CoreController(APIRouter):
    def __init__(self):
        super().__init__(prefix="/core", tags=["Core"])

        self.add_api_route("/categoryes/list", self.list_category, methods=["GET"], description="List category", response_model=ListResponse)
        self.add_api_route("/categoryes/", self.add_or_update_category, methods=["PATCH"], description="Add or update category", response_model=None)

    async def list_category(
            self,
            request: CategoryListRequest = Query(default=CategoryListRequest()),
            db: AsyncSession = Depends(get_session),
            ) -> list[CategoryResponse]:
        
        offset = (request.page - 1) * request.limit

        query = select(Category).offset(offset).limit(request.limit).where(
            or_(
                Category.name.icontains(request.keyword),
                Category.description.icontains(request.keyword)
        )).order_by(
            Category.updated_at.desc()
        ).add_columns(
            func.count(Category.id).over().label("total")
        ).group_by(Category.name, Category.id)
        
        categories = await db_execute(db, query, with_result="raw_all")
        _, total_count = categories[0]

        response = ListResponse(
            page=request.page,
            limit=request.limit,
            total=total_count,
            items=[CategoryResponse.model_validate(category) for category, _ in categories]
        )
        return response
    
    async def add_or_update_category(
            self, 
            category: CategoryRequest, 
            db: AsyncSession = Depends(get_session)
            ):
        category_db = await db_execute(
                db,
                select(Category).where(
                    Category.name == category.name
                ),
                with_result="one"
            )

        if category_db:
            return HTTPException(status.HTTP_409_CONFLICT, "Category already exists")

        await db_execute(
            db,
            insert(Category).values(
                id=category.id,
                name=category.name,
                description=category.description
            ).on_conflict_do_update(
                index_elements=[Category.id],
                set_={
                    Category.name: category.name,
                    Category.updated_at: datetime.now(),
                    Category.description: category.description
                },
                where=(Category.id == category.id)
            )
        )

        return status.HTTP_204_NO_CONTENT