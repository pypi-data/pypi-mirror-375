"""Model wrappers for QuietAudit SDK"""

from .base import BaseModelWrapper
from .openai import OpenAIWrapper
from .anthropic import AnthropicWrapper

def wrap_model(model_client, api_key: str, **kwargs):
    """
    Wrap any supported AI model client with QuietAudit logging
    
    Args:
        model_client: The AI model client (OpenAI, Anthropic, etc.)
        api_key: QuietAudit API key
        **kwargs: Additional configuration
        
    Returns:
        Wrapped model client with automatic audit logging
        
    Raises:
        ModelNotSupportedError: If model type is not supported
    """
    from ..exceptions import ModelNotSupportedError
    
    # Detect model type and return appropriate wrapper
    client_type = type(model_client).__name__
    module_name = type(model_client).__module__
    
    if "openai" in module_name.lower():
        return OpenAIWrapper(model_client, api_key, **kwargs)
    elif "anthropic" in module_name.lower():
        return AnthropicWrapper(model_client, api_key, **kwargs)
    else:
        raise ModelNotSupportedError(
            f"Model client type '{client_type}' from module '{module_name}' is not supported. "
            f"Supported providers: OpenAI, Anthropic"
        )

__all__ = ["wrap_model", "BaseModelWrapper", "OpenAIWrapper", "AnthropicWrapper"]