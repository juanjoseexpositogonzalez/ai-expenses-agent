"""Claude provider implementation."""
import base64
import json
import re
from datetime import datetime
from typing import Optional
from anthropic import Anthropic
from app.config import settings
from app.services.ai.base import AIProvider, ExpenseData

logger = __import__('logging').getLogger(__name__)


class ClaudeProvider(AIProvider):
    """Anthropic Claude provider for expense analysis."""
    
    def __init__(self):
        """Initialize Claude client."""
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required")
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    async def analyze_expense(
        self,
        text: Optional[str] = None,
        image: Optional[bytes] = None,
        pdf: Optional[bytes] = None
    ) -> ExpenseData:
        """Analyze expense using Claude."""
        if not any([text, image]):
            raise ValueError("At least one input (text or image) is required")
        
        system_message = """You are an expense analysis assistant. Extract the following information from the provided expense data:
- amount: The monetary amount (as a float number)
- currency: The currency code (ISO 4217, e.g., EUR, USD, GBP)
- description: A clear, concise description of what was purchased
- date: The date of the expense in YYYY-MM-DD format (use today's date if not found)
- category_name: One of these exact categories: Comida, Transporte, Alojamiento, Entretenimiento, Salud, Compras, Servicios, Otros

Return ONLY a valid JSON object with these exact keys: amount, currency, description, date, category_name.
Do not include any other text or explanation."""
        
        content = []
        
        # Add text if provided
        if text:
            content.append({
                "type": "text",
                "text": f"Analyze this expense information:\n\n{text}"
            })
        
        # Add image if provided
        if image:
            base64_image = base64.b64encode(image).decode('utf-8')
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": base64_image
                }
            })
        
        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                system=system_message,
                messages=[
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            )
            
            response_text = message.content[0].text
            
            # Try to extract JSON from response
            json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
            else:
                # Fallback parsing
                return self._parse_fallback(response_text)
            
            # Parse date
            try:
                expense_date = datetime.strptime(data.get("date", ""), "%Y-%m-%d")
            except (ValueError, TypeError):
                expense_date = datetime.now()
            
            return ExpenseData(
                amount=float(data.get("amount", 0.0)),
                currency=data.get("currency", "EUR").upper(),
                description=data.get("description", "Expense"),
                date=expense_date,
                category_name=data.get("category_name", "Otros")
            )
        
        except Exception as e:
            logger.error(f"Error analyzing expense with Claude: {e}")
            raise Exception(f"Failed to analyze expense: {str(e)}")
    
    def _parse_fallback(self, response_text: str) -> ExpenseData:
        """Fallback parsing if JSON parsing fails."""
        # Try to extract data using regex
        amount_match = re.search(r'"amount"\s*:\s*([\d.]+)', response_text)
        currency_match = re.search(r'"currency"\s*:\s*"([A-Z]{3})"', response_text)
        date_match = re.search(r'"date"\s*:\s*"(\d{4}-\d{2}-\d{2})"', response_text)
        category_match = re.search(r'"category_name"\s*:\s*"([^"]+)"', response_text)
        desc_match = re.search(r'"description"\s*:\s*"([^"]+)"', response_text)
        
        try:
            expense_date = datetime.strptime(date_match.group(1), "%Y-%m-%d") if date_match else datetime.now()
        except:
            expense_date = datetime.now()
        
        return ExpenseData(
            amount=float(amount_match.group(1)) if amount_match else 0.0,
            currency=(currency_match.group(1) if currency_match else "EUR").upper(),
            description=desc_match.group(1) if desc_match else "Expense",
            date=expense_date,
            category_name=category_match.group(1) if category_match else "Otros"
        )
