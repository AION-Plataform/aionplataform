import sys
import os
import json
import asyncio

sys.path.append(os.getcwd())

from compiler.compiler import AIONCompiler
from runtime.executor import AIONRuntime

async def run_full_test():
    dsl_path = "examples/full_rag_gen.json"
    print(f"Loading {dsl_path}...")
    with open(dsl_path, 'r') as f:
        dsl = json.load(f)

    compiler = AIONCompiler()
    try:
        plan = compiler.compile(dsl)
    except Exception as e:
        print(f"Compilation Failed: {e}")
        return

    runtime = AIONRuntime()
    result = await runtime.execute_plan(plan)
    
    print("Execution Result Keys:", result["results"].keys())
    llm_res = result["results"].get("step_generator", {})
    print("LLM Output:", llm_res.get("output", "No Output"))

if __name__ == "__main__":
    asyncio.run(run_full_test())
