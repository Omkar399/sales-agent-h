"""Configuration settings for the Sales Agent Backend."""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings."""
    
    # API Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sales_agent.db")
    
    # AI Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # External APIs
    HUBSPOT_API_KEY: str = os.getenv("HUBSPOT_API_KEY", "")
    GOOGLE_CALENDAR_CREDENTIALS_PATH: str = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_PATH", "")
    
    # Gmail API Configuration
    GMAIL_CLIENT_ID: str = os.getenv("GMAIL_CLIENT_ID", "")
    GMAIL_CLIENT_SECRET: str = os.getenv("GMAIL_CLIENT_SECRET", "")
    GMAIL_REFRESH_TOKEN: str = os.getenv("GMAIL_REFRESH_TOKEN", "")
    
    # CORS
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
    
    # Application
    PROJECT_NAME: str = "Sales Agent Dashboard"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI-powered sales dashboard with Kanban board and intelligent assistant"


settings = Settings()
