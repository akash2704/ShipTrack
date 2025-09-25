from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.core.database import get_db
from app.models.expense import Budget, BudgetLineItem, Expense, ExpenseCategory
from app.schemas.expense import BudgetCreate, Budget as BudgetSchema

router = APIRouter()

@router.post("/budgets/", response_model=BudgetSchema)
async def create_budget(budget: BudgetCreate, db: AsyncSession = Depends(get_db)):
    db_budget = Budget(**budget.model_dump())
    db.add(db_budget)
    await db.commit()
    await db.refresh(db_budget)
    return db_budget

@router.get("/budgets/", response_model=List[BudgetSchema])
async def get_budgets(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Budget))
    budgets = result.scalars().all()
    return budgets

@router.get("/budgets/{budget_id}/variance")
async def get_budget_variance(budget_id: int, db: AsyncSession = Depends(get_db)):
    """Get budget vs actual variance report"""
    budget_result = await db.execute(select(Budget).where(Budget.id == budget_id))
    budget = budget_result.scalar_one_or_none()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    # Get actual expenses for budget period
    actual_result = await db.execute(
        select(func.sum(Expense.amount_usd)).where(
            Expense.expense_date.between(budget.start_date, budget.end_date)
        )
    )
    actual_expenses = actual_result.scalar() or 0

    variance = float(budget.total_budget) - float(actual_expenses)
    variance_percentage = (variance / float(budget.total_budget)) * 100 if budget.total_budget > 0 else 0

    return {
        "budget_name": budget.name,
        "budgeted_amount": float(budget.total_budget),
        "actual_amount": float(actual_expenses),
        "variance": variance,
        "variance_percentage": variance_percentage,
        "period": f"{budget.start_date} to {budget.end_date}"
    }
