"""Anthropic model wrapper with QuietAudit logging"""

import time
from typing import Any, Dict

from .base import BaseModelWrapper 
from ..types import AuditContext
from ..exceptions import ContextExtractionError


class AnthropicWrapper(BaseModelWrapper):
    """Wrapper for Anthropic client with automatic audit logging"""
    
    def _get_provider_name(self) -> str:
        return "anthropic"
    
    def _extract_context(self, method_name: str, args: tuple, kwargs: dict, response: Any) -> AuditContext:
        """Extract context from Anthropic API call"""
        
        try:
            # Handle messages API (Claude 3)
            if "message" in method_name.lower():
                return self._extract_messages_context(kwargs, response)
            
            # Handle legacy completions
            elif "completion" in method_name.lower():
                return self._extract_completion_context(kwargs, response)
            
            # Generic fallback
            else:
                return self._extract_generic_context(method_name, kwargs, response)
                
        except Exception as e:
            raise ContextExtractionError(f"Failed to extract Anthropic context: {str(e)}")
    
    def _extract_messages_context(self, kwargs: dict, response: Any) -> AuditContext:
        """Extract context from Anthropic messages call (Claude 3)"""
        
        model_name = kwargs.get("model", "unknown")
        
        # Extract messages
        messages = kwargs.get("messages", [])
        prompt = self._messages_to_string(messages)
        
        # Add system prompt if present
        system_prompt = kwargs.get("system", "")
        if system_prompt:
            prompt = f"System: {system_prompt}\n\n{prompt}"
        
        # Extract response
        if hasattr(response, 'content') and response.content:
            if isinstance(response.content, list) and response.content:
                response_text = response.content[0].text
            else:
                response_text = str(response.content)
        else:
            response_text = str(response)
        
        # Extract token usage if available
        token_usage = None
        if hasattr(response, 'usage') and response.usage:
            token_usage = {
                "input_tokens": getattr(response.usage, 'input_tokens', None),
                "output_tokens": getattr(response.usage, 'output_tokens', None),
            }
        
        return AuditContext(
            request_id="",
            model_provider=self._provider_name,
            model_name=model_name,
            timestamp=int(time.time()),
            prompt=prompt,
            response=response_text,
            token_usage=token_usage,
            application_context={
                "method": "messages.create",
                "max_tokens": kwargs.get("max_tokens"),
                "temperature": kwargs.get("temperature"),
                "top_p": kwargs.get("top_p"),
                "top_k": kwargs.get("top_k"),
                "system_prompt": bool(system_prompt),
            }
        )
    
    def _extract_completion_context(self, kwargs: dict, response: Any) -> AuditContext:
        """Extract context from legacy Anthropic completion"""
        
        model_name = kwargs.get("model", "unknown")
        prompt = kwargs.get("prompt", "")
        
        # Extract response
        if hasattr(response, 'completion'):
            response_text = response.completion
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
        """Generic context extraction for other Anthropic methods"""
        
        return AuditContext(
            request_id="",
            model_provider=self._provider_name,
            model_name=kwargs.get("model", "unknown"),
            timestamp=int(time.time()),
            prompt=f"Anthropic {method_name} call",
            response=str(response)[:1000],
            application_context={
                "method": method_name,
                "kwargs": {k: str(v)[:100] for k, v in kwargs.items()}
            }
        )
    
    def _messages_to_string(self, messages: list) -> str:
        """Convert Anthropic messages format to readable string"""
        
        if not messages:
            return ""
        
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            
            # Handle different content formats
            if isinstance(content, list):
                content = " ".join(str(item.get("text", item)) for item in content if isinstance(item, dict))
            
            prompt_parts.append(f"{role}: {content}")
        
        return "\n".join(prompt_parts)
    
    def _should_audit_method(self, method_name: str) -> bool:
        """Anthropic specific method filtering"""
        
        audit_methods = [
            "create",  # messages.create, completions.create
        ]
        
        return any(method in method_name for method in audit_methods)