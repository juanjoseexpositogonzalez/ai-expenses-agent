"""Currency conversion service using ExchangeRate API."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
import httpx
from app.config import settings

logger = __import__('logging').getLogger(__name__)


class CurrencyService:
    """Service for currency conversion."""
    
    BASE_URL = "https://api.exchangerate-api.com/v4"
    
    def __init__(self):
        """Initialize currency service."""
        self.api_key = settings.EXCHANGE_RATE_API_KEY
        self.base_currency = settings.BASE_CURRENCY
        self._cache: dict[str, float] = {}  # Cache for exchange rates
    
    async def convert(
        self,
        amount: Decimal,
        from_currency: str,
        to_currency: Optional[str] = None,
        expense_date: Optional[date] = None
    ) -> Decimal:
        """
        Convert amount from one currency to another.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code (ISO 4217)
            to_currency: Target currency code (defaults to base_currency)
            expense_date: Date for historical rates (defaults to today)
            
        Returns:
            Converted amount
        """
        if to_currency is None:
            to_currency = self.base_currency
        
        if from_currency.upper() == to_currency.upper():
            return amount
        
        # Use today if no date provided
        if expense_date is None:
            expense_date = date.today()
        
        # Get exchange rate
        rate = await self.get_exchange_rate(from_currency, to_currency, expense_date)
        
        return Decimal(str(amount * Decimal(str(rate))))
    
    async def get_exchange_rate(
        self,
        from_currency: str,
        to_currency: str,
        expense_date: Optional[date] = None
    ) -> float:
        """
        Get exchange rate between two currencies.
        
        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            expense_date: Date for historical rates (defaults to today)
            
        Returns:
            Exchange rate
        """
        if expense_date is None:
            expense_date = date.today()
        
        cache_key = f"{from_currency}_{to_currency}_{expense_date}"
        
        # Check cache
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            # ExchangeRate API free tier - use latest rates
            # For historical rates, you might need a paid plan
            url = f"{self.BASE_URL}/latest/{from_currency.upper()}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                # Cache the rate
                if "rates" in data:
                    rate = data["rates"].get(to_currency.upper(), 1.0)
                    self._cache[cache_key] = rate
                    return rate
                else:
                    # Fallback: try direct conversion
                    return await self._get_direct_rate(from_currency, to_currency)
        
        except Exception as e:
            logger.warning(f"Error fetching exchange rate: {e}, using 1.0")
            # Fallback to 1.0 if API fails
            return 1.0
    
    async def _get_direct_rate(self, from_currency: str, to_currency: str) -> float:
        """Get direct exchange rate via USD intermediate."""
        try:
            # Convert via USD if direct rate not available
            if from_currency.upper() != "USD":
                from_rate = await self._fetch_rate("USD", from_currency)
            else:
                from_rate = 1.0
            
            if to_currency.upper() != "USD":
                to_rate = await self._fetch_rate("USD", to_currency)
            else:
                to_rate = 1.0
            
            return to_rate / from_rate if from_rate != 0 else 1.0
        
        except Exception:
            return 1.0
    
    async def _fetch_rate(self, base: str, target: str) -> float:
        """Fetch rate from API."""
        url = f"{self.BASE_URL}/latest/{base.upper()}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            return data.get("rates", {}).get(target.upper(), 1.0)
