from typing import Dict, Any
from .base import BaseNode

class PdfLoaderNode(BaseNode):
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        path = self.config.get("path")
        if not path:
            print("Warning: No path provided for PDF Loader")
            return {"content": ""}
            
        # In a real impl, we would use pypdf or similar.
        # For MVP/Sim, we return a mock string.
        print(f"  [PdfLoader] Loading file: {path}")
        return {
            "content": f"Content loaded from PDF at {path}. (Simulated)",
            "metadata": {"source": path, "type": "pdf"}
        }

class StaticTextNode(BaseNode):
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        text = self.config.get("text", "")
        return {"content": text}

class SqlLoaderNode(BaseNode):
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        query = self.config.get("query", "")
        if not query:
            return {"rows": [], "warning": "No SQL query provided."}
        print(f"  [SqlLoader] Executing query: {query}")
        # Mocked rows for MVP
        return {"rows": [{"id": 1, "result": "sample"}], "query": query}

class ApiLoaderNode(BaseNode):
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        url = self.config.get("url")
        method = self.config.get("method", "GET").upper()
        payload = self.config.get("payload")
        if not url:
            return {"response": None, "warning": "No URL provided."}
        print(f"  [ApiLoader] Fetching {method} {url}")
        return {"response": {"status": "ok", "url": url, "method": method, "payload": payload}}

class WebLoaderNode(BaseNode):
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        url = self.config.get("url")
        if not url:
            return {"content": "", "warning": "No URL provided."}
        print(f"  [WebLoader] Scraping {url}")
        return {"content": f"Content scraped from {url}. (Simulated)", "metadata": {"source": url}}
