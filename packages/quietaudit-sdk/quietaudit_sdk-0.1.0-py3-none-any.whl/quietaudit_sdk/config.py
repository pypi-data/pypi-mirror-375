"""Configuration management for QuietAudit SDK"""

import os
from typing import Optional
from .types import QuietAuditConfig, Environment
from .exceptions import ConfigurationError

def load_config(
    api_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    environment: Optional[str] = None,
    **kwargs
) -> QuietAuditConfig:
    """
    Load QuietAudit configuration from parameters or environment variables
    
    Priority order:
    1. Direct parameters
    2. Environment variables
    3. Default values
    """
    
    # Get API key
    final_api_key = (
        api_key or 
        os.getenv("QUIETAUDIT_API_KEY") or
        os.getenv("QA_API_KEY")
    )
    
    if not final_api_key:
        raise ConfigurationError(
            "API key is required. Set QUIETAUDIT_API_KEY environment variable "
            "or pass api_key parameter"
        )
    
    # Get secret key (optional)
    final_secret_key = (
        secret_key or
        os.getenv("QUIETAUDIT_SECRET_KEY") or
        os.getenv("QA_SECRET_KEY")
    )
    
    # Get environment
    env_str = (
        environment or
        os.getenv("QUIETAUDIT_ENVIRONMENT", "production")
    ).lower()
    
    try:
        final_environment = Environment(env_str)
    except ValueError:
        raise ConfigurationError(
            f"Invalid environment '{env_str}'. Must be one of: "
            f"{[e.value for e in Environment]}"
        )
    
    # Build config
    config_data = {
        "api_key": final_api_key,
        "secret_key": final_secret_key,
        "environment": final_environment,
        **kwargs
    }
    
    # Override base_url for different environments
    if final_environment == Environment.DEVELOPMENT:
        config_data.setdefault("base_url", "http://localhost:8000")
    elif final_environment == Environment.STAGING:
        config_data.setdefault("base_url", "https://staging-api.quietstack.com")
    
    return QuietAuditConfig(**config_data)