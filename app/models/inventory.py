from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class Location(BaseModel):
    __tablename__ = "locations"

    name = Column(String(100), nullable=False)
    location_type = Column(String(50), nullable=False)
    address = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)
    is_active = Column(Boolean, default=True)

class Product(BaseModel):
    __tablename__ = "products"

    name = Column(String(100), nullable=False)
    sku = Column(String(50), unique=True, nullable=False)
    description = Column(String(500))
    unit_price = Column(Float, nullable=False)
    category = Column(String(50))
    weight_kg = Column(Float, default=0.0)  # Added weight

class Inventory(BaseModel):
    __tablename__ = "inventory"

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    quantity = Column(Integer, default=0)
    reserved_quantity = Column(Integer, default=0)  # Added reserved quantity
    min_stock_level = Column(Integer, default=10)

    # Relationships
    product = relationship("Product")
    location = relationship("Location")

    @property
    def available_quantity(self):
        return self.quantity - self.reserved_quantity
