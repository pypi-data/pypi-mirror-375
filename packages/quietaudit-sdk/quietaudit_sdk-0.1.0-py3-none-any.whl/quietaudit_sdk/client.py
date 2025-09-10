"""Main QuietAudit client for blockchain audit trail logging"""

import json
import time
import uuid
from typing import Dict, Any, Optional
import httpx

from .types import AuditContext, QuietAuditConfig, Environment
from .config import load_config
from .exceptions import APIError, AuthenticationError, RateLimitError


class QuietAuditClient:
    """
    Main client for QuietAudit SDK
    
    Handles authentication with QuietStack SaaS and logging of AI decision contexts
    to blockchain through the backend API.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        environment: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize QuietAudit client
        
        Args:
            api_key: QuietStack API key (or set QUIETAUDIT_API_KEY env var)
            secret_key: QuietStack secret key (optional)
            environment: "production", "staging", or "development"
            **kwargs: Additional configuration options
        """
        self.config = load_config(
            api_key=api_key,
            secret_key=secret_key, 
            environment=environment,
            **kwargs
        )
        
        self._client = httpx.Client(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "User-Agent": f"QuietAudit-SDK/0.1.0"
            }
        )
        
        # Track for debugging
        self._request_count = 0
    
    async def log_context(self, context: AuditContext) -> Dict[str, Any]:
        """
        Log an AI decision context to blockchain via QuietStack API
        
        Args:
            context: The audit context to log
            
        Returns:
            Dict containing transaction hash and audit ID
            
        Raises:
            APIError: If logging fails
            AuthenticationError: If API key is invalid
            RateLimitError: If rate limit exceeded
        """
        
        # Prepare payload for QuietStack backend
        payload = {
            "context": {
                "request_id": context.request_id,
                "model_provider": context.model_provider,
                "model_name": context.model_name,
                "timestamp": context.timestamp,
                "prompt": context.prompt,
                "response": context.response,
                "user_id": context.user_id,
                "session_id": context.session_id,
                "application_context": context.application_context,
                "token_usage": context.token_usage,
                "response_time_ms": context.response_time_ms,
            },
            "client_info": {
                "client_id": self.config.client_id,
                "application_name": self.config.application_name,
                "environment": self.config.environment.value,
            }
        }
        
        try:
            self._request_count += 1
            response = self._client.post("/v1/audit/log", json=payload)
            
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code >= 400:
                error_data = response.json() if response.content else {}
                raise APIError(
                    f"API request failed: {response.status_code}", 
                    status_code=response.status_code,
                    response=error_data
                )
            
            return response.json()
            
        except httpx.RequestError as e:
            raise APIError(f"Network error: {str(e)}")
    
    def verify_context(self, audit_id: str) -> Dict[str, Any]:
        """
        Verify an audit trail by ID
        
        Args:
            audit_id: The audit ID to verify
            
        Returns:
            Dict containing verification status and blockchain proof
        """
        try:
            response = self._client.get(f"/v1/audit/verify/{audit_id}")
            
            if response.status_code == 404:
                return {"verified": False, "reason": "Audit not found"}
            elif response.status_code >= 400:
                error_data = response.json() if response.content else {}
                raise APIError(
                    f"Verification failed: {response.status_code}",
                    status_code=response.status_code,
                    response=error_data
                )
            
            return response.json()
            
        except httpx.RequestError as e:
            raise APIError(f"Network error during verification: {str(e)}")
    
    def get_audit_history(
        self, 
        user_id: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get audit history for debugging/monitoring
        
        Args:
            user_id: Filter by user ID
            start_time: Unix timestamp start filter
            end_time: Unix timestamp end filter  
            limit: Max number of results
            
        Returns:
            Dict containing audit history
        """
        params = {"limit": limit}
        if user_id:
            params["user_id"] = user_id
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
            
        try:
            response = self._client.get("/v1/audit/history", params=params)
            
            if response.status_code >= 400:
                error_data = response.json() if response.content else {}
                raise APIError(
                    f"History request failed: {response.status_code}",
                    status_code=response.status_code,
                    response=error_data
                )
            
            return response.json()
            
        except httpx.RequestError as e:
            raise APIError(f"Network error: {str(e)}")
    
    def close(self):
        """Close the HTTP client"""
        self._client.close()
    
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()