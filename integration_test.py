import sys
import os
import json
import asyncio

# Add current directory to sys.path to ensure imports work
sys.path.append(os.getcwd())

from compiler.compiler import AIONCompiler
from runtime.executor import AIONRuntime

async def run_test():
    print("=== AION Integration Test ===")
    
    # 1. Load DSL
    dsl_path = "examples/simple_flow.json"
    print(f"[1] Loading DSL from {dsl_path}...")
    with open(dsl_path, 'r') as f:
        dsl = json.load(f)
    
    # 2. Compile
    print("[2] Compiling Flow...")
    compiler = AIONCompiler()
    try:
        plan = compiler.compile(dsl)
        print("    Compilation Successful!")
        # print(json.dumps(plan, indent=2))
    except Exception as e:
        print(f"    Compilation Failed: {e}")
        return

    # 3. Execute
    print("[3] Executing Plan...")
    runtime = AIONRuntime()
    try:
        result = await runtime.execute_plan(plan)
        print("    Execution Successful!")
        print(f"    Results: {json.dumps(result, indent=2)}")
    except Exception as e:
         print(f"    Execution Failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_test())
