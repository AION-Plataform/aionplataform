from typing import Dict, Any
from .base import BaseNode

class CleanTextNode(BaseNode):
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Expecting input named 'content' or just taking the first available input
        content = ""
        for key, val in inputs.items():
            if isinstance(val, dict) and "content" in val:
                content = val["content"]
                break
            elif isinstance(val, str):
                content = val
                break
        
        remove_stopwords = self.config.get("remove_stopwords", False)
        
        print(f"  [CleanText] Cleaning content (size: {len(content)})")
        cleaned = content.strip().upper() # Simple mock transformation
        
        if remove_stopwords:
            cleaned += " [STOPWORDS REMOVED]"
            
        return {"content": cleaned}
