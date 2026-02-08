import unittest
import asyncio

from compiler.compiler import AIONCompiler
from runtime.executor import AIONRuntime


class TestDSLExecution(unittest.IsolatedAsyncioTestCase):
    async def test_compiler_and_runtime_execute_simple_flow(self):
        dsl = {
            "metadata": {"name": "test-flow", "version": "1.0.0"},
            "nodes": [
                {"id": "src", "type": "loader.static", "version": "1.0.0", "config": {"text": "hello"}},
                {"id": "clean", "type": "transform.clean", "version": "1.0.0", "config": {}},
            ],
            "edges": [
                {
                    "id": "e1",
                    "source": "src",
                    "source_output": "content",
                    "target": "clean",
                    "target_input": "content",
                }
            ],
        }

        compiler = AIONCompiler()
        plan = compiler.compile(dsl)
        self.assertEqual(plan["flow_id"], "test-flow")
        self.assertEqual(len(plan["steps"]), 2)

        runtime = AIONRuntime()
        result = await runtime.execute_plan(plan)
        self.assertEqual(result["status"], "success")
        self.assertIn("step_src", result["results"])
        self.assertIn("step_clean", result["results"])


if __name__ == "__main__":
    unittest.main()
