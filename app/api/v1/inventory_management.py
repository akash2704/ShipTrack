from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.inventory import Inventory
from app.schemas.inventory import Inventory as InventorySchema, InventoryCreate

router = APIRouter()

@router.get("/location/{location_id}/product/{product_id}", response_model=InventorySchema)
async def get_inventory_by_location_product(location_id: int, product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Inventory).where(
            Inventory.location_id == location_id,
            Inventory.product_id == product_id
        )
    )
    inventory = result.scalar_one_or_none()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory

@router.post("/", response_model=InventorySchema)
async def create_inventory(inventory_data: InventoryCreate, db: AsyncSession = Depends(get_db)):
    db_inventory = Inventory(**inventory_data.model_dump())
    db.add(db_inventory)
    await db.commit()
    await db.refresh(db_inventory)
    return db_inventory
