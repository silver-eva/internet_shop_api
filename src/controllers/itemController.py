from fastapi import APIRouter, status

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
            response_model=dict, #TODO: Item
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

    async def get_items(self) -> list:
        return []
    
    async def get_item(self, id: int) -> dict:
        return {}
    
    async def create_item(self, item: dict):
        return None
    
    async def update_item(self, id: int, item: dict):
        return None
    
    async def delete_item(self, id: int):
        return None