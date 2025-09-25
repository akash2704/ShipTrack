from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import BaseModel

class ExpenseCategory(BaseModel):
    __tablename__ = "expense_categories"

    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True)
    parent_id = Column(Integer, ForeignKey("expense_categories.id"))
    description = Column(Text)
    is_active = Column(Boolean, default=True)

    # Self-referential relationship for hierarchy
    parent = relationship("ExpenseCategory", remote_side="ExpenseCategory.id")
    children = relationship("ExpenseCategory", back_populates="parent")

class Vendor(BaseModel):
    __tablename__ = "vendors"

    name = Column(String(200), nullable=False)
    contact_person = Column(String(100))
    email = Column(String(100))
    phone = Column(String(50))
    address = Column(Text)
    tax_id = Column(String(50))
    payment_terms = Column(String(50))
    is_active = Column(Boolean, default=True)

class Expense(BaseModel):
    __tablename__ = "expenses"

    expense_number = Column(String(50), unique=True)
    amount = Column(Numeric(15,2), nullable=False)
    currency = Column(String(3), default='USD')
    exchange_rate = Column(Numeric(10,6), default=1.0)
    amount_usd = Column(Numeric(15,2))

    # Categories
    category_id = Column(Integer, ForeignKey("expense_categories.id"))
    subcategory_id = Column(Integer, ForeignKey("expense_categories.id"))

    # Linking to operational entities
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=True)

    # Vendor information
    vendor_name = Column(String(200))
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    invoice_number = Column(String(100))

    # Expense details
    expense_date = Column(Date, nullable=False)
    description = Column(Text)
    notes = Column(Text)
    receipt_urls = Column(Text)  # Changed from ARRAY to Text for SQLite compatibility

    # Workflow and approval
    status = Column(String(20), default='draft')
    submitted_at = Column(DateTime)
    approved_at = Column(DateTime)
    rejection_reason = Column(Text)

    # User tracking (simplified for now)
    created_by_name = Column(String(100))
    approved_by_name = Column(String(100))

    # Reimbursement tracking
    is_reimbursable = Column(Boolean, default=False)
    reimbursed_at = Column(DateTime)
    reimbursement_amount = Column(Numeric(15,2))

    # Relationships
    category = relationship("ExpenseCategory", foreign_keys=[category_id])
    subcategory = relationship("ExpenseCategory", foreign_keys=[subcategory_id])
    vendor = relationship("Vendor")
    shipment = relationship("Shipment")

class Budget(BaseModel):
    __tablename__ = "budgets"

    name = Column(String(100))
    fiscal_year = Column(Integer)
    period_type = Column(String(20))
    start_date = Column(Date)
    end_date = Column(Date)
    total_budget = Column(Numeric(15,2))
    created_by_name = Column(String(100))

class BudgetLineItem(BaseModel):
    __tablename__ = "budget_line_items"

    budget_id = Column(Integer, ForeignKey("budgets.id"))
    category_id = Column(Integer, ForeignKey("expense_categories.id"))
    budgeted_amount = Column(Numeric(15,2))
    actual_amount = Column(Numeric(15,2), default=0)
    variance_percentage = Column(Numeric(5,2))
    notes = Column(Text)

    # Relationships
    budget = relationship("Budget")
    category = relationship("ExpenseCategory")
