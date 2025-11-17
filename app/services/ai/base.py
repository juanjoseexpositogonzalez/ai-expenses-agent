"""Base abstract class for AI providers."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ExpenseData:
    """Data extracted from expense analysis."""
    amount: float
    currency: str
    description: str
    date: datetime
    category_name: str


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    async def analyze_expense(
        self,
        text: Optional[str] = None,
        image: Optional[bytes] = None,
        pdf: Optional[bytes] = None
    ) -> ExpenseData:
        """
        Analyze an expense from text, image, or PDF.
        
        Args:
            text: Text description of the expense or extracted text from PDF
            image: Image bytes (e.g., photo of receipt)
            pdf: PDF bytes (e.g., invoice PDF) - not used directly, text should be extracted first
            
        Returns:
            ExpenseData with extracted information
            
        Raises:
            ValueError: If no input provided or analysis fails
        """
        pass
