"""Configuration settings for SAINIK"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Core SAINIK settings"""
    
    app_name: str = "SAINIK"
    app_version: str = "0.1.0"
    debug: bool = True
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Supabase (optional for local dev, use SQLite as fallback)
    supabase_url: Optional[str] = os.getenv("SUPABASE_URL")
    supabase_key: Optional[str] = os.getenv("SUPABASE_KEY")
    
    # Database (SQLite for local dev)
    database_url: str = "sqlite:///./sainik.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
