"""OpenAI model wrapper with QuietAudit logging"""

import json
import time
from typing import Any, Dict, List

from .base import BaseModelWrapper
from ..types import AuditContext
from ..exceptions import ContextExtractionError


class OpenAIWrapper(BaseModelWrapper):
    """Wrapper for OpenAI client with automatic audit logging"""
    
    def _get_provider_name(self) -> str:
        return "openai"
    
    def _extract_context(self, method_name: str, args: tuple, kwargs: dict, response: Any) -> AuditContext:
        """Extract context from OpenAI API call"""
        
        try:
            # Handle chat completions (most common case)
            if "chat" in method_name.lower() and "completion" in method_name.lower():
                return self._extract_chat_completion_context(kwargs, response)
            
            # Handle legacy completions
            elif "completion" in method_name.lower():
                return self._extract_completion_context(kwargs, response)
            
            # Generic fallback
            else:
                return self._extract_generic_context(method_name, kwargs, response)
                
        except Exception as e:
            raise ContextExtractionError(f"Failed to extract OpenAI context: {str(e)}")
    
    def _extract_chat_completion_context(self, kwargs: dict, response: Any) -> AuditContext:
        """Extract context from chat completion call"""
        
        # Extract model
        model_name = kwargs.get("model", "unknown")
        
        # Extract messages and convert to prompt string
        messages = kwargs.get("messages", [])
        prompt = self._messages_to_string(messages)
        
        # Extract response
        if hasattr(response, 'choices') and response.choices:
            response_text = response.choices[0].message.content
        else:
            response_text = str(response)
        
        # Extract token usage if available
        token_usage = None
        if hasattr(response, 'usage') and response.usage:
            token_usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        
        return AuditContext(
            request_id="",  # Will be set by base wrapper
            model_provider=self._provider_name,
            model_name=model_name,
            timestamp=int(time.time()),
            prompt=prompt,
            response=response_text,
            token_usage=token_usage,
            application_context={
                "method": "chat.completions.create",
                "temperature": kwargs.get("temperature"),
                "max_tokens": kwargs.get("max_tokens"),
                "top_p": kwargs.get("top_p"),
                "frequency_penalty": kwargs.get("frequency_penalty"),
                "presence_penalty": kwargs.get("presence_penalty"),
            }
        )
    
    def _extract_completion_context(self, kwargs: dict, response: Any) -> AuditContext:
        """Extract context from legacy completion call"""
        
        model_name = kwargs.get("model", "unknown")
        prompt = kwargs.get("prompt", "")
        
        # Convert prompt to string if it's a list
        if isinstance(prompt, list):
            prompt = " ".join(str(p) for p in prompt)
        
        # Extract response
        if hasattr(response, 'choices') and response.choices:
            response_text = response.choices[0].text
        else:
            response_text = str(response)
        
        return AuditContext(
            request_id="",
            model_provider=self._provider_name,
            model_name=model_name,
            timestamp=int(time.time()),
            prompt=str(prompt),
            response=response_text,
            application_context={
                "method": "completions.create",
                **{k: v for k, v in kwargs.items() if k != "prompt"}
            }
        )
    
    def _extract_generic_context(self, method_name: str, kwargs: dict, response: Any) -> AuditContext:
        """Generic context extraction for other OpenAI methods"""
        
        return AuditContext(
            request_id="",
            model_provider=self._provider_name,
            model_name=kwargs.get("model", "unknown"),
            timestamp=int(time.time()),
            prompt=f"OpenAI {method_name} call",
            response=str(response)[:1000],  # Truncate long responses
            application_context={
                "method": method_name,
                "kwargs": {k: str(v)[:100] for k, v in kwargs.items()}  # Truncate values
            }
        )
    
    def _messages_to_string(self, messages: List[Dict[str, Any]]) -> str:
        """Convert OpenAI messages format to a readable string"""
        
        if not messages:
            return ""
        
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            prompt_parts.append(f"{role}: {content}")
        
        return "\n".join(prompt_parts)
    
    def _should_audit_method(self, method_name: str) -> bool:
        """OpenAI specific method filtering"""
        
        # Audit these OpenAI methods
        audit_methods = [
            "create",  # completions.create, chat.completions.create
        ]
        
        return any(method in method_name for method in audit_methods)