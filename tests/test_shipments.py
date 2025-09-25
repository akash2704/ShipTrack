import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_shipments_empty_list(client: AsyncClient):
    """Test getting shipments returns empty list initially"""
    response = await client.get("/api/v1/shipments/")

    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_create_shipment_success(client: AsyncClient):
    """Test creating a shipment successfully"""
    # First create locations for origin and destination
    origin_data = {
        "name": "Origin Warehouse",
        "location_type": "warehouse",
        "address": "123 Origin St"
    }
    dest_data = {
        "name": "Destination Port",
        "location_type": "port",
        "address": "456 Dest Ave"
    }

    origin_response = await client.post("/api/v1/inventory/locations/", json=origin_data)
    dest_response = await client.post("/api/v1/inventory/locations/", json=dest_data)

    origin_id = origin_response.json()["id"]
    dest_id = dest_response.json()["id"]

    # Now create shipment
    shipment_data = {
        "tracking_number": "SHIP001",
        "origin_location_id": origin_id,
        "destination_location_id": dest_id,
        "status": "pending",
        "estimated_delivery": "2024-01-15T10:00:00"
    }

    response = await client.post("/api/v1/shipments/", json=shipment_data)

    assert response.status_code == 200
    data = response.json()
    assert data["tracking_number"] == "SHIP001"
    assert data["status"] == "pending"
    assert data["origin_location_id"] == origin_id
    assert data["destination_location_id"] == dest_id
    assert "id" in data

@pytest.mark.asyncio
async def test_get_shipment_by_id(client: AsyncClient):
    """Test getting a specific shipment by ID"""
    # Create locations first
    origin_data = {"name": "Test Origin", "location_type": "warehouse"}
    dest_data = {"name": "Test Dest", "location_type": "port"}

    origin_response = await client.post("/api/v1/inventory/locations/", json=origin_data)
    dest_response = await client.post("/api/v1/inventory/locations/", json=dest_data)

    # Create shipment
    shipment_data = {
        "tracking_number": "SHIP002",
        "origin_location_id": origin_response.json()["id"],
        "destination_location_id": dest_response.json()["id"],
        "status": "in_transit"
    }

    create_response = await client.post("/api/v1/shipments/", json=shipment_data)
    shipment_id = create_response.json()["id"]

    # Get shipment by ID
    response = await client.get(f"/api/v1/shipments/{shipment_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == shipment_id
    assert data["tracking_number"] == "SHIP002"

@pytest.mark.asyncio
async def test_update_shipment_status(client: AsyncClient):
    """Test updating shipment status"""
    # Create locations and shipment first
    origin_data = {"name": "Update Origin", "location_type": "warehouse"}
    dest_data = {"name": "Update Dest", "location_type": "port"}

    origin_response = await client.post("/api/v1/inventory/locations/", json=origin_data)
    dest_response = await client.post("/api/v1/inventory/locations/", json=dest_data)

    shipment_data = {
        "tracking_number": "SHIP003",
        "origin_location_id": origin_response.json()["id"],
        "destination_location_id": dest_response.json()["id"],
        "status": "pending"
    }

    create_response = await client.post("/api/v1/shipments/", json=shipment_data)
    shipment_id = create_response.json()["id"]

    # Update status
    update_data = {"status": "delivered"}
    response = await client.patch(f"/api/v1/shipments/{shipment_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "delivered"
