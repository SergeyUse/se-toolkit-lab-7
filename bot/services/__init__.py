"""Service clients for the bot.

Contains API clients for LMS and LLM services.
"""

import httpx
from typing import Optional, Dict, Any


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
    
    async def health_check(self) -> bool:
        """Check if the LMS API is healthy.
        
        Returns:
            True if the API is healthy, False otherwise.
        """
        try:
            client = await self._get_client()
            response = await client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception:
            return False
    
    async def get_labs(self) -> Dict[str, Any]:
        """Get list of available labs.
        
        Returns:
            Dictionary with labs information.
        """
        client = await self._get_client()
        response = await client.get(f"{self.base_url}/labs")
        response.raise_for_status()
        return response.json()
    
    async def get_scores(self, user_id: str, lab_id: Optional[str] = None) -> Dict[str, Any]:
        """Get scores for a user.
        
        Args:
            user_id: The user's ID.
            lab_id: Optional specific lab ID to get scores for.
            
        Returns:
            Dictionary with scores information.
        """
        client = await self._get_client()
        url = f"{self.base_url}/scores/{user_id}"
        if lab_id:
            url += f"?lab_id={lab_id}"
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


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
