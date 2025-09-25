from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class Shipment(BaseModel):
    __tablename__ = "shipments"

    tracking_number = Column(String(50), unique=True, nullable=False)
    origin_location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    destination_location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    status = Column(String(50), default="pending")
    estimated_delivery = Column(DateTime, nullable=True)

    # Relationships
    origin_location = relationship("Location", foreign_keys=[origin_location_id])
    destination_location = relationship("Location", foreign_keys=[destination_location_id])
    items = relationship("ShipmentItem", back_populates="shipment", cascade="all, delete-orphan")
