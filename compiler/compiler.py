import networkx as nx
from typing import List, Dict, Any
from pydantic import BaseModel
from .validator import GraphValidator, FlowDSL

class ExecutionStep(BaseModel):
    step_id: str
    node_id: str
    node_type: str
    config: Dict[str, Any]
    depends_on: List[str] # List of node_ids this step depends on

class ExecutionPlan(BaseModel):
    flow_id: str
    steps: List[ExecutionStep]
    metadata: Dict[str, Any]

class AIONCompiler:
    def __init__(self):
        pass

    def compile(self, dsl_json: Dict[str, Any]) -> Dict[str, Any]:
        validator = GraphValidator(dsl_json)
        result = validator.validate()
        
        if not result.valid:
            raise ValueError(f"Flow validation failed: {result.errors}")

        # Topological Sort for Execution Order
        try:
            ordered_nodes = list(nx.topological_sort(validator.graph))
        except nx.NetworkXUnfeasible:
            raise ValueError("Cannot compile: Graph has cycles.")

        steps = []
        node_map = {n.id: n for n in validator.dsl.nodes}

        for node_id in ordered_nodes:
            node = node_map[node_id]
            # Find dependencies (parents)
            dependencies = list(validator.graph.predecessors(node_id))
            
            step = ExecutionStep(
                step_id=f"step_{node_id}",
                node_id=node.id,
                node_type=node.type,
                config=node.config,
                depends_on=dependencies
            )
            steps.append(step)

        plan = ExecutionPlan(
            flow_id=validator.dsl.metadata.get("name", "unknown"),
            steps=steps,
            metadata={
                "compiled_at": "now", # Placeholder
                "original_metadata": validator.dsl.metadata
            }
        )

        return plan.dict()
