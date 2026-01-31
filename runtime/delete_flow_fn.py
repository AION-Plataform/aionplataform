# Add to database.py after get_flow function

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
