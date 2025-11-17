"""Configuration management using python-decouple."""
from decouple import config
from typing import Literal


class Settings:
    """Application settings loaded from environment variables."""
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = config("TELEGRAM_BOT_TOKEN")
    
    # Database
    DATABASE_URL: str = config(
        "DATABASE_URL",
        default="postgresql://expenses_user:expenses_pass@localhost:5432/expenses_db"
    )
    
    # AI Provider
    AI_PROVIDER: Literal["openai", "claude"] = config("AI_PROVIDER", default="openai")
    OPENAI_API_KEY: str = config("OPENAI_API_KEY", default="")
    ANTHROPIC_API_KEY: str = config("ANTHROPIC_API_KEY", default="")
    
    # Currency
    EXCHANGE_RATE_API_KEY: str = config("EXCHANGE_RATE_API_KEY", default="")
    BASE_CURRENCY: str = config("BASE_CURRENCY", default="EUR")
    
    # Email
    SMTP_HOST: str = config("SMTP_HOST", default="smtp.gmail.com")
    SMTP_PORT: int = config("SMTP_PORT", default=587, cast=int)
    SMTP_USER: str = config("SMTP_USER", default="")
    SMTP_PASSWORD: str = config("SMTP_PASSWORD", default="")
    REPORT_EMAIL: str = config("REPORT_EMAIL", default="")
    
    # Reports
    REPORT_FREQUENCY: Literal["weekly", "biweekly"] = config("REPORT_FREQUENCY", default="weekly")


settings = Settings()
