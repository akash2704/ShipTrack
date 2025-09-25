import os
from fastapi import FastAPI
from app.core.config import settings
from app.core.database import get_db, init_database, Base
from app.api.v1.router import api_router
from app.api.v1.websocket import router as websocket_router

app = FastAPI(
    title="ShipTrack API",
    description="Advanced Serverless Inventory & Logistics SaaS Platform",
    version="1.0.0"
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(websocket_router)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_database()

@app.get("/")
async def root():
    return {"message": "ShipTrack API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/db-test")
async def test_db():
    try:
        async for db in get_db():
            return {"status": "Database connected successfully!"}
    except Exception as e:
        return {"error": str(e)}
