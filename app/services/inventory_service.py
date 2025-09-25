from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.inventory import Inventory

class InventoryService:
    @staticmethod
    async def reserve_inventory(db: AsyncSession, product_id: int, location_id: int, quantity: int) -> bool:
        """Reserve inventory for a shipment"""
        result = await db.execute(
            select(Inventory).where(
                Inventory.product_id == product_id,
                Inventory.location_id == location_id
            )
        )
        inventory = result.scalar_one_or_none()

        if inventory and inventory.available_quantity >= quantity:
            inventory.reserved_quantity = (inventory.reserved_quantity or 0) + quantity
            await db.commit()
            await db.refresh(inventory)
            return True
        return False

    @staticmethod
    async def move_inventory(db: AsyncSession, product_id: int, from_location_id: int, to_location_id: int, quantity: int):
        """Move inventory from one location to another"""
        # Get source inventory
        source_result = await db.execute(
            select(Inventory).where(
                Inventory.product_id == product_id,
                Inventory.location_id == from_location_id
            )
        )
        source_inventory = source_result.scalar_one_or_none()

        if source_inventory:
            # Remove from source (including reserved)
            source_inventory.quantity -= quantity
            source_inventory.reserved_quantity = max(0, (source_inventory.reserved_quantity or 0) - quantity)

        # Get or create destination inventory
        dest_result = await db.execute(
            select(Inventory).where(
                Inventory.product_id == product_id,
                Inventory.location_id == to_location_id
            )
        )
        dest_inventory = dest_result.scalar_one_or_none()

        if dest_inventory:
            dest_inventory.quantity += quantity
        else:
            # Create new inventory record at destination
            new_inventory = Inventory(
                product_id=product_id,
                location_id=to_location_id,
                quantity=quantity,
                reserved_quantity=0
            )
            db.add(new_inventory)

        await db.commit()

    @staticmethod
    async def release_reservation(db: AsyncSession, product_id: int, location_id: int, quantity: int):
        """Release reserved inventory back to available"""
        result = await db.execute(
            select(Inventory).where(
                Inventory.product_id == product_id,
                Inventory.location_id == location_id
            )
        )
        inventory = result.scalar_one_or_none()

        if inventory:
            inventory.reserved_quantity = max(0, (inventory.reserved_quantity or 0) - quantity)
            await db.commit()
            await db.refresh(inventory)
