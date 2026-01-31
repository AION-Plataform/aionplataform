import json
import argparse
from typing import Dict, Any
from .compiler import AIONCompiler

def load_json(path: str) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(description="AION Compiler CLI")
    parser.add_argument("input_file", help="Path to input DSL JSON file")
    parser.add_argument("--output", help="Path to output Execution Plan JSON file", default="plan.json")
    
    args = parser.parse_args()
    
    try:
        dsl = load_json(args.input_file)
        compiler = AIONCompiler()
        plan = compiler.compile(dsl)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2)
            
        print(f"Successfully compiled '{args.input_file}' to '{args.output}'")
        
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
