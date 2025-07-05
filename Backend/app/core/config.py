from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    MONGODB_URL: str = "mongodb://admin:password123@localhost:27017/n8n_clone?authSource=admin"
    DATABASE_NAME: str = "n8n_clone"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # API Keys
    OPENAI_API_KEY: str = ""
    HASHNODE_API_KEY: str = ""
    TWITTER_API_KEY: str = ""
    TWITTER_API_SECRET: str = ""
    TWITTER_ACCESS_TOKEN: str = ""
    TWITTER_ACCESS_TOKEN_SECRET: str = ""
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # App
    APP_NAME: str = "N8N Clone"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()