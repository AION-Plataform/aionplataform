import requests
import json
import time
import uuid

BASE_URL = "http://localhost:8000"

def test_copilot():
    print("=== AION Copilot Test ===")

    # 0. Auth
    username = f"copilot_test_{uuid.uuid4().hex[:6]}"
    password = "password123"
    requests.post(f"{BASE_URL}/auth/register", json={"username": username, "password": password})
    r = requests.post(f"{BASE_URL}/auth/token", data={"username": username, "password": password})
    if r.status_code != 200:
        print("Auth failed")
        return
    headers = {"Authorization": f"Bearer {r.json()['access_token']}"}
    
    # 1. Generate RAG Flow
    print("[1] Generating 'RAG' Flow...")
    resp = requests.post(f"{BASE_URL}/copilot/generate", json={"prompt": "I need a RAG pipeline for PDF docs"}, headers=headers)
    if resp.status_code == 200:
        dsl = resp.json()["dsl"]
        print(f"    Generated Flow Name: {dsl['metadata']['name']}")
        print(f"    Node Count: {len(dsl['nodes'])}")
        
        # Verify result contains PDF loader
        if any(n["type"] == "loader.pdf" for n in dsl["nodes"]):
             print("    [PASS] Contains loader.pdf")
        else:
             print("    [FAIL] Missing loader.pdf")
    else:
        print(f"    [FAIL] Error: {resp.text}")

    # 2. Validate Bad Flow
    print("[2] Validating Incomplete Flow...")
    bad_flow = {
        "metadata": {"name": "Bad Flow", "version": "1.0", "created_at": "", "owner": "test"},
        "nodes": [
            {"id": "n1", "type": "rag.chunk", "version": "1.0", "config": {}} 
            # Missing vector store, should trigger rule
        ],
        "edges": []
    }
    
    resp = requests.post(f"{BASE_URL}/copilot/validate", json={"dsl": bad_flow}, headers=headers)
    if resp.status_code == 200:
        result = resp.json()
        print(f"    Valid: {result['valid']}")
        print(f"    Suggestions: {result['suggestions']}")
        
        if "vector store" in str(result['suggestions']).lower():
            print("    [PASS] Detected missing vector store")
        else:
            print("    [FAIL] Did not detect issue")
    else:
        print(f"    [FAIL] Error: {resp.text}")

if __name__ == "__main__":
    test_copilot()
