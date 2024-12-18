from fastapi import FastAPI

from controllers.itemController import ItemController

async def startup_event():
    print("Startup")

async def shutdown_event():
    print("Shutdown")

class App(FastAPI):
    def __init__(self):
        super().__init__(title="API", version="0.0.1", description="Shop API", openapi_prefix="/api/v1")

        self.set_event_handlers()
        self.set_routers()
        self.set_error_handlers()
        self.set_middlewares()
        
    def set_routers(self):
        self.include_router(ItemController())

    def set_event_handlers(self):
        self.add_event_handler("startup", startup_event)
        self.add_event_handler("shutdown", shutdown_event)

    def set_error_handlers(self):
        pass

    def set_middlewares(self):
        pass

app = App()