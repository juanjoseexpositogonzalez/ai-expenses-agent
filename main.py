"""Main entry point for the application."""
import os

# Force CPU usage for docling before any imports
# This must be set before docling is imported anywhere
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["ACCELERATOR"] = "cpu"

import logging
from app.telegram.bot import create_bot

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """Main function to run the bot."""
    logger.info("Starting AI Expenses Agent...")
    
    # Create bot application
    application = create_bot()
    
    # Start polling (run_polling handles the event loop internally)
    logger.info("Starting bot polling...")
    application.run_polling()


if __name__ == "__main__":
    main()
