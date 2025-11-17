"""Pydantic models for document processing."""
from pydantic import BaseModel
from typing import Optional


class ProcessedDocument(BaseModel):
    """Resultado del procesamiento de un documento."""
    type: str  # "pdf", "image", "text"
    text_content: Optional[str] = None  # Texto extraído (para PDFs)
    image_bytes: Optional[bytes] = None  # Bytes de imagen (para fotos)
    metadata: Optional[dict] = None  # Metadatos adicionales (nombre archivo, tamaño, etc.)

