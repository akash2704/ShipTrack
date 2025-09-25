from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.schemas.shipment import ShipmentCreate, Shipment as ShipmentSchema, ShipmentUpdate
from app.services.shipment_service import ShipmentService

router = APIRouter()

@router.get("/", response_model=List[ShipmentSchema])
async def get_shipments(db: AsyncSession = Depends(get_db)):
    return await ShipmentService.get_all_shipments(db)

@router.post("/", response_model=ShipmentSchema)
async def create_shipment(shipment: ShipmentCreate, db: AsyncSession = Depends(get_db)):
    return await ShipmentService.create_shipment(db, shipment)

@router.get("/{shipment_id}", response_model=ShipmentSchema)
async def get_shipment(shipment_id: int, db: AsyncSession = Depends(get_db)):
    shipment = await ShipmentService.get_shipment_by_id(db, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment

@router.patch("/{shipment_id}", response_model=ShipmentSchema)
async def update_shipment(shipment_id: int, shipment_update: ShipmentUpdate, db: AsyncSession = Depends(get_db)):
    shipment = await ShipmentService.get_shipment_by_id(db, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    return await ShipmentService.update_shipment(db, shipment, shipment_update)
@router.get("/track/{tracking_number}", response_model=ShipmentSchema)
async def track_shipment(tracking_number: str, db: AsyncSession = Depends(get_db)):
    from app.models.shipment import Shipment
    result = await db.execute(select(Shipment).where(Shipment.tracking_number == tracking_number))
    shipment = result.scalar_one_or_none()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment
@router.post("/{shipment_id}/locations")
async def add_location_update(
    shipment_id: int,
    location_data: dict,
    db: AsyncSession = Depends(get_db)
):
    from app.models.location_tracking import LocationUpdate
    location_update = LocationUpdate(
        shipment_id=shipment_id,
        latitude=location_data["latitude"],
        longitude=location_data["longitude"]
    )
    db.add(location_update)
    await db.commit()
    await db.refresh(location_update)
    return location_update

@router.get("/{shipment_id}/locations")
async def get_location_history(shipment_id: int, db: AsyncSession = Depends(get_db)):
    from app.models.location_tracking import LocationUpdate
    result = await db.execute(select(LocationUpdate).where(LocationUpdate.shipment_id == shipment_id))
    return result.scalars().all()
