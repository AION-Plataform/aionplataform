from typing import Dict, Any
from .base import BaseNode

class LLMGenerateNode(BaseNode):
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        prompt_template = self.config.get("prompt", "")
        model = self.config.get("model", "gpt-4o")
        
        # Build context from inputs
        context_str = ""
        for key, val in inputs.items():
            context_str += f"{key}: {val}\n"
            
        print(f"  [LLMGenerate] Generating with {model}. Prompt len: {len(prompt_template)}")
        
        # Mock LLM generation
        return {
            "output": f"Generated response from {model} based on inputs: {list(inputs.keys())}",
            "token_usage": {"prompt": 50, "completion": 20}
        }

class AgentRouterNode(BaseNode):
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        intent = self.config.get("default_route", "general")
        
        # Mock routing logic
        user_input = inputs.get("query", {}).get("content", "")
        if "refund" in user_input.lower():
            intent = "refund_flow"
        elif "tech support" in user_input.lower():
            intent = "support_flow"
            
        print(f"  [AgentRouter] Routing to: {intent}")
        return {
            "route": intent,
            "confidence": 0.95
        }
