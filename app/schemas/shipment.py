from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ShipmentBase(BaseModel):
    tracking_number: str
    origin_location_id: int
    destination_location_id: int
    status: str = "pending"
    estimated_delivery: Optional[datetime] = None

class ShipmentCreate(ShipmentBase):
    pass

class ShipmentUpdate(BaseModel):
    status: Optional[str] = None
    estimated_delivery: Optional[datetime] = None

class Shipment(ShipmentBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)