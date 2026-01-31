"""
Configuration module for AION Platform
Loads environment variables and provides centralized config access
"""
import os
from typing import Optional
from dotenv import load_dotenv
from cryptography.fernet import Fernet

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration"""
    
    # Security Keys
    SECRET_KEY: str = os.getenv("SECRET_KEY", "aion-dev-secret-key-change-in-production")
    ENCRYPTION_KEY: bytes = os.getenv("ENCRYPTION_KEY", Fernet.generate_key()).encode() if isinstance(os.getenv("ENCRYPTION_KEY"), str) else Fernet.generate_key()
    
    # JWT Configuration
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "aion.db")
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # CORS
    CORS_ORIGINS: list = [
        origin.strip() 
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
    ]
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

# Global config instance
config = Config()

# Validate critical config on startup
if config.is_production and config.SECRET_KEY == "aion-dev-secret-key-change-in-production":
    raise ValueError("SECRET_KEY must be set in production environment!")
