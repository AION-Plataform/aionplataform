import sys
import os
import json
import asyncio

sys.path.append(os.getcwd())

from compiler.compiler import AIONCompiler
from runtime.executor import AIONRuntime

async def run_rag_test():
    print("=== AION RAG Test ===")
    
    # 1. Load DSL
    dsl_path = "examples/rag_flow.json"
    print(f"[1] Loading DSL from {dsl_path}...")
    with open(dsl_path, 'r') as f:
        dsl = json.load(f)
    
    # 2. Compile
    print("[2] Compiling Flow...")
    compiler = AIONCompiler()
    try:
        plan = compiler.compile(dsl)
        print("    Compilation Successful!")
    except Exception as e:
        print(f"    Compilation Failed: {e}")
        return

    # 3. Execute
    print("[3] Executing Plan...")
    runtime = AIONRuntime()
    try:
        result = await runtime.execute_plan(plan)
        print("    Execution Successful!")
        print(f"    Results keys: {list(result['results'].keys())}")
        
        # Validate Embeddings present
        store_res = result['results'].get('step_store', {})
        print(f"    Store Result: {store_res}")
        
    except Exception as e:
         print(f"    Execution Failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_rag_test())
