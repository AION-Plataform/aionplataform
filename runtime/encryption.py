from cryptography.fernet import Fernet
from .config import config

# Use encryption key from config (environment variable)
ENCRYPTION_KEY = config.ENCRYPTION_KEY
cipher = Fernet(ENCRYPTION_KEY)

def encrypt_value(value: str) -> str:
    """Encrypt a secret value"""
    return cipher.encrypt(value.encode()).decode()

def decrypt_value(encrypted: str) -> str:
    """Decrypt a secret value"""
    return cipher.decrypt(encrypted.encode()).decode()
