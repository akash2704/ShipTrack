from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.models.location_tracking import LocationUpdate
from app.models.shipment import Shipment
from app.core.websocket_manager import manager

router = APIRouter()

class LocationUpdateRequest(BaseModel):
    latitude: float
    longitude: float
    timestamp: str
    speed: float = None
    heading: float = None

@router.post("/{shipment_id}/location")
async def update_shipment_location(
    shipment_id: int,
    location_data: LocationUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Update shipment location and broadcast to subscribers"""
    # Verify shipment exists
    result = await db.execute(select(Shipment).where(Shipment.id == shipment_id))
    shipment = result.scalar_one_or_none()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    # Parse timestamp
    timestamp = datetime.fromisoformat(location_data.timestamp.replace('Z', '+00:00'))

    # Save location update
    location_update = LocationUpdate(
        shipment_id=shipment_id,
        latitude=location_data.latitude,
        longitude=location_data.longitude,
        timestamp=timestamp,
        speed=location_data.speed,
        heading=location_data.heading
    )

    db.add(location_update)
    await db.commit()

    # Broadcast to WebSocket subscribers
    await manager.broadcast_to_shipment({
        "type": "location_update",
        "shipment_id": shipment_id,
        "latitude": location_data.latitude,
        "longitude": location_data.longitude,
        "timestamp": location_data.timestamp,
        "speed": location_data.speed,
        "heading": location_data.heading,
        "tracking_number": shipment.tracking_number
    }, shipment_id)

    return {"message": "Location updated successfully"}

