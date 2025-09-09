"""HTTP client wrapper for BasicOps API interactions."""

import asyncio
import json
import uuid
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

import httpx
from loguru import logger

from .config import get_config
from .exceptions import (
    BasicOpsNetworkError,
    create_error_from_response,
)


class BasicOpsClient:
    """Async HTTP client wrapper for BasicOps API with retry logic and logging."""
    
    def __init__(self, config: Optional[Any] = None):
        """Initialize the BasicOps client."""
        self.config = config or get_config()
        self.client: Optional[httpx.AsyncClient] = None
        
    async def __aenter__(self) -> "BasicOpsClient":
        """Async context manager entry."""
        await self._ensure_client()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()
            self.client = None
    
    async def _ensure_client(self) -> None:
        """Ensure HTTP client is initialized."""
        if self.client is None:
            self.client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.config.basicops_timeout),
                headers={
                    "User-Agent": "mcp-basicops-server/0.1.0",
                    "Content-Type": "application/json",
                    **self.config.auth_header
                }
            )
    
    def _generate_correlation_id(self) -> str:
        """Generate a correlation ID for request tracking."""
        return str(uuid.uuid4())[:8]
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        return urljoin(self.config.basicops_api_url + "/", endpoint.lstrip("/"))
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        correlation_id: Optional[str] = None,
    ) -> httpx.Response:
        """Make HTTP request with retry logic."""
        await self._ensure_client()
        
        correlation_id = correlation_id or self._generate_correlation_id()
        url = self._build_url(endpoint)
        
        # Prepare request headers
        request_headers = {}
        if not files:  # Don't set content-type for multipart requests
            request_headers["Content-Type"] = "application/json"
        if headers:
            request_headers.update(headers)
        
        # Log request
        logger.debug(
            "Making request",
            correlation_id=correlation_id,
            method=method,
            url=url,
            params=params,
            data=data if not files else "<multipart-data>",
        )
        
        last_exception = None
        for attempt in range(self.config.basicops_max_retries + 1):
            try:
                # Prepare request data
                request_kwargs = {
                    "method": method,
                    "url": url,
                    "params": params,
                    "headers": request_headers,
                }
                
                if files:
                    request_kwargs["files"] = files
                    if data:
                        request_kwargs["data"] = data
                elif data is not None:
                    request_kwargs["json"] = data
                
                response = await self.client.request(**request_kwargs)
                
                # Log response
                logger.debug(
                    "Received response",
                    correlation_id=correlation_id,
                    status_code=response.status_code,
                    response_size=len(response.content),
                )
                
                if response.is_success:
                    return response
                
                # Handle error response
                try:
                    error_data = response.json()
                except (json.JSONDecodeError, ValueError):
                    error_data = {"error": response.text}
                
                logger.warning(
                    "Request failed",
                    correlation_id=correlation_id,
                    status_code=response.status_code,
                    error_data=error_data,
                    attempt=attempt + 1,
                )
                
                # Don't retry client errors (4xx), only server errors and network issues
                if 400 <= response.status_code < 500:
                    raise create_error_from_response(
                        response.status_code, endpoint, error_data
                    )
                
                # Server error - might retry
                last_exception = create_error_from_response(
                    response.status_code, endpoint, error_data
                )
                
            except httpx.RequestError as e:
                logger.warning(
                    "Network error occurred",
                    correlation_id=correlation_id,
                    error=str(e),
                    attempt=attempt + 1,
                )
                last_exception = BasicOpsNetworkError(
                    f"Network error: {str(e)}",
                    endpoint=endpoint,
                    details={"original_error": str(e)}
                )
            
            # Wait before retry (except on last attempt)
            if attempt < self.config.basicops_max_retries:
                delay = self.config.basicops_retry_delay * (2 ** attempt)  # Exponential backoff
                logger.debug(
                    "Retrying request",
                    correlation_id=correlation_id,
                    delay=delay,
                    attempt=attempt + 1,
                )
                await asyncio.sleep(delay)
        
        # All retries exhausted
        logger.error(
            "Request failed after all retries",
            correlation_id=correlation_id,
            attempts=self.config.basicops_max_retries + 1,
        )
        raise last_exception
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make GET request."""
        response = await self._make_request("GET", endpoint, params=params, headers=headers)
        return response.json()
    
    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make POST request."""
        response = await self._make_request("POST", endpoint, params=params, data=data, headers=headers)
        return response.json()
    
    async def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make PUT request."""
        response = await self._make_request("PUT", endpoint, params=params, data=data, headers=headers)
        return response.json()
    
    async def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make DELETE request."""
        response = await self._make_request("DELETE", endpoint, params=params, headers=headers)
        return response.json()
    
    async def post_multipart(
        self,
        endpoint: str,
        files: Dict[str, Any],
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make multipart POST request for file uploads."""
        response = await self._make_request(
            "POST", endpoint, data=data, files=files, headers=headers
        )
        return response.json()
    
    async def download(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> bytes:
        """Download binary content."""
        response = await self._make_request("GET", endpoint, params=params, headers=headers)
        return response.content
