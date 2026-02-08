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

class NormalizeNode(BaseNode):
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        records = []
        for value in inputs.values():
            if isinstance(value, dict) and "rows" in value:
                records = value["rows"]
                break
            if isinstance(value, list):
                records = value
                break

        schema = self.config.get("schema", {})
        print(f"  [Normalize] Normalizing {len(records)} records to schema: {list(schema.keys())}")
        normalized = []
        for record in records:
            if isinstance(record, dict):
                normalized.append({key: record.get(key) for key in schema.keys()} if schema else record)
            else:
                normalized.append(record)

        return {"normalized": normalized}
