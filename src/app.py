from fastapi import FastAPI

from src.controllers.itemController import ItemController

async def startup_event():
    print("Startup")

async def shutdown_event():
    print("Shutdown")

class App(FastAPI):
    def __init__(self):
        super().__init__(title="API", version="0.0.1", description="Shop API", root_path="/api/v1")

        self.set_error_handlers()
        self.set_routers()
        self.set_middlewares()
        
    def set_routers(self):
        self.include_router(ItemController())

    def set_error_handlers(self):
        pass

    def set_middlewares(self):
        pass