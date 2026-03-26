"""Service clients for the bot.

Contains API clients for LMS and LLM services.
"""

import httpx
from typing import Optional, Dict, Any, List, Tuple


class BackendError(Exception):
    """Exception raised when backend API calls fail."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


class LMSClient:
    """Client for the LMS (Learning Management System) API."""
    
    def __init__(self, base_url: str, api_key: str):
        """Initialize the LMS client.
        
        Args:
            base_url: Base URL of the LMS API.
            api_key: API key for authentication.
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30.0,
            )
        return self._client
    
    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    def _format_error_message(self, error: Exception, operation: str) -> str:
        """Format a user-friendly error message that includes the actual error.
        
        Args:
            error: The original exception.
            operation: The operation that failed.
            
        Returns:
            A user-friendly error message with the actual error details.
        """
        error_str = str(error).lower()
        
        # Connection errors
        if "connection refused" in error_str or "connect" in error_str:
            return f"Backend error: connection refused ({self.base_url}). Check that the services are running."
        if "name resolution" in error_str or "nodename" in error_str:
            return f"Backend error: cannot resolve hostname ({self.base_url}). Check network configuration."
        
        # HTTP errors
        if isinstance(error, httpx.HTTPStatusError):
            status = error.response.status_code
            reason = error.response.reason_phrase
            return f"Backend error: HTTP {status} {reason}. The backend service may be down."
        
        # Timeout errors
        if "timeout" in error_str or "timed out" in error_str:
            return f"Backend error: request timed out. The service may be overloaded."
        
        # Generic error - include the actual error message
        return f"Backend error: {str(error)}. Check that the services are running."
    
    async def health_check(self) -> Tuple[bool, str]:
        """Check if the LMS API is healthy.
        
        Returns:
            Tuple of (is_healthy, status_message).
        """
        try:
            client = await self._get_client()
            response = await client.get(f"{self.base_url}/items/")
            if response.status_code == 200:
                items = response.json()
                count = len(items)
                return True, f"Backend is healthy. {count} items available."
            else:
                return False, f"Backend returned HTTP {response.status_code}."
        except Exception as e:
            error_msg = self._format_error_message(e, "health check")
            return False, error_msg
    
    async def get_labs(self) -> Tuple[bool, List[str], str]:
        """Get list of available labs.
        
        Returns:
            Tuple of (success, labs_list, error_message).
        """
        try:
            client = await self._get_client()
            response = await client.get(f"{self.base_url}/items/")
            response.raise_for_status()
            
            items = response.json()
            labs = [item["title"] for item in items if item.get("type") == "lab"]
            
            if not labs:
                return True, ["No labs found in the system."], ""
            
            return True, labs, ""
            
        except Exception as e:
            error_msg = self._format_error_message(e, "get labs")
            return False, [], error_msg
    
    async def get_pass_rates(self, lab_id: str) -> Tuple[bool, List[Dict[str, Any]], str]:
        """Get pass rates for a specific lab.
        
        Args:
            lab_id: The lab identifier (e.g., "lab-04").
            
        Returns:
            Tuple of (success, pass_rates_list, error_message).
        """
        try:
            client = await self._get_client()
            response = await client.get(
                f"{self.base_url}/analytics/pass-rates",
                params={"lab": lab_id}
            )
            response.raise_for_status()
            
            data = response.json()
            return True, data, ""
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return False, [], f"Lab '{lab_id}' not found. Use /labs to see available labs."
            error_msg = self._format_error_message(e, "get pass rates")
            return False, [], error_msg
        except Exception as e:
            error_msg = self._format_error_message(e, "get pass rates")
            return False, [], error_msg


class LLMClient:
    """Client for the LLM (Language Learning Model) API."""
    
    def __init__(self, base_url: str, api_key: str, model: str):
        """Initialize the LLM client.
        
        Args:
            base_url: Base URL of the LLM API.
            api_key: API key for authentication.
            model: Model name to use for completions.
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=60.0,
            )
        return self._client
    
    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    async def chat_completion(self, messages: list) -> str:
        """Get a chat completion from the LLM.
        
        Args:
            messages: List of message dictionaries with role and content.
            
        Returns:
            The completion text from the LLM.
        """
        client = await self._get_client()
        response = await client.post(
            f"{self.base_url}/chat/completions",
            json={
                "model": self.model,
                "messages": messages,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    
    async def health_check(self) -> bool:
        """Check if the LLM API is healthy.
        
        Returns:
            True if the API is healthy, False otherwise.
        """
        try:
            client = await self._get_client()
            response = await client.get(f"{self.base_url}/models")
            return response.status_code == 200
        except Exception:
            return False
