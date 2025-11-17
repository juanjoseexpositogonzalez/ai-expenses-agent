"""Expense model for storing expense records."""
from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.category import Category


class Expense(SQLModel, table=True):
    """Expense model for storing expense records."""
    
    id: int | None = Field(default=None, primary_key=True)
    amount: Decimal = Field(max_digits=12, decimal_places=2)
    currency: str = Field(max_length=3)  # ISO 4217 currency code
    converted_amount: Decimal | None = Field(default=None, max_digits=12, decimal_places=2)
    base_currency: str = Field(max_length=3)  # User's preferred currency
    description: str
    date: datetime = Field(index=True)
    category_id: int = Field(foreign_key="category.id", index=True)
    user_id: str | None = Field(default=None, index=True)  # For future multi-user support
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    category: "Category" = Relationship()
