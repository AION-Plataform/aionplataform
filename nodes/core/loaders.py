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
