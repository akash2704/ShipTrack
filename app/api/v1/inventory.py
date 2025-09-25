from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.models.inventory import Location, Product
from app.schemas.inventory import LocationCreate, Location as LocationSchema, ProductCreate, Product as ProductSchema

router = APIRouter()

@router.post("/locations/", response_model=LocationSchema)
async def create_location(location: LocationCreate, db: AsyncSession = Depends(get_db)):
    db_location = Location(**location.model_dump())  # Changed from .dict()
    db.add(db_location)
    await db.commit()
    await db.refresh(db_location)
    return db_location

@router.post("/products/", response_model=ProductSchema)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    db_product = Product(**product.model_dump())  # Changed from .dict()
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

@router.get("/locations/", response_model=List[LocationSchema])
async def get_locations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Location))
    locations = result.scalars().all()
    return locations


@router.get("/products/", response_model=List[ProductSchema])
async def get_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    products = result.scalars().all()
    return products