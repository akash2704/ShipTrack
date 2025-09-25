from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class ShipmentItem(BaseModel):
    __tablename__ = "shipment_items"

    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)

    # Relationships
    shipment = relationship("Shipment", back_populates="items")
    product = relationship("Product")

    @property
    def total_price(self):
        return self.quantity * self.unit_price