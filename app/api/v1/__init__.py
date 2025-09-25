from fastapi import APIRouter
from .inventory import router as inventory_router
from .shipments import router as shipments_router
from .expenses import router as expenses_router
from .auth import router as auth_router

api_router = APIRouter()
api_router.include_router(inventory_router, prefix="/inventory", tags=["inventory"])
api_router.include_router(shipments_router, prefix="/shipments", tags=["shipments"])
api_router.include_router(expenses_router, prefix="/expenses", tags=["expenses"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
