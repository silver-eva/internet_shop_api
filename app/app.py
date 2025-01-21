from fastapi import FastAPI
from routers import core, items, news
from lib.middleware.logging import LoggingMiddleware

app = FastAPI()

# Add middleware
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(core.router, prefix="/core", tags=["Core"])
app.include_router(items.router, prefix="/items", tags=["Items"])
app.include_router(news.router, prefix="/news", tags=["News"])

async def startup_event():
    print("Startup")

async def shutdown_event():
    print("Shutdown")

app.add_event_handler("startup", startup_event)
app.add_event_handler("shutdown", shutdown_event)

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI app!"}