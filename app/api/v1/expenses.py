from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.models.expense import Expense, ExpenseCategory, Vendor
from app.schemas.expense import (
    ExpenseCreate, Expense as ExpenseSchema, ExpenseUpdate,
    ExpenseCategoryCreate, ExpenseCategory as ExpenseCategorySchema,
    VendorCreate, Vendor as VendorSchema, ExpenseReport
)

router = APIRouter()

# Expense Categories
@router.post("/expense-categories/", response_model=ExpenseCategorySchema)
async def create_expense_category(category: ExpenseCategoryCreate, db: AsyncSession = Depends(get_db)):
    db_category = ExpenseCategory(**category.model_dump())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category

@router.get("/expense-categories/", response_model=List[ExpenseCategorySchema])
async def get_expense_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ExpenseCategory).where(ExpenseCategory.is_active == True))
    categories = result.scalars().all()
    return categories

# Vendors
@router.post("/vendors/", response_model=VendorSchema)
async def create_vendor(vendor: VendorCreate, db: AsyncSession = Depends(get_db)):
    db_vendor = Vendor(**vendor.model_dump())
    db.add(db_vendor)
    await db.commit()
    await db.refresh(db_vendor)
    return db_vendor

@router.get("/vendors/", response_model=List[VendorSchema])
async def get_vendors(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Vendor).where(Vendor.is_active == True))
    vendors = result.scalars().all()
    return vendors

# Expenses
@router.post("/expenses/", response_model=ExpenseSchema)
async def create_expense(expense: ExpenseCreate, db: AsyncSession = Depends(get_db)):
    # Generate expense number
    count_result = await db.execute(select(func.count(Expense.id)))
    count = count_result.scalar() or 0
    expense_number = f"EXP-2024-{count + 1:04d}"

    # Calculate USD amount
    amount_usd = expense.amount * expense.exchange_rate if hasattr(expense, 'exchange_rate') else expense.amount

    db_expense = Expense(
        expense_number=expense_number,
        amount_usd=amount_usd,
        **expense.model_dump()
    )
    db.add(db_expense)
    await db.commit()
    await db.refresh(db_expense)
    return db_expense

@router.get("/expenses/", response_model=List[ExpenseSchema])
async def get_expenses(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Expense))
    expenses = result.scalars().all()
    return expenses

@router.get("/expenses/{expense_id}", response_model=ExpenseSchema)
async def get_expense(expense_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Expense).where(Expense.id == expense_id))
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@router.put("/expenses/{expense_id}", response_model=ExpenseSchema)
async def update_expense(expense_id: int, expense_update: ExpenseUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Expense).where(Expense.id == expense_id))
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    update_data = expense_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(expense, field, value)

    await db.commit()
    await db.refresh(expense)
    return expense

# Expense Workflow
@router.post("/expenses/{expense_id}/submit")
async def submit_expense(expense_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Expense).where(Expense.id == expense_id))
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    if expense.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft expenses can be submitted")

    expense.status = "submitted"
    expense.submitted_at = datetime.now()

    await db.commit()
    return {"message": "Expense submitted for approval"}

@router.post("/expenses/{expense_id}/approve")
async def approve_expense(expense_id: int, approval_data: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Expense).where(Expense.id == expense_id))
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    if expense.status != "submitted":
        raise HTTPException(status_code=400, detail="Only submitted expenses can be approved")

    expense.status = "approved"
    expense.approved_at = datetime.now()
    expense.approved_by_name = "Manager"  # Simplified for now

    await db.commit()
    return {"message": "Expense approved"}

@router.post("/expenses/{expense_id}/reject")
async def reject_expense(expense_id: int, rejection_data: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Expense).where(Expense.id == expense_id))
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    expense.status = "rejected"
    expense.rejection_reason = rejection_data.get("reason", "No reason provided")

    await db.commit()
    return {"message": "Expense rejected"}

# Reports
@router.get("/reports/expenses", response_model=ExpenseReport)
async def get_expense_report(db: AsyncSession = Depends(get_db)):
    # Get total expenses
    total_result = await db.execute(select(func.sum(Expense.amount_usd)))
    total_expenses = total_result.scalar() or 0

    # Get expense count
    count_result = await db.execute(select(func.count(Expense.id)))
    expense_count = count_result.scalar() or 0

    # Calculate average
    average_expense = total_expenses / expense_count if expense_count > 0 else 0

    # Get expenses by category (simplified)
    expenses_by_category = {"Office Supplies": float(total_expenses)}

    # Get expenses by status
    expenses_by_status = {"draft": expense_count}

    return ExpenseReport(
        total_expenses=total_expenses,
        expense_count=expense_count,
        average_expense=average_expense,
        expenses_by_category=expenses_by_category,
        expenses_by_status=expenses_by_status
    )
