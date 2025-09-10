"""Type definitions for QuietAudit SDK"""

from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import time

class Environment(Enum):
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"

@dataclass
class AuditContext:
    """Context data for AI decision audit trails"""
    
    # Core identification
    request_id: str
    model_provider: str  # "openai", "anthropic", etc.
    model_name: str      # "gpt-4", "claude-3", etc.
    timestamp: int
    
    # AI interaction data
    prompt: str
    response: str
    
    # Metadata
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    application_context: Optional[Dict[str, Any]] = None
    
    # Technical details
    token_usage: Optional[Dict[str, int]] = None
    response_time_ms: Optional[int] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = int(time.time())

@dataclass
class QuietAuditConfig:
    """Configuration for QuietAudit SDK"""
    
    api_key: str
    secret_key: Optional[str] = None
    environment: Environment = Environment.PRODUCTION
    base_url: str = "https://api.quietstack.com"
    timeout: int = 30
    max_retries: int = 3
    
    # Optional client identification
    client_id: Optional[str] = None
    application_name: Optional[str] = None