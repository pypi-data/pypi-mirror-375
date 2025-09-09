import httpx
import os
from typing import Any, Dict, Optional

class DefectDojoClient:
    """Client for interacting with the DefectDojo API."""
    
    def __init__(self, base_url: str, api_token: str):
        """Initialize the DefectDojo API client.
        
        Args:
            base_url: Base URL for the DefectDojo API
            api_token: API token for authentication
        """
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Token {api_token}",
            "Content-Type": "application/json"
        }
        # Consider adding timeout configuration
        self.client = httpx.AsyncClient(headers=self.headers, timeout=30.0) 

    async def _request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Helper method to make API requests."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = await self.client.request(method, url, params=params, json=json)
            response.raise_for_status()
            # Handle cases where response might be empty (e.g., 204 No Content)
            if response.status_code == 204:
                return {} 
            return response.json()
        except httpx.HTTPStatusError as e:
            # Log or handle specific status codes if needed
            return {"error": f"HTTP error: {e.response.status_code}", "details": e.response.text}
        except httpx.RequestError as e:
            # Handle network errors, timeouts, etc.
            return {"error": f"Request error: {str(e)}"}
        except Exception as e:
            # Catch unexpected errors
            return {"error": f"An unexpected error occurred: {str(e)}"}

    async def get_findings(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get findings with optional filters."""
        return await self._request("GET", "/api/v2/findings/", params=filters)
    
    async def search_findings(self, query: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Search for findings using a text query."""
        params = filters or {}
        params["search"] = query
        return await self._request("GET", "/api/v2/findings/", params=params)
    
    async def update_finding(self, finding_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a finding by ID."""
        return await self._request("PATCH", f"/api/v2/findings/{finding_id}/", json=data)
    
    async def add_note_to_finding(self, finding_id: int, note: str) -> Dict[str, Any]:
        """Add a note to a finding."""
        data = {"entry": note, "finding": finding_id}
        return await self._request("POST", "/api/v2/notes/", json=data)
    
    async def create_finding(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new finding."""
        return await self._request("POST", "/api/v2/findings/", json=data)
    
    async def get_products(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get products with optional filters."""
        return await self._request("GET", "/api/v2/products/", params=filters)
            
    async def get_engagements(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get engagements with optional filters."""
        return await self._request("GET", "/api/v2/engagements/", params=filters)
    
    async def get_engagement(self, engagement_id: int) -> Dict[str, Any]:
        """Get a specific engagement by ID."""
        return await self._request("GET", f"/api/v2/engagements/{engagement_id}/")
    
    async def create_engagement(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new engagement."""
        return await self._request("POST", "/api/v2/engagements/", json=data)
    
    async def update_engagement(self, engagement_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing engagement."""
        return await self._request("PATCH", f"/api/v2/engagements/{engagement_id}/", json=data)

# --- Client Factory ---

def get_client(validate_token=True, base_url=None, token=None) -> DefectDojoClient:
    """Get a configured DefectDojo client.
    
    Args:
        validate_token: Whether to validate that the token is set (default: True)
        base_url: Optional base URL override for testing
        token: Optional token override for testing
        
    Returns:
        A configured DefectDojoClient instance
        
    Raises:
        ValueError: If DEFECTDOJO_API_TOKEN environment variable is not set and validate_token is True
    """
    # Use provided values or get from environment variables.
    # Ensure DEFECTDOJO_API_BASE and DEFECTDOJO_API_TOKEN are set in your environment.
    actual_token = token if token is not None else os.environ.get("DEFECTDOJO_API_TOKEN")
    actual_base_url = base_url if base_url is not None else os.environ.get("DEFECTDOJO_API_BASE")

    if not actual_base_url:
         raise ValueError("DEFECTDOJO_API_BASE environment variable or base_url argument must be provided and cannot be empty.")
    
    # Only validate token if requested (e.g., skipped for tests)
    if validate_token and not actual_token:
        raise ValueError("DEFECTDOJO_API_TOKEN environment variable or token argument must be provided")
    
    return DefectDojoClient(actual_base_url, actual_token)
