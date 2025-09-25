from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.models.shipment_item import ShipmentItem
from app.models.shipment import Shipment
from app.models.inventory import Product
from app.services.inventory_service import InventoryService
from app.schemas.shipment_item import (
    ShipmentItemCreate, ShipmentItem as ShipmentItemSchema,
    ShipmentItemUpdate, BulkItemsCreate, BulkItemsResponse,
    CopyItemsRequest, CopyItemsResponse, ShipmentSummary
)

router = APIRouter()

@router.get("/{shipment_id}/items", response_model=List[ShipmentItemSchema])
async def get_shipment_items(shipment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ShipmentItem).where(ShipmentItem.shipment_id == shipment_id))
    items = result.scalars().all()
    return items

@router.post("/{shipment_id}/items", response_model=ShipmentItemSchema)
async def add_item_to_shipment(shipment_id: int, item: ShipmentItemCreate, db: AsyncSession = Depends(get_db)):
    # Get shipment with origin location
    shipment_result = await db.execute(select(Shipment).where(Shipment.id == shipment_id))
    shipment = shipment_result.scalar_one_or_none()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    # Reserve inventory if shipment is pending
    if shipment.status == "pending":
        reserved = await InventoryService.reserve_inventory(
            db, item.product_id, shipment.origin_location_id, item.quantity
        )
        if not reserved:
            raise HTTPException(status_code=400, detail="Insufficient inventory")

    db_item = ShipmentItem(shipment_id=shipment_id, **item.model_dump())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

@router.patch("/{shipment_id}/items/{item_id}", response_model=ShipmentItemSchema)
async def update_shipment_item(shipment_id: int, item_id: int, item_update: ShipmentItemUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ShipmentItem).where(
            ShipmentItem.id == item_id,
            ShipmentItem.shipment_id == shipment_id
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    await db.commit()
    await db.refresh(item)
    return item

@router.delete("/{shipment_id}/items/{item_id}")
async def remove_item_from_shipment(shipment_id: int, item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ShipmentItem).where(
            ShipmentItem.id == item_id,
            ShipmentItem.shipment_id == shipment_id
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    await db.delete(item)
    await db.commit()
    return {"message": "Item removed successfully"}

@router.post("/{shipment_id}/items/bulk", response_model=BulkItemsResponse)
async def bulk_add_items(shipment_id: int, bulk_data: BulkItemsCreate, db: AsyncSession = Depends(get_db)):
    shipment_result = await db.execute(select(Shipment).where(Shipment.id == shipment_id))
    if not shipment_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Shipment not found")

    created_items = []
    total_value = 0.0

    for item_data in bulk_data.items:
        db_item = ShipmentItem(shipment_id=shipment_id, **item_data.model_dump())
        db.add(db_item)
        created_items.append(db_item)
        total_value += item_data.quantity * item_data.unit_price

    await db.commit()

    for item in created_items:
        await db.refresh(item)

    return BulkItemsResponse(created_items=created_items, total_value=total_value)

@router.post("/{shipment_id}/items/copy", response_model=CopyItemsResponse)
async def copy_items_from_shipment(shipment_id: int, copy_data: CopyItemsRequest, db: AsyncSession = Depends(get_db)):
    source_result = await db.execute(
        select(ShipmentItem).where(ShipmentItem.shipment_id == copy_data.source_shipment_id)
    )
    source_items = source_result.scalars().all()

    if not source_items:
        raise HTTPException(status_code=404, detail="Source shipment not found or has no items")

    copied_count = 0
    for source_item in source_items:
        new_item = ShipmentItem(
            shipment_id=shipment_id,
            product_id=source_item.product_id,
            quantity=source_item.quantity,
            unit_price=source_item.unit_price
        )
        db.add(new_item)
        copied_count += 1

    await db.commit()
    return CopyItemsResponse(copied_items=copied_count)

@router.get("/{shipment_id}/summary", response_model=ShipmentSummary)
async def get_shipment_summary(shipment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ShipmentItem, Product).join(Product).where(ShipmentItem.shipment_id == shipment_id)
    )
    items_with_products = result.all()

    total_value = 0.0
    total_items = 0
    total_weight = 0.0
    unique_products = len(items_with_products)

    for item, product in items_with_products:
        total_value += item.quantity * item.unit_price
        total_items += item.quantity
        total_weight += item.quantity * (product.weight_kg or 0.0)

    return ShipmentSummary(
        total_value=total_value,
        total_items=total_items,
        unique_products=unique_products,
        total_weight_kg=total_weight
    )
