# Append to database.py - Secrets CRUD

class SecretRecord(BaseModel):
    id: str
    user_id: str
    key: str
    encrypted_value: str
    created_at: str

def create_secret(user_id: str, key: str, encrypted_value: str) -> str:
    """Create a new secret"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    secret_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    
    c.execute(
        "INSERT INTO secrets (id, user_id, key, encrypted_value, created_at) VALUES (?, ?, ?, ?, ?)",
        (secret_id, user_id, key, encrypted_value, created_at)
    )
    
    conn.commit()
    conn.close()
    return secret_id

def list_secrets(user_id: str) -> List[Dict[str, Any]]:
    """List all secrets for a user (values masked)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("SELECT id, key, created_at FROM secrets WHERE user_id = ?", (user_id,))
    rows = c.fetchall()
    conn.close()
    
    return [
        {
            "id": row[0],
            "key": row[1],
            "value": "••••••",  # Masked
            "created_at": row[2]
        }
        for row in rows
    ]

def get_secret_value(user_id: str, key: str) -> Optional[str]:
    """Get decrypted secret value by key"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("SELECT encrypted_value FROM secrets WHERE user_id = ? AND key = ?", (user_id, key))
    row = c.fetchone()
    conn.close()
    
    if row:
        return row[0]  # Return encrypted value (decrypt in caller)
    return None

def delete_secret(secret_id: str, user_id: str) -> bool:
    """Delete a secret"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("DELETE FROM secrets WHERE id = ? AND user_id = ?", (secret_id, user_id))
    deleted = c.rowcount > 0
    
    conn.commit()
    conn.close()
    return deleted
