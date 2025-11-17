"""Service for processing image files."""
import logging
from pathlib import Path
from typing import Optional
from PIL import Image
from app.services.models import ProcessedDocument

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Processes image files for AI analysis."""
    
    def __init__(self, max_image_size: int = 5 * 1024 * 1024):  # 5MB default
        """
        Initialize image processor.
        
        Args:
            max_image_size: Maximum image file size in bytes (default: 5MB)
        """
        self.max_image_size = max_image_size
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.webp'}
    
    def process_image(self, file_path: Path) -> ProcessedDocument:
        """
        Process an image file and prepare it for AI analysis.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            ProcessedDocument with image bytes
            
        Raises:
            ValueError: If image format is not supported or size exceeds limit
            Exception: If image processing fails
        """
        try:
            # Validate file extension
            file_ext = file_path.suffix.lower()
            if file_ext not in self.supported_formats:
                raise ValueError(
                    f"Unsupported image format: {file_ext}. "
                    f"Supported formats: {', '.join(self.supported_formats)}"
                )
            
            # Check file size
            file_size = file_path.stat().st_size
            if file_size > self.max_image_size:
                raise ValueError(
                    f"Image size ({file_size} bytes) exceeds maximum "
                    f"allowed size ({self.max_image_size} bytes)"
                )
            
            logger.info(f"Processing image: {file_path}")
            
            # Open and validate image
            with Image.open(file_path) as img:
                # Convert to RGB if necessary (for JPEG compatibility)
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                
                # Get image metadata
                width, height = img.size
                format_name = img.format or file_ext[1:].upper()
                
                # Read image bytes
                # Save to bytes buffer
                from io import BytesIO
                buffer = BytesIO()
                img.save(buffer, format='JPEG', quality=95)
                image_bytes = buffer.getvalue()
            
            logger.info(
                f"Processed image: {width}x{height}, "
                f"{len(image_bytes)} bytes, format: {format_name}"
            )
            
            return ProcessedDocument(
                type="image",
                image_bytes=image_bytes,
                metadata={
                    "file_name": file_path.name,
                    "file_size": file_size,
                    "width": width,
                    "height": height,
                    "format": format_name
                }
            )
        
        except Exception as e:
            logger.error(f"Error processing image {file_path}: {e}")
            raise Exception(f"Failed to process image: {str(e)}")
    
    def validate_image(self, file_path: Path) -> bool:
        """
        Validate that a file is a valid image.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            True if image is valid, False otherwise
        """
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True
        except Exception as e:
            logger.warning(f"Image validation failed for {file_path}: {e}")
            return False

