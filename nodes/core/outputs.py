from typing import Dict, Any
from .base import BaseNode


class ApiEndpointNode(BaseNode):
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        result = inputs.get("result")
        if result is None and inputs:
            result = next(iter(inputs.values()))
        path = self.config.get("path", "/output")
        print(f"  [ApiEndpoint] Emitting response on {path}")
        return {"response": result, "path": path}
