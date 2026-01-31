import networkx as nx
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# Re-using definitions that would ideally come from shared schemas
class Node(BaseModel):
    id: str
    type: str
    version: str
    config: Dict[str, Any] = {}

class Edge(BaseModel):
    id: str
    source: Dict[str, str] = Field(alias="from")
    target: Dict[str, str] = Field(alias="to")

class FlowDSL(BaseModel):
    metadata: Dict[str, Any]
    nodes: List[Node]
    edges: List[Edge]
    secrets_ref: Optional[List[str]] = []
    policies: Optional[Dict[str, Any]] = {}

class ValidationResult(BaseModel):
    valid: bool
    errors: List[str] = []
    warnings: List[str] = []

class GraphValidator:
    def __init__(self, dsl_data: Dict[str, Any]):
        self.dsl = FlowDSL(**dsl_data)
        self.graph = nx.DiGraph()
        self._build_graph()

    def _build_graph(self):
        for node in self.dsl.nodes:
            self.graph.add_node(node.id, **node.dict())
        
        for edge in self.dsl.edges:
            self.graph.add_edge(edge.source['node'], edge.target['node'], id=edge.id)

    def validate(self) -> ValidationResult:
        errors = []
        warnings = []

        # 1. Check for Cycles
        if not nx.is_directed_acyclic_graph(self.graph):
            try:
                cycle = nx.find_cycle(self.graph)
                errors.append(f"Cycle detected in flow: {cycle}")
            except nx.NetworkXNoCycle:
                pass # Should not happen given is_directed_acyclic_graph is False

        # 2. Check for Disconnected Components (Islands)
        # It's okay to have islands? Maybe just a warning.
        if not nx.is_weakly_connected(self.graph) and len(self.dsl.nodes) > 1:
            warnings.append("Graph has multiple disconnected components. Ensure all nodes are reachable if needed.")

        # 3. Check for Pending Inputs (Nodes without parents that aren't Sources?)
        # This requires knowledge of Node Types (Inputs vs Transforms).
        # For now, we do structural validation only.
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
