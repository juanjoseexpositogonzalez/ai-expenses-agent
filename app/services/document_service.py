"""Unified service for processing documents from Telegram."""
import logging
from pathlib import Path
from telegram import Bot
from telegram import File as TelegramFile, PhotoSize
from app.services.file_downloader import FileDownloader
from app.services.document_processor import DocumentProcessor
from app.services.image_processor import ImageProcessor
from app.services.models import ProcessedDocument

logger = logging.getLogger(__name__)


class DocumentService:
    """Unified service for processing documents and images."""
    
    def __init__(
        self,
        max_pdf_size: int = 10 * 1024 * 1024,  # 10MB
        max_image_size: int = 5 * 1024 * 1024   # 5MB
    ):
        """
        Initialize document service.
        
        Args:
            max_pdf_size: Maximum PDF file size in bytes
            max_image_size: Maximum image file size in bytes
        """
        self.file_downloader = FileDownloader(max_file_size=max_pdf_size)
        self.document_processor = DocumentProcessor()
        self.image_processor = ImageProcessor(max_image_size=max_image_size)
    
    async def process_document(
        self,
        document: TelegramFile,
        bot: Bot
    ) -> ProcessedDocument:
        """
        Process a PDF document from Telegram.
        
        Args:
            document: Telegram File object (PDF)
            bot: Telegram Bot instance
            
        Returns:
            ProcessedDocument with extracted text content
        """
        temp_path = None
        try:
            # Download PDF
            temp_path = await self.file_downloader.download_telegram_file(
                document,
                bot,
                suffix='.pdf'
            )
            
            # Process PDF
            result = self.document_processor.process_pdf(temp_path)
            
            return result
        
        finally:
            # Clean up temporary file
            if temp_path:
                self.file_downloader.cleanup_temp_file(temp_path)
    
    async def process_photo(
        self,
        photo: PhotoSize,
        bot: Bot
    ) -> ProcessedDocument:
        """
        Process a photo from Telegram.
        
        Args:
            photo: Telegram PhotoSize object
            bot: Telegram Bot instance
            
        Returns:
            ProcessedDocument with image bytes
        """
        temp_path = None
        try:
            # Download photo
            temp_path = await self.file_downloader.download_telegram_file(
                photo,
                bot,
                suffix='.jpg'
            )
            
            # Process image
            result = self.image_processor.process_image(temp_path)
            
            return result
        
        finally:
            # Clean up temporary file
            if temp_path:
                self.file_downloader.cleanup_temp_file(temp_path)
    
    async def process_text(self, text: str) -> ProcessedDocument:
        """
        Process plain text message.
        
        Args:
            text: Text content
            
        Returns:
            ProcessedDocument with text content
        """
        return ProcessedDocument(
            type="text",
            text_content=text,
            metadata={"text_length": len(text)}
        )

