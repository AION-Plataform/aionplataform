from typing import Dict, Any, Optional
import aiohttp
import json

class HTTPNode:
    """Node for making HTTP requests to external APIs"""
    
    def __init__(self, config: Dict[str, Any]):
        self.url = config.get("url", "")
        self.method = config.get("method", "GET").upper()
        self.headers = config.get("headers", {})
        self.body = config.get("body", None)
        self.timeout = config.get("timeout", 30)
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make HTTP request
        
        Inputs:
            - url_params: Optional dict to substitute in URL
            - body_params: Optional dict to merge with body
        
        Returns:
            - status: HTTP status code
            - data: Response body (parsed JSON if possible)
            - headers: Response headers
        """
        # Build final URL (replace placeholders if needed)
        final_url = self.url
        if "url_params" in inputs:
            for key, value in inputs["url_params"].items():
                final_url = final_url.replace(f"{{{key}}}", str(value))
        
        # Build final body
        final_body = self.body
        if self.body and "body_params" in inputs:
            if isinstance(self.body, dict):
                final_body = {**self.body, **inputs["body_params"]}
        
        # Make request
        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(
                    method=self.method,
                    url=final_url,
                    headers=self.headers,
                    json=final_body if self.method in ["POST", "PUT", "PATCH"] else None,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    
                    # Try to parse as JSON
                    try:
                        data = await response.json()
                    except:
                        data = await response.text()
                    
                    return {
                        "status": response.status,
                        "data": data,
                        "headers": dict(response.headers),
                        "success": 200 <= response.status < 300
                    }
            
            except aiohttp.ClientError as e:
                return {
                    "status": 0,
                    "data": None,
                    "error": str(e),
                    "success": False
                }
