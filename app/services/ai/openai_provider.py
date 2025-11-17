"""OpenAI provider implementation."""
import base64
import json
import re
from datetime import datetime
from typing import Optional
from openai import OpenAI
from app.config import settings
from app.services.ai.base import AIProvider, ExpenseData

logger = __import__('logging').getLogger(__name__)


class OpenAIProvider(AIProvider):
    """OpenAI GPT-4 Vision provider for expense analysis."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def analyze_expense(
        self,
        text: Optional[str] = None,
        image: Optional[bytes] = None,
        pdf: Optional[bytes] = None
    ) -> ExpenseData:
        """Analyze expense using OpenAI GPT-4 Vision."""
        if not any([text, image]):
            raise ValueError("At least one input (text or image) is required")
        
        # Build messages
        system_message = """You are an expense analysis assistant. Extract the following information from the provided expense data:
- amount: The monetary amount (as a float number)
- currency: The currency code (ISO 4217, e.g., EUR, USD, GBP)
- description: A clear, concise description of what was purchased
- date: The date of the expense in YYYY-MM-DD format (use today's date if not found)
- category_name: One of these exact categories: Comida, Transporte, Alojamiento, Entretenimiento, Salud, Compras, Servicios, Otros

Return ONLY a valid JSON object with these exact keys: amount, currency, description, date, category_name.
Do not include any other text or explanation."""
        
        messages = [{"role": "system", "content": system_message}]
        
        content_parts = []
        
        # Add text if provided
        if text:
            content_parts.append({
                "type": "text",
                "text": f"Analyze this expense information:\n\n{text}"
            })
        
        # Add image if provided
        if image:
            base64_image = base64.b64encode(image).decode('utf-8')
            content_parts.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })
        
        messages.append({
            "role": "user",
            "content": content_parts
        })
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # GPT-4o supports vision
                messages=messages,
                response_format={"type": "json_object"},
                max_tokens=500
            )
            
            response_text = response.choices[0].message.content
            
            # Parse JSON response
            data = json.loads(response_text)
            
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
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            # Fallback parsing
            return self._parse_fallback(response_text)
        except Exception as e:
            logger.error(f"Error analyzing expense with OpenAI: {e}")
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
