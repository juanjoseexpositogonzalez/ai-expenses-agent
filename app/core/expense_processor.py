"""Core expense processing logic."""
from datetime import datetime
from decimal import Decimal
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.database import get_session
from app.models import Expense, Category
from app.services.ai.base import AIProvider, ExpenseData
from app.services.currency import CurrencyService
from app.config import settings

logger = __import__('logging').getLogger(__name__)


class ExpenseProcessor:
    """Processes expenses from various sources."""
    
    def __init__(self, ai_provider: AIProvider):
        """Initialize expense processor."""
        self.ai_provider = ai_provider
        self.currency_service = CurrencyService()
    
    async def process_expense(
        self,
        text: str | None = None,
        image: bytes | None = None,
        pdf_text: str | None = None
    ) -> Expense:
        """
        Process an expense from text, image, or PDF text.
        
        Args:
            text: Text description of expense
            image: Image bytes (receipt photo)
            pdf_text: Extracted text from PDF
            
        Returns:
            Created Expense record
        """
        # Use PDF text if available, otherwise use regular text
        analysis_text = pdf_text if pdf_text else text
        
        # Analyze with AI
        expense_data = await self.ai_provider.analyze_expense(
            text=analysis_text,
            image=image
        )
        
        # Get or create category
        with get_session() as session:
            category = self._get_or_create_category(session, expense_data.category_name)
            
            # Convert currency if needed
            amount = Decimal(str(expense_data.amount))
            converted_amount = amount
            
            if expense_data.currency.upper() != settings.BASE_CURRENCY.upper():
                try:
                    converted_amount = await self.currency_service.convert(
                        amount=amount,
                        from_currency=expense_data.currency,
                        to_currency=settings.BASE_CURRENCY,
                        expense_date=expense_data.date.date()
                    )
                except Exception as e:
                    logger.warning(f"Currency conversion failed: {e}, using original amount")
                    converted_amount = amount
            
            # Create expense
            expense = Expense(
                amount=amount,
                currency=expense_data.currency.upper(),
                converted_amount=converted_amount,
                base_currency=settings.BASE_CURRENCY.upper(),
                description=expense_data.description,
                date=expense_data.date,
                category_id=category.id
            )
            
            session.add(expense)
            session.commit()
            session.refresh(expense)
            
            # Reload expense with category relationship
            statement = select(Expense).options(selectinload(Expense.category)).where(Expense.id == expense.id)
            expense = session.exec(statement).first()
            
            logger.info(f"Expense created: {expense.id} - {expense.amount} {expense.currency}")
            
            return expense
    
    def _get_or_create_category(self, session: Session, category_name: str) -> Category:
        """Get existing category or create a new one."""
        # Try to find existing category
        statement = select(Category).where(Category.name == category_name)
        category = session.exec(statement).first()
        
        if category:
            return category
        
        # Create new category (user-defined)
        category = Category(
            name=category_name,
            description=f"User-defined category: {category_name}",
            is_system=False
        )
        session.add(category)
        session.commit()
        session.refresh(category)
        
        logger.info(f"Created new category: {category_name}")
        
        return category
