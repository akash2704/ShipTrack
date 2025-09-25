import pytest
from httpx import AsyncClient
from decimal import Decimal
from datetime import date

@pytest.mark.asyncio
async def test_create_expense_category(client: AsyncClient):
    """Test creating expense categories"""
    category_data = {
        "name": "Transportation",
        "code": "TRANS",
        "description": "Transportation related expenses"
    }

    response = await client.post("/api/v1/expense-categories/", json=category_data)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Transportation"
    assert data["code"] == "TRANS"
    assert "id" in data

@pytest.mark.asyncio
async def test_create_vendor(client: AsyncClient):
    """Test creating a vendor"""
    vendor_data = {
        "name": "ABC Fuel Company",
        "contact_person": "John Smith",
        "email": "john@abcfuel.com",
        "phone": "555-0123",
        "payment_terms": "Net 30"
    }

    response = await client.post("/api/v1/vendors/", json=vendor_data)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "ABC Fuel Company"
    assert data["contact_person"] == "John Smith"

@pytest.mark.asyncio
async def test_create_expense(client: AsyncClient):
    """Test creating an expense"""
    # First create category
    category_data = {"name": "Fuel Costs", "code": "FUEL"}
    category_response = await client.post("/api/v1/expense-categories/", json=category_data)
    category_id = category_response.json()["id"]

    # Create expense
    expense_data = {
        "amount": "150.75",
        "category_id": category_id,
        "expense_date": "2024-01-15",
        "description": "Fuel for delivery truck",
        "vendor_name": "Shell Gas Station",
        "invoice_number": "INV-001"
    }

    response = await client.post("/api/v1/expenses/", json=expense_data)

    assert response.status_code == 200
    data = response.json()
    assert float(data["amount"]) == 150.75
    assert data["description"] == "Fuel for delivery truck"
    assert data["status"] == "draft"
    assert "expense_number" in data

@pytest.mark.asyncio
async def test_expense_approval_workflow(client: AsyncClient):
    """Test expense approval workflow"""
    # Create category and expense
    category_data = {"name": "Vehicle Maintenance", "code": "MAINT"}
    category_response = await client.post("/api/v1/expense-categories/", json=category_data)
    category_id = category_response.json()["id"]

    expense_data = {
        "amount": "500.00",
        "category_id": category_id,
        "expense_date": "2024-01-15",
        "description": "Brake repair"
    }

    expense_response = await client.post("/api/v1/expenses/", json=expense_data)
    expense_id = expense_response.json()["id"]

    # Submit for approval
    submit_response = await client.post(f"/api/v1/expenses/{expense_id}/submit")
    assert submit_response.status_code == 200

    # Check status changed
    get_response = await client.get(f"/api/v1/expenses/{expense_id}")
    assert get_response.json()["status"] == "submitted"

    # Approve expense
    approve_response = await client.post(f"/api/v1/expenses/{expense_id}/approve",
                                       json={"comments": "Approved by manager"})
    assert approve_response.status_code == 200

    # Check status changed to approved
    final_response = await client.get(f"/api/v1/expenses/{expense_id}")
    assert final_response.json()["status"] == "approved"

@pytest.mark.asyncio
async def test_expense_reporting(client: AsyncClient):
    """Test expense reporting functionality"""
    # Create category and multiple expenses
    category_data = {"name": "Office Supplies", "code": "OFFICE"}
    category_response = await client.post("/api/v1/expense-categories/", json=category_data)
    category_id = category_response.json()["id"]

    # Create multiple expenses
    expenses = [
        {"amount": "25.50", "description": "Pens and paper"},
        {"amount": "75.00", "description": "Printer cartridges"},
        {"amount": "120.25", "description": "Office chair"}
    ]

    for expense_data in expenses:
        expense_data.update({
            "category_id": category_id,
            "expense_date": "2024-01-15"
        })
        await client.post("/api/v1/expenses/", json=expense_data)

    # Get expense report
    response = await client.get("/api/v1/reports/expenses")

    assert response.status_code == 200
    report = response.json()
    assert float(report["total_expenses"]) == 220.75
    assert report["expense_count"] == 3
    assert "expenses_by_category" in report
