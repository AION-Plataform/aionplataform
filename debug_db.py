import sqlite3
from passlib.context import CryptContext

print("--- DB Check ---")
try:
    conn = sqlite3.connect('aion.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", tables)
    conn.close()
except Exception as e:
    print("DB Error:", e)

print("\n--- Passlib Check ---")
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hash = pwd_context.hash("test1234")
    print("Hash success:", hash[:10] + "...")
except Exception as e:
    print("Passlib Error:", e)
