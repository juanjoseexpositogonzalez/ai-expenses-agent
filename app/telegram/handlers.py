"""Telegram bot handlers."""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from app.services.document_service import DocumentService

logger = logging.getLogger(__name__)

# Initialize document service lazily to avoid initialization errors at import time
_document_service = None

def get_document_service() -> DocumentService:
    """Get or create document service instance."""
    global _document_service
    if _document_service is None:
        _document_service = DocumentService()
    return _document_service


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    logger.info(f"User {user.id} ({user.username}) started the bot")
    
    await update.message.reply_text(
        f"¡Hola {user.first_name}! 👋\n\n"
        "Soy tu asistente de gastos con IA.\n"
        "Puedes enviarme:\n"
        "• Texto con tus gastos\n"
        "• Fotos de facturas\n"
        "• PDFs de facturas\n\n"
        "¡Empieza enviándome un gasto!"
    )


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages."""
    user = update.effective_user
    text = update.message.text
    
    logger.info(f"Received text from user {user.id}: {text}")
    
    try:
        # Process text
        document_service = get_document_service()
        processed = await document_service.process_text(text)
        
        await update.message.reply_text(
            f"✅ Texto recibido:\n\n{text}\n\n"
            "📝 Procesando gasto con IA..."
        )
        
        # TODO: Send to AI for analysis
        logger.info(f"Processed text: {len(processed.text_content or '')} characters")
        
    except Exception as e:
        logger.error(f"Error processing text: {e}")
        await update.message.reply_text(
            "❌ Error al procesar el texto. Por favor, inténtalo de nuevo."
        )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle photo messages."""
    user = update.effective_user
    photo = update.message.photo[-1]  # Get highest resolution
    
    logger.info(f"Received photo from user {user.id}, file_id: {photo.file_id}")
    
    try:
        # Send initial feedback
        status_msg = await update.message.reply_text("📥 Descargando imagen...")
        
        # Process photo
        document_service = get_document_service()
        processed = await document_service.process_photo(photo, context.bot)
        
        await status_msg.edit_text("📄 Procesando imagen...")
        
        await status_msg.edit_text(
            f"✅ Imagen procesada:\n"
            f"• Tamaño: {processed.metadata.get('width')}x{processed.metadata.get('height')}\n"
            f"• Formato: {processed.metadata.get('format')}\n\n"
            "🤖 Analizando con IA..."
        )
        
        # TODO: Send to AI for analysis
        logger.info(
            f"Processed image: {processed.metadata.get('file_name')}, "
            f"{len(processed.image_bytes or b'')} bytes"
        )
        
    except ValueError as e:
        logger.warning(f"Validation error processing photo: {e}")
        await update.message.reply_text(
            f"⚠️ {str(e)}\n\nPor favor, envía una imagen válida."
        )
    except Exception as e:
        logger.error(f"Error processing photo: {e}")
        await update.message.reply_text(
            "❌ Error al procesar la imagen. Por favor, inténtalo de nuevo."
        )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle document messages (PDFs, etc.)."""
    user = update.effective_user
    document = update.message.document
    
    logger.info(
        f"Received document from user {user.id}: "
        f"{document.file_name} ({document.file_size} bytes, "
        f"mime_type: {document.mime_type})"
    )
    
    # Only process PDFs for now
    if document.mime_type != "application/pdf":
        await update.message.reply_text(
            "⚠️ Solo se pueden procesar archivos PDF por ahora.\n"
            "Por favor, envía un archivo PDF."
        )
        return
    
    try:
        # Send initial feedback
        status_msg = await update.message.reply_text("📥 Descargando PDF...")
        
        # Process PDF
        document_service = get_document_service()
        processed = await document_service.process_document(document, context.bot)
        
        await status_msg.edit_text("📄 Procesando PDF con docling...")
        
        text_length = len(processed.text_content or "")
        await status_msg.edit_text(
            f"✅ PDF procesado:\n"
            f"• Nombre: {processed.metadata.get('file_name')}\n"
            f"• Texto extraído: {text_length} caracteres\n\n"
            "🤖 Analizando con IA..."
        )
        
        # TODO: Send to AI for analysis
        logger.info(
            f"Processed PDF: {processed.metadata.get('file_name')}, "
            f"{text_length} characters extracted"
        )
        
    except ValueError as e:
        logger.warning(f"Validation error processing PDF: {e}")
        await update.message.reply_text(
            f"⚠️ {str(e)}\n\nPor favor, envía un PDF válido."
        )
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        await update.message.reply_text(
            "❌ Error al procesar el PDF. Por favor, inténtalo de nuevo.\n"
            f"Error: {str(e)}"
        )

