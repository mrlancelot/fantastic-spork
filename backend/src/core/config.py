"""
Centralized configuration for the TravelAI backend
Clean, minimal, and effective configuration management
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Keys (only what we need)
    openrouter_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None
    
    # Scraper Settings
    scraper_headless: bool = True
    scraper_timeout: int = 30000
    scraper_max_retries: int = 3
    cache_ttl: int = 3600  # 1 hour cache
    
    # Agent Settings
    agent_thinking_enabled: bool = True
    agent_stream_delay: float = 0.1
    agent_max_results: int = 10
    
    # Application Settings
    environment: str = "production"
    debug: bool = False
    log_level: str = "INFO"
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Convenience function to get specific settings
def get_api_keys():
    """Get API keys from settings"""
    settings = get_settings()
    return {
        "openrouter": settings.openrouter_api_key,
        "tavily": settings.tavily_api_key
    }


def is_development() -> bool:
    """Check if running in development mode"""
    settings = get_settings()
    return settings.environment == "development" or settings.debug


def get_scraper_config():
    """Get scraper configuration"""
    settings = get_settings()
    return {
        "headless": settings.scraper_headless,
        "timeout": settings.scraper_timeout,
        "max_retries": settings.scraper_max_retries,
        "cache_ttl": settings.cache_ttl
    }