import networkx as nx
from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Any, Optional

# Re-using definitions that would ideally come from shared schemas
class Node(BaseModel):
    id: str
    type: str
    version: str = "1.0.0"
    inputs: Optional[Dict[str, Any]] = None
    outputs: Optional[Dict[str, Any]] = None
    config: Dict[str, Any] = {}
    policies: Optional[Dict[str, Any]] = None

class Edge(BaseModel):
    id: str
    source: Optional[str] = None
    source_output: Optional[str] = None
    target: Optional[str] = None
    target_input: Optional[str] = None
    legacy_source: Optional[Dict[str, str]] = Field(default=None, alias="from")
    legacy_target: Optional[Dict[str, str]] = Field(default=None, alias="to")

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_fields(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(values, dict):
            return values

        legacy_source = values.get("from")
        legacy_target = values.get("to")

        if isinstance(legacy_source, dict):
            values.setdefault("source", legacy_source.get("node"))
            values.setdefault("source_output", legacy_source.get("port"))

        if isinstance(legacy_target, dict):
            values.setdefault("target", legacy_target.get("node"))
            values.setdefault("target_input", legacy_target.get("port"))

        if isinstance(values.get("source"), dict):
            source_dict = values["source"]
            values["source"] = source_dict.get("node")
            values.setdefault("source_output", source_dict.get("output"))

        if isinstance(values.get("target"), dict):
            target_dict = values["target"]
            values["target"] = target_dict.get("node")
            values.setdefault("target_input", target_dict.get("input"))

        return values

    def source_node(self) -> Optional[str]:
        return self.source

    def target_node(self) -> Optional[str]:
        return self.target

    def source_port(self) -> str:
        return self.source_output or "output"

    def target_port(self) -> str:
        return self.target_input or "input"

class FlowDSL(BaseModel):
    metadata: Dict[str, Any] = {}
    nodes: List[Node] = []
    edges: List[Edge] = []
    secrets_reference: Optional[Dict[str, Any]] = Field(default=None, alias="secrets_reference")
    policies: Optional[Dict[str, Any]] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_secrets_reference(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(values, dict):
            return values
        if "secrets_reference" not in values and "secrets_ref" in values:
            values["secrets_reference"] = values.get("secrets_ref")
        return values

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
            source_node = edge.source_node()
            target_node = edge.target_node()
            if not source_node or not target_node:
                continue
            self.graph.add_edge(source_node, target_node, id=edge.id)

    def validate(self) -> ValidationResult:
        errors = []
        warnings = []

        # 0. Check for invalid edges
        node_ids = {node.id for node in self.dsl.nodes}
        for edge in self.dsl.edges:
            source_node = edge.source_node()
            target_node = edge.target_node()
            if not source_node or not target_node:
                errors.append(f"Edge {edge.id} is missing source or target node.")
                continue
            if source_node not in node_ids or target_node not in node_ids:
                errors.append(f"Edge {edge.id} references unknown nodes: {source_node} -> {target_node}.")

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
