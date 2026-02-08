import asyncio
from typing import Dict, Any, List
from pydantic import BaseModel

# Duplicate definition for now to avoid package import issues across folders in this env
class InputBinding(BaseModel):
    source_node: str
    source_output: str
    target_input: str

class ExecutionStep(BaseModel):
    step_id: str
    node_id: str
    node_type: str
    config: Dict[str, Any]
    depends_on: List[str]
    input_bindings: List[InputBinding] = []

class ExecutionPlan(BaseModel):
    flow_id: str
    steps: List[ExecutionStep]
    metadata: Dict[str, Any]

class Executioncontext:
    def __init__(self):
        self.results = {} # step_id -> result
        self.state = {}

class AIONRuntime:
    def __init__(self):
        pass

    async def execute_plan(self, plan_data: Dict[str, Any]):
        plan = ExecutionPlan(**plan_data)
        context = Executioncontext()
        
        print(f"--- Starting Execution of Flow: {plan.flow_id} ---")
        
        # Simple sequential execution for MVP (since plan is already topologically sorted)
        # In a real scenario, this would use asyncio.gather for independent branches
        for step in plan.steps:
            await self._execute_step(step, context)
            
        print(f"--- Execution Completed ---")
        return {"status": "success", "results": context.results}

    async def _execute_step(self, step: ExecutionStep, context: Executioncontext):
        print(f"Running Step: {step.step_id} (Type: {step.node_type})")
        
        # Resolve Inputs from dependencies
        inputs = {}
        if step.input_bindings:
            for binding in step.input_bindings:
                dep_step_id = f"step_{binding.source_node}"
                if dep_step_id not in context.results:
                    continue
                source_result = context.results[dep_step_id]
                if isinstance(source_result, dict) and binding.source_output in source_result:
                    value = source_result[binding.source_output]
                else:
                    value = source_result

                if binding.target_input in inputs:
                    existing = inputs[binding.target_input]
                    if isinstance(existing, list):
                        existing.append(value)
                    else:
                        inputs[binding.target_input] = [existing, value]
                else:
                    inputs[binding.target_input] = value
        else:
            for dep_id in step.depends_on:
                dep_step_id = f"step_{dep_id}" # fallback mapping
                if dep_step_id in context.results:
                    inputs[dep_id] = context.results[dep_step_id]

        # Simulate Node Logic
        result = await self._simulate_node_execution(step.node_type, step.config, inputs)
        context.results[step.step_id] = result
        print(f"  -> Result: {result}")

    async def _simulate_node_execution(self, node_type: str, config: Dict[str, Any], inputs: Dict[str, Any]):
        from nodes.registry import NodeRegistry
        
        try:
            node_class = NodeRegistry.get_node_class(node_type)
            node_instance = node_class(config)
            return await node_instance.execute(inputs)
        except Exception as e:
            print(f"  [Error] Failed to execute node {node_type}: {e}")
            return {"error": str(e)}
