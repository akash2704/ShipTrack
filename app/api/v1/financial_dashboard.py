from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, extract
from datetime import datetime, date
from decimal import Decimal

from app.core.database import get_db
from app.models.expense import Expense, ExpenseCategory
from app.schemas.expense import FinancialKPIs

router = APIRouter()

@router.get("/dashboard/financial-kpis", response_model=FinancialKPIs)
async def get_financial_kpis(db: AsyncSession = Depends(get_db)):
    """Get real-time financial KPIs for dashboard"""
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Total monthly expenses
    monthly_result = await db.execute(
        select(func.sum(Expense.amount_usd)).where(
            and_(
                extract('month', Expense.expense_date) == current_month,
                extract('year', Expense.expense_date) == current_year
            )
        )
    )
    total_monthly_expenses = monthly_result.scalar() or Decimal('0')

    # Expense growth rate (simplified - comparing to last month)
    last_month = current_month - 1 if current_month > 1 else 12
    last_month_year = current_year if current_month > 1 else current_year - 1

    last_month_result = await db.execute(
        select(func.sum(Expense.amount_usd)).where(
            and_(
                extract('month', Expense.expense_date) == last_month,
                extract('year', Expense.expense_date) == last_month_year
            )
        )
    )
    last_month_expenses = last_month_result.scalar() or Decimal('1')

    growth_rate = float((total_monthly_expenses - last_month_expenses) / last_month_expenses * 100)

    # Top expense categories
    category_result = await db.execute(
        select(
            ExpenseCategory.name,
            func.sum(Expense.amount_usd).label('total')
        ).join(Expense, Expense.category_id == ExpenseCategory.id)
        .group_by(ExpenseCategory.name)
        .order_by(func.sum(Expense.amount_usd).desc())
        .limit(5)
    )

    top_categories = [
        {"category": row.name, "amount": float(row.total)}
        for row in category_result.all()
    ]

    # Pending approvals count
    pending_result = await db.execute(
        select(func.count(Expense.id)).where(Expense.status == 'submitted')
    )
    pending_approvals = pending_result.scalar() or 0

    return FinancialKPIs(
        total_monthly_expenses=total_monthly_expenses,
        expense_growth_rate=growth_rate,
        top_expense_categories=top_categories,
        pending_approvals_count=pending_approvals,
        budget_utilization=75.5  # Placeholder
    )

@router.get("/dashboard/expense-trends")
async def get_expense_trends(db: AsyncSession = Depends(get_db)):
    """Get expense trends for charts"""
    # Get monthly expenses for the last 6 months
    result = await db.execute(
        select(
            extract('month', Expense.expense_date).label('month'),
            extract('year', Expense.expense_date).label('year'),
            func.sum(Expense.amount_usd).label('total')
        ).group_by(
            extract('month', Expense.expense_date),
            extract('year', Expense.expense_date)
        ).order_by(
            extract('year', Expense.expense_date),
            extract('month', Expense.expense_date)
        ).limit(6)
    )

    trends = [
        {
            "period": f"{int(row.year)}-{int(row.month):02d}",
            "amount": float(row.total)
        }
        for row in result.all()
    ]

    return {"expense_trends": trends}