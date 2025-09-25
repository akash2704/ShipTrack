from pydantic import BaseModel, ConfigDict, computed_field
from typing import Optional
from datetime import datetime

class ShipmentItemBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: float

class ShipmentItemCreate(ShipmentItemBase):
    pass

class ShipmentItemUpdate(BaseModel):
    quantity: Optional[int] = None
    unit_price: Optional[float] = None

class ShipmentItem(ShipmentItemBase):
    id: int
    shipment_id: int
    created_at: datetime

    @computed_field
    @property
    def total_price(self) -> float:
        return self.quantity * self.unit_price

    model_config = ConfigDict(from_attributes=True)

class BulkItemsCreate(BaseModel):
    items: list[ShipmentItemCreate]

class BulkItemsResponse(BaseModel):
    created_items: list[ShipmentItem]
    total_value: float

class CopyItemsRequest(BaseModel):
    source_shipment_id: int

class CopyItemsResponse(BaseModel):
    copied_items: int

class ShipmentSummary(BaseModel):
    total_value: float
    total_items: int
    unique_products: int
    total_weight_kg: float