import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

DB_PATH = "aion.db"

class UserRecord(BaseModel):
    id: str
    username: str
    hashed_password: str

class FlowRecord(BaseModel):
    id: str
    name: str
    dsl: Dict[str, Any]
    created_at: str
    user_id: Optional[str] = None

class ExecutionRecord(BaseModel):
    id: str
    flow_id: str
    status: str 
    result: Optional[Dict[str, Any]] = None
    started_at: str
    completed_at: Optional[str] = None
    user_id: Optional[str] = None

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Users Table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id TEXT PRIMARY KEY, username TEXT UNIQUE, hashed_password TEXT)''')

    # Flows Table
    # Note: Adding user_id column if it doesn't exist (simulating migration for MVP)
    c.execute('''CREATE TABLE IF NOT EXISTS flows
                 (id TEXT PRIMARY KEY, name TEXT, dsl TEXT, created_at TEXT, user_id TEXT)''')
    
    try:
        c.execute("ALTER TABLE flows ADD COLUMN user_id TEXT")
    except sqlite3.OperationalError:
        pass # Column likely exists

    # Executions Table
    c.execute('''CREATE TABLE IF NOT EXISTS executions
                 (id TEXT PRIMARY KEY, flow_id TEXT, status TEXT, result TEXT, 
                  started_at TEXT, completed_at TEXT, user_id TEXT)''')
    
    try:
         c.execute("ALTER TABLE executions ADD COLUMN user_id TEXT")
    except sqlite3.OperationalError:
        pass
    
    # Secrets Table (encrypted API keys)
    c.execute('''CREATE TABLE IF NOT EXISTS secrets
                 (id TEXT PRIMARY KEY, user_id TEXT, key TEXT, 
                  encrypted_value TEXT, created_at TEXT)''')

    conn.commit()
    conn.close()

# --- User Operations ---

def create_user(username: str, hashed_password: str) -> str:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    user_id = str(uuid.uuid4())
    try:
        c.execute("INSERT INTO users (id, username, hashed_password) VALUES (?, ?, ?)",
                  (user_id, username, hashed_password))
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        return None # User exists
    finally:
        conn.close()

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

# --- Flow Operations (Updated with user_id) ---

def create_flow(dsl: Dict[str, Any], user_id: str = None) -> str:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    flow_id = dsl.get("metadata", {}).get("name", "unknown") + "-" + str(uuid.uuid4())[:8]
    name = dsl.get("metadata", {}).get("name", "Unnamed Flow")
    created_at = datetime.utcnow().isoformat()
    
    c.execute("INSERT INTO flows (id, name, dsl, created_at, user_id) VALUES (?, ?, ?, ?, ?)",
              (flow_id, name, json.dumps(dsl), created_at, user_id))
    
    conn.commit()
    conn.close()
    return flow_id

def list_flows(user_id: str = None) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    query = "SELECT id, name, created_at, user_id FROM flows"
    params = []
    
    if user_id:
        query += " WHERE user_id = ?"
        params.append(user_id)
        
    query += " ORDER BY created_at DESC"
    
    c.execute(query, tuple(params))
    rows = c.fetchall()
    
    flows = [dict(row) for row in rows]
    conn.close()
    return flows

def get_flow(flow_id: str, user_id: str = None) -> Optional[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    query = "SELECT * FROM flows WHERE id = ?"
    params = [flow_id]
    
    # If user_id is provided, enforce ownership (rudimentary)
    # Ideally checking if shared etc, but for MVP strict ownership
    if user_id:
        query += " AND user_id = ?"
        params.append(user_id)

    c.execute(query, tuple(params))
    row = c.fetchone()
    conn.close()
    
    if row:
        data = dict(row)
        data["dsl"] = json.loads(data["dsl"])
        return data
    return None

def update_flow(flow_id: str, dsl: Dict[str, Any], user_id: str = None) -> bool:
    """Update a flow's DSL (with ownership check)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    name = dsl.get("metadata", {}).get("name", "Unnamed Flow")
    
    query = "UPDATE flows SET dsl = ?, name = ? WHERE id = ?"
    params = [json.dumps(dsl), name, flow_id]
    
    if user_id:
        query += " AND user_id = ?"
        params.append(user_id)
    
    c.execute(query, tuple(params))
    updated = c.rowcount > 0
    
    conn.commit()
    conn.close()
    return updated

def delete_flow(flow_id: str, user_id: str = None) -> bool:
    """Delete a flow (with ownership check)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    query = "DELETE FROM flows WHERE id = ?"
    params = [flow_id]
    
    if user_id:
        query += " AND user_id = ?"
        params.append(user_id)
    
    c.execute(query, tuple(params))
    deleted = c.rowcount > 0
    
    conn.commit()
    conn.close()
    return deleted

# --- Execution Operations (Updated with user_id) ---

def create_execution(flow_id: str, user_id: str = None) -> str:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    exec_id = str(uuid.uuid4())
    started_at = datetime.utcnow().isoformat()
    status = "pending"
    
    c.execute("INSERT INTO executions (id, flow_id, status, started_at, user_id) VALUES (?, ?, ?, ?, ?)",
              (exec_id, flow_id, status, started_at, user_id))
    
    conn.commit()
    conn.close()
    return exec_id

def update_execution(exec_id: str, status: str, result: Optional[Dict[str, Any]] = None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    completed_at = datetime.utcnow().isoformat() if status in ["completed", "failed"] else None
    result_json = json.dumps(result) if result else None
    
    query = "UPDATE executions SET status = ?"
    params = [status]
    
    if result_json:
        query += ", result = ?"
        params.append(result_json)
        
    if completed_at:
        query += ", completed_at = ?"
        params.append(completed_at)
        
    query += " WHERE id = ?"
    params.append(exec_id)
    
    c.execute(query, tuple(params))
    conn.commit()
    conn.close()

def get_execution(exec_id: str, user_id: str = None) -> Optional[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    query = "SELECT * FROM executions WHERE id = ?"
    params = [exec_id]
    
    if user_id:
        query += " AND user_id = ?"
        params.append(user_id)

    c.execute(query, tuple(params))
    row = c.fetchone()
    conn.close()
    
    if row:
        data = dict(row)
        if data["result"]:
            data["result"] = json.loads(data["result"])
        return data
    return None
