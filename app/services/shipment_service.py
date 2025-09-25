from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime

from app.models.shipment import Shipment
from app.models.shipment_item import ShipmentItem
from app.schemas.shipment import ShipmentCreate, ShipmentUpdate
from app.services.inventory_service import InventoryService
from app.core.websocket_manager import manager

class ShipmentService:
    @staticmethod
    async def get_all_shipments(db: AsyncSession) -> List[Shipment]:
        result = await db.execute(select(Shipment))
        return result.scalars().all()

    @staticmethod
    async def create_shipment(db: AsyncSession, shipment_data: ShipmentCreate) -> Shipment:
        db_shipment = Shipment(**shipment_data.model_dump())
        db.add(db_shipment)
        await db.commit()
        await db.refresh(db_shipment)
        return db_shipment

    @staticmethod
    async def get_shipment_by_id(db: AsyncSession, shipment_id: int) -> Optional[Shipment]:
        result = await db.execute(select(Shipment).where(Shipment.id == shipment_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_shipment(db: AsyncSession, shipment: Shipment, update_data: ShipmentUpdate) -> Shipment:
        old_status = shipment.status

        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(shipment, field, value)

        # Handle status changes that affect inventory
        if "status" in update_dict:
            new_status = update_dict["status"]
            await ShipmentService._handle_status_change(db, shipment, old_status, new_status)

            # Broadcast status change to WebSocket subscribers
            await manager.broadcast_to_shipment({
                "type": "status_update",
                "shipment_id": shipment.id,
                "old_status": old_status,
                "new_status": new_status,
                "tracking_number": shipment.tracking_number,
                "timestamp": datetime.now().isoformat()  # Use current time instead
            }, shipment.id)

        await db.commit()
        await db.refresh(shipment)
        return shipment

    @staticmethod
    async def _handle_status_change(db: AsyncSession, shipment: Shipment, old_status: str, new_status: str):
        """Handle inventory changes when shipment status changes"""
        items_result = await db.execute(select(ShipmentItem).where(ShipmentItem.shipment_id == shipment.id))
        items = items_result.scalars().all()

        if new_status == "dispatched" and old_status == "pending":
            for item in items:
                await InventoryService.move_inventory(
                    db, item.product_id, shipment.origin_location_id,
                    shipment.destination_location_id, item.quantity
                )

        elif new_status == "cancelled":
            for item in items:
                await InventoryService.release_reservation(
                    db, item.product_id, shipment.origin_location_id, item.quantity
                )