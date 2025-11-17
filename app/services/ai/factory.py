"""Factory for creating AI providers."""
from app.config import settings
from app.services.ai.base import AIProvider
from app.services.ai.openai_provider import OpenAIProvider
from app.services.ai.claude_provider import ClaudeProvider

logger = __import__('logging').getLogger(__name__)


def create_ai_provider() -> AIProvider:
    """
    Create an AI provider based on configuration.
    
    Returns:
        AIProvider instance
        
    Raises:
        ValueError: If provider is not configured correctly
    """
    # Clean provider name (remove comments, whitespace, quotes)
    provider_name = settings.AI_PROVIDER.lower().strip()
    # Remove any comments after #
    if '#' in provider_name:
        provider_name = provider_name.split('#')[0].strip()
    # Remove quotes if present
    provider_name = provider_name.strip('"\'')
    
    if provider_name == "openai":
        logger.info("Creating OpenAI provider")
        return OpenAIProvider()
    elif provider_name == "claude":
        logger.info("Creating Claude provider")
        return ClaudeProvider()
    else:
        raise ValueError(f"Unknown AI provider: '{provider_name}'. Use 'openai' or 'claude'")

