from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import BaseModel

class LocationUpdate(BaseModel):
    __tablename__ = "location_updates"

    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    speed = Column(Float, nullable=True)
    heading = Column(Float, nullable=True)

    # Relationships
    shipment = relationship("Shipment")
