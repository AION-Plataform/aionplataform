import requests
import json
import time
import uuid

BASE_URL = "http://localhost:8000"

def test_api():
    print("=== AION API Persistence Test ===")
    
    # 1. Health Check
    try:
        resp = requests.get(f"{BASE_URL}/")
        print(f"[1] Health Check: {resp.status_code}")
    except Exception as e:
        print(f"[!] Server not running? {e}")
        return

    # 1.1 Register & Login
    username = f"testuser_{uuid.uuid4().hex[:6]}"
    password = "password123"
    
    print(f"[1.1] Registering {username}...")
    requests.post(f"{BASE_URL}/auth/register", json={"username": username, "password": password})
    
    print(f"[1.2] Logging in...")
    r = requests.post(f"{BASE_URL}/auth/token", data={"username": username, "password": password})
    if r.status_code != 200:
        print(f"Login Failed: {r.text}")
        return
        
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"    Got Token: {token[:10]}...")

    # 2. Create Flow
    print("[2] Creating Flow...")
    with open("examples/simple_flow.json", "r") as f:
        dsl = json.load(f)
        
    resp = requests.post(f"{BASE_URL}/flows", json={"dsl": dsl}, headers=headers)
    if resp.status_code != 200:
        print(f"    Failed: {resp.text}")
        return
    
    flow_id = resp.json()["id"]
    print(f"    Created Flow ID: {flow_id}")

    # 3. List Flows
    print("[3] Listing Flows...")
    resp = requests.get(f"{BASE_URL}/flows", headers=headers)
    print(f"    Flows found: {len(resp.json())}")

    # 4. Execute Flow
    print("[4] Executing Flow...")
    resp = requests.post(f"{BASE_URL}/flows/{flow_id}/execute", params={"background_tasks": "true"}, headers=headers)
    if resp.status_code != 200:
        print(f"    Failed to start execution: {resp.text}")
        return
        
    exec_id = resp.json()["execution_id"]
    print(f"    Execution ID: {exec_id}")

    # 5. Poll Execution Status
    print("[5] Polling Status...")
    for _ in range(5):
        resp = requests.get(f"{BASE_URL}/executions/{exec_id}", headers=headers)
        data = resp.json()
        status = data["status"]
        print(f"    Status: {status}")
        
        if status in ["completed", "failed"]:
            print(f"    Result: {data.get('result')}")
            break
        time.sleep(1)

if __name__ == "__main__":
    test_api()
