"""Telegram bot configuration and initialization."""
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from app.config import settings
from app.telegram.handlers import (
    start_command,
    handle_text_message,
    handle_photo,
    handle_document
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def create_bot() -> Application:
    """Create and configure Telegram bot."""
    if not settings.TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is required. Check your .env file.")
    
    logger.info("Creating Telegram bot application...")
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.Document.PDF, handle_document))
    
    logger.info("Handlers registered successfully")
    
    return application
