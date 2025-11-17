"""Service for downloading files from Telegram."""
import logging
import tempfile
import os
from pathlib import Path
from telegram import Bot
from telegram import File as TelegramFile

logger = logging.getLogger(__name__)


class FileDownloader:
    """Handles downloading files from Telegram."""
    
    def __init__(self, max_file_size: int = 10 * 1024 * 1024):  # 10MB default
        """
        Initialize file downloader.
        
        Args:
            max_file_size: Maximum file size in bytes (default: 10MB)
        """
        self.max_file_size = max_file_size
    
    async def download_telegram_file(
        self,
        file: TelegramFile,
        bot: Bot,
        suffix: str = None
    ) -> Path:
        """
        Download a file from Telegram to a temporary location.
        
        Args:
            file: Telegram File object
            bot: Telegram Bot instance
            suffix: Optional suffix for the temporary file (e.g., '.pdf', '.jpg')
            
        Returns:
            Path to the downloaded temporary file
            
        Raises:
            ValueError: If file exceeds maximum size
            Exception: If download fails
        """
        # Check file size
        if file.file_size and file.file_size > self.max_file_size:
            raise ValueError(
                f"File size ({file.file_size} bytes) exceeds maximum "
                f"allowed size ({self.max_file_size} bytes)"
            )
        
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix or "",
                prefix="telegram_"
            )
            temp_path = Path(temp_file.name)
            temp_file.close()
            
            logger.info(f"Downloading file {file.file_id} to {temp_path}")
            
            # Download file
            downloaded_file = await bot.get_file(file.file_id)
            await downloaded_file.download_to_drive(temp_path)
            
            logger.info(f"File downloaded successfully to {temp_path}")
            
            return temp_path
        
        except Exception as e:
            # Clean up on error
            if 'temp_path' in locals() and temp_path.exists():
                self.cleanup_temp_file(temp_path)
            logger.error(f"Error downloading file: {e}")
            raise
    
    @staticmethod
    def cleanup_temp_file(file_path: Path) -> None:
        """
        Remove a temporary file.
        
        Args:
            file_path: Path to the file to remove
        """
        try:
            if file_path.exists():
                file_path.unlink()
                logger.debug(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.warning(f"Error cleaning up temporary file {file_path}: {e}")

