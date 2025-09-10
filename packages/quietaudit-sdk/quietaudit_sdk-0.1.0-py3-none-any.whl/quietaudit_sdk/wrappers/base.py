"""Base wrapper class for AI model clients"""

import uuid
import time
from typing import Any, Dict, Optional
from abc import ABC, abstractmethod

from ..client import QuietAuditClient
from ..types import AuditContext
from ..exceptions import ContextExtractionError


class BaseModelWrapper(ABC):
    """Base class for wrapping AI model clients with audit logging"""
    
    def __init__(self, original_client: Any, api_key: str, **kwargs):
        """
        Initialize the base wrapper
        
        Args:
            original_client: The original AI client (OpenAI, Anthropic, etc.)
            api_key: QuietAudit API key
            **kwargs: Additional configuration for QuietAuditClient
        """
        self._original_client = original_client
        self._audit_client = QuietAuditClient(api_key=api_key, **kwargs)
        self._provider_name = self._get_provider_name()
    
    @abstractmethod
    def _get_provider_name(self) -> str:
        """Return the provider name (e.g., 'openai', 'anthropic')"""
        pass
    
    @abstractmethod
    def _extract_context(self, method_name: str, args: tuple, kwargs: dict, response: Any) -> AuditContext:
        """Extract audit context from method call and response"""
        pass
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        return str(uuid.uuid4())
    
    async def _log_context_async(self, context: AuditContext) -> Optional[Dict[str, Any]]:
        """Asynchronously log context (non-blocking)"""
        try:
            return await self._audit_client.log_context(context)
        except Exception as e:
            # Log error but don't fail the original request
            print(f"QuietAudit logging failed: {e}")
            return None
    
    def _log_context_sync(self, context: AuditContext) -> Optional[Dict[str, Any]]:
        """Synchronously log context"""
        try:
            # For now, we'll use sync version - can enhance with async later
            import asyncio
            return asyncio.run(self._audit_client.log_context(context))
        except Exception as e:
            # Log error but don't fail the original request
            print(f"QuietAudit logging failed: {e}")
            return None
    
    def __getattr__(self, name: str) -> Any:
        """
        Delegate attribute access to original client
        This allows the wrapper to be a drop-in replacement
        """
        attr = getattr(self._original_client, name)
        
        # If it's a method that we want to audit, wrap it
        if callable(attr) and self._should_audit_method(name):
            return self._create_audited_method(name, attr)
        
        return attr
    
    def _should_audit_method(self, method_name: str) -> bool:
        """
        Determine if a method should be audited
        Override in subclasses for specific providers
        """
        # By default, audit methods that look like AI calls
        audit_patterns = [
            'create',
            'complete', 
            'chat',
            'generate',
            'predict'
        ]
        return any(pattern in method_name.lower() for pattern in audit_patterns)
    
    def _create_audited_method(self, method_name: str, original_method):
        """Create a wrapped version of a method that includes audit logging"""
        
        def audited_method(*args, **kwargs):
            start_time = time.time()
            request_id = self._generate_request_id()
            
            try:
                # Call original method
                response = original_method(*args, **kwargs)
                
                # Extract context and log
                response_time_ms = int((time.time() - start_time) * 1000)
                
                try:
                    context = self._extract_context(method_name, args, kwargs, response)
                    context.request_id = request_id
                    context.response_time_ms = response_time_ms
                    
                    # Log in background (don't block the response)
                    self._log_context_sync(context)
                    
                except ContextExtractionError as e:
                    print(f"Failed to extract context for audit: {e}")
                
                return response
                
            except Exception as e:
                # Log the error attempt if possible
                try:
                    error_context = AuditContext(
                        request_id=request_id,
                        model_provider=self._provider_name,
                        model_name="unknown",
                        timestamp=int(time.time()),
                        prompt=f"Error in {method_name}",
                        response=f"ERROR: {str(e)}",
                        response_time_ms=int((time.time() - start_time) * 1000)
                    )
                    self._log_context_sync(error_context)
                except:
                    pass  # Don't let logging errors interfere
                
                # Re-raise original exception
                raise e
        
        return audited_method