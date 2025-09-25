from pydantic import BaseModel, ConfigDict, computed_field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

class ExpenseCategoryBase(BaseModel):
    name: str
    code: Optional[str] = None
    parent_id: Optional[int] = None
    description: Optional[str] = None
    is_active: bool = True

class ExpenseCategoryCreate(ExpenseCategoryBase):
    pass

class ExpenseCategory(ExpenseCategoryBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class VendorBase(BaseModel):
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_id: Optional[str] = None
    payment_terms: Optional[str] = None
    is_active: bool = True

class VendorCreate(VendorBase):
    pass

class Vendor(VendorBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ExpenseBase(BaseModel):
    amount: Decimal
    currency: str = 'USD'
    category_id: int
    subcategory_id: Optional[int] = None
    shipment_id: Optional[int] = None
    vendor_name: Optional[str] = None
    vendor_id: Optional[int] = None
    invoice_number: Optional[str] = None
    expense_date: date
    description: str
    notes: Optional[str] = None
    is_reimbursable: bool = False

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    amount: Optional[Decimal] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None

class Expense(ExpenseBase):
    id: int
    expense_number: str
    amount_usd: Optional[Decimal] = None
    status: str
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    created_by_name: Optional[str] = None
    approved_by_name: Optional[str] = None
    receipt_urls: Optional[str] = None  # Changed to string
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BudgetBase(BaseModel):
    name: str
    fiscal_year: int
    period_type: str
    start_date: date
    end_date: date
    total_budget: Decimal

class BudgetCreate(BudgetBase):
    pass

class Budget(BudgetBase):
    id: int
    created_by_name: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Financial Reports
class ExpenseReport(BaseModel):
    total_expenses: Decimal
    expense_count: int
    average_expense: Decimal
    expenses_by_category: dict
    expenses_by_status: dict

class FinancialKPIs(BaseModel):
    total_monthly_expenses: Decimal
    expense_growth_rate: float
    top_expense_categories: List[dict]
    pending_approvals_count: int
    budget_utilization: float