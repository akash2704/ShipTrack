from pydantic import BaseModel, ConfigDict, computed_field
from typing import Optional
from datetime import datetime

class LocationBase(BaseModel):
    name: str
    location_type: str
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class LocationCreate(LocationBase):
    pass

class Location(LocationBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProductBase(BaseModel):
    name: str
    sku: str
    description: Optional[str] = None
    unit_price: float
    category: Optional[str] = None
    weight_kg: Optional[float] = 0.0  # Added weight field

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Add the missing Inventory schemas
class InventoryBase(BaseModel):
    product_id: int
    location_id: int
    quantity: int
    reserved_quantity: Optional[int] = 0
    min_stock_level: Optional[int] = 10

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    quantity: Optional[int] = None
    reserved_quantity: Optional[int] = None
    min_stock_level: Optional[int] = None

class Inventory(InventoryBase):
    id: int
    created_at: datetime

    @computed_field
    @property
    def available_quantity(self) -> int:
        return self.quantity - (self.reserved_quantity or 0)

    model_config = ConfigDict(from_attributes=True)