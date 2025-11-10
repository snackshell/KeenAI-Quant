"""
Core Configuration Management for KeenAI-Quant Backend
Centralized configuration loading and validation
"""

import os
from typing import Any, Dict, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    openrouter_api_key: str = Field(default="", env="OPENROUTER_API_KEY")
    openalgo_api_key: str = Field(default="", env="OPENALGO_API_KEY")
    
    # OpenAlgo Configuration
    openalgo_host: str = Field(default="http://127.0.0.1:5000", env="OPENALGO_HOST")
    
    # MT5 Configuration
    mt5_account: str = Field(default="", env="MT5_ACCOUNT")
    mt5_password: str = Field(default="", env="MT5_PASSWORD")
    mt5_server: str = Field(default="", env="MT5_SERVER")
    
    # Database
    database_url: str = Field(default="sqlite:///./data/keenai.db", env="DATABASE_URL")
    
    # Application Settings
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Security
    encryption_key: str = Field(default="", env="ENCRYPTION_KEY")
    app_key: str = Field(default="", env="APP_KEY")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_setting(key: str, default: Any = None) -> Any:
    """
    Get a setting value by key
    
    Args:
        key: Setting key (e.g., 'openrouter_api_key')
        default: Default value if key not found
        
    Returns:
        Setting value or default
    """
    return getattr(settings, key, default)


def validate_required_settings() -> Dict[str, bool]:
    """
    Validate that required settings are present
    
    Returns:
        Dictionary of setting names and their validation status
    """
    required = {
        'openrouter_api_key': bool(settings.openrouter_api_key),
        'database_url': bool(settings.database_url),
    }
    
    optional = {
        'openalgo_api_key': bool(settings.openalgo_api_key),
        'mt5_account': bool(settings.mt5_account),
    }
    
    return {
        'required': required,
        'optional': optional,
        'all_required_present': all(required.values())
    }
