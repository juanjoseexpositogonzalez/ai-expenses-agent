"""Category model for expense categorization."""
from datetime import datetime
from sqlmodel import SQLModel, Field


class Category(SQLModel, table=True):
    """Category model for grouping expenses."""
    
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: str | None = None
    is_system: bool = Field(default=False)  # True for predefined categories
    created_at: datetime = Field(default_factory=datetime.utcnow)
