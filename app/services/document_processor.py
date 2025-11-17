"""Service for processing PDF documents using docling."""
import logging
import os
from pathlib import Path

# Force CPU usage before importing docling to avoid CUDA issues
# Hide CUDA devices to force CPU usage
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["ACCELERATOR"] = "cpu"

from docling.document_converter import DocumentConverter
from app.services.models import ProcessedDocument

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Processes PDF documents using docling."""
    
    def __init__(self):
        """Initialize document processor with docling converter."""
        # Initialize converter - docling handles PDFs by default
        # CPU mode is enforced at module level via ACCELERATOR env var
        self.converter = DocumentConverter()
    
    def process_pdf(self, file_path: Path) -> ProcessedDocument:
        """
        Process a PDF file and extract text content.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            ProcessedDocument with extracted text content
            
        Raises:
            Exception: If PDF processing fails
        """
        try:
            logger.info(f"Processing PDF: {file_path}")
            
            # Convert PDF to document model
            result = self.converter.convert(str(file_path))
            
            # Extract text content
            text_content = result.document.export_to_markdown()
            
            # If markdown is empty, try to get plain text
            if not text_content or not text_content.strip():
                # Fallback: try to extract text from document structure
                text_content = self._extract_text_from_document(result.document)
            
            logger.info(f"Extracted {len(text_content)} characters from PDF")
            
            return ProcessedDocument(
                type="pdf",
                text_content=text_content,
                metadata={
                    "file_name": file_path.name,
                    "file_size": file_path.stat().st_size if file_path.exists() else None,
                    "text_length": len(text_content)
                }
            )
        
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {e}")
            raise Exception(f"Failed to process PDF: {str(e)}")
    
    def _extract_text_from_document(self, document) -> str:
        """
        Extract plain text from docling document structure.
        
        Args:
            document: Docling document object
            
        Returns:
            Plain text content
        """
        text_parts = []
        
        # Try to extract text from document sections
        if hasattr(document, 'sections'):
            for section in document.sections:
                if hasattr(section, 'text'):
                    text_parts.append(section.text)
                elif hasattr(section, 'content'):
                    # Recursively extract from content
                    for item in section.content:
                        if hasattr(item, 'text'):
                            text_parts.append(item.text)
        
        return "\n".join(text_parts) if text_parts else ""

