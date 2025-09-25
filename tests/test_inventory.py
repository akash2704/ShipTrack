import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_locations_empty_list(client: AsyncClient):
    """Test getting locations returns empty list initially"""
    response = await client.get("/api/v1/inventory/locations/")

    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_create_location_success(client: AsyncClient):
    """Test creating a location successfully"""
    location_data = {
        "name": "Main Warehouse",
        "location_type": "warehouse",
        "address": "123 Main St",
        "latitude": 40.7128,
        "longitude": -74.0060
    }

    response = await client.post("/api/v1/inventory/locations/", json=location_data)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Main Warehouse"
    assert data["location_type"] == "warehouse"
    assert "id" in data

@pytest.mark.asyncio
async def test_create_location_missing_required_fields(client: AsyncClient):
    """Test creating location with missing required fields fails"""
    incomplete_data = {
        "name": "Test Warehouse"
        # Missing location_type
    }

    response = await client.post("/api/v1/inventory/locations/", json=incomplete_data)
    assert response.status_code == 422  # Validation error