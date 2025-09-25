from fastapi import APIRouter
from .inventory import router as inventory_router
from .shipments import router as shipments_router
from .shipment_items import router as shipment_items_router
from .inventory_management import router as inventory_mgmt_router
from .location_tracking import router as location_router
from .expenses import router as expenses_router
from .financial_dashboard import router as dashboard_router
from .budgets import router as budgets_router
from .auth import router as auth_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(inventory_router, prefix="/inventory", tags=["inventory"])
api_router.include_router(shipments_router, prefix="/shipments", tags=["shipments"])
api_router.include_router(shipment_items_router, prefix="/shipments", tags=["shipment-items"])
api_router.include_router(inventory_mgmt_router, prefix="/inventory", tags=["inventory-management"])
api_router.include_router(location_router, prefix="/shipments", tags=["location-tracking"])
api_router.include_router(expenses_router, prefix="", tags=["expenses"])
api_router.include_router(dashboard_router, prefix="", tags=["financial-dashboard"])
api_router.include_router(budgets_router, prefix="", tags=["budgets"])
