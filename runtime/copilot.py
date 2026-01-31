from typing import Dict, Any, List
import datetime

class AIONCopilot:
    def __init__(self):
        pass

    async def generate_flow_from_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Generates a valid AION DSL from a natural language prompt.
        For MVP, we use keyword matching to select templates.
        """
        prompt_lower = prompt.lower()
        
        # Template: RAG Flow
        if "rag" in prompt_lower or "pdf" in prompt_lower:
            return self._create_rag_template(prompt)
        
        # Template: Simple Agent
        if "agent" in prompt_lower or "chatbot" in prompt_lower:
            return self._create_agent_template(prompt)
            
        # Default: Hello World
        return self._create_default_template(prompt)

    async def validate_flow(self, dsl: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes a flow and returns suggestions.
        """
        issues = []
        suggestions = []
        
        nodes = dsl.get("nodes", [])
        node_types = [n.get("type") for n in nodes]
        
        # Rule 1: Check for RAG completeness
        if "rag.chunk" in node_types and "rag.vector_store" not in node_types:
            issues.append("Flow has chunking but no vector store.")
            suggestions.append("Add a Vector Store node to save embeddings.")
            
        # Rule 2: Check for Output
        has_output = False
        # Simplified check
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions
        }

    def _create_rag_template(self, prompt: str) -> Dict[str, Any]:
        timestamp = datetime.datetime.utcnow().isoformat()
        return {
          "metadata": {
            "name": f"Copilot RAG Flow {timestamp}",
            "version": "1.0.0",
            "created_at": timestamp,
            "owner": "copilot"
          },
          "nodes": [
            { "id": "n1", "type": "loader.pdf", "version": "1.0", "config": { "path": "docs/" }, "position": { "x": 100, "y": 100 } },
            { "id": "n2", "type": "rag.chunk", "version": "1.0", "config": { "size": 500 }, "position": { "x": 300, "y": 100 } },
            { "id": "n3", "type": "rag.embed", "version": "1.0", "config": {}, "position": { "x": 500, "y": 100 } },
            { "id": "n4", "type": "rag.vector_store", "version": "1.0", "config": {}, "position": { "x": 700, "y": 100 } }
          ],
          "edges": [
            { "id": "e1", "from": { "node": "n1", "port": "output" }, "to": { "node": "n2", "port": "input" } },
            { "id": "e2", "from": { "node": "n2", "port": "output" }, "to": { "node": "n3", "port": "input" } },
            { "id": "e3", "from": { "node": "n3", "port": "output" }, "to": { "node": "n4", "port": "input" } }
          ]
        }

    def _create_agent_template(self, prompt: str) -> Dict[str, Any]:
        timestamp = datetime.datetime.utcnow().isoformat()
        return {
          "metadata": {
            "name": f"Copilot Agent Flow {timestamp}",
            "version": "1.0.0",
            "created_at": timestamp,
            "owner": "copilot"
          },
          "nodes": [
            { "id": "n1", "type": "loader.static", "version": "1.0", "config": { "text": "System Prompt..." }, "position": { "x": 100, "y": 100 } },
            { "id": "n2", "type": "llm.generate", "version": "1.0", "config": { "model": "gpt-4" }, "position": { "x": 400, "y": 100 } }
          ],
          "edges": [
            { "id": "e1", "from": { "node": "n1", "port": "output" }, "to": { "node": "n2", "port": "context" } }
          ]
        }

    def _create_default_template(self, prompt: str) -> Dict[str, Any]:
        # Empty or simple flow
        timestamp = datetime.datetime.utcnow().isoformat()
        return {
          "metadata": {
            "name": "Empty Flow",
            "version": "1.0.0",
            "created_at": timestamp,
            "owner": "copilot"
          },
          "nodes": [],
          "edges": []
        }
