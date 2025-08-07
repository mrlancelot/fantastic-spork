"""Configuration Management - Clean settings for TravelAI Backend

Centralized configuration management using Pydantic Settings.
Handles environment variables and provides sensible defaults.
"""

import os
from typing import Optional, List
from pathlib import Path
from dotenv import load_dotenv

try:
    from pydantic_settings import BaseSettings
except ImportError:
    try:
        from pydantic import BaseSettings
    except ImportError:
        # Fallback for environments without pydantic
        class BaseSettings:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)

# Load environment variables from project root
project_root = Path(__file__).parent.parent.parent.parent
load_dotenv(project_root / '.env')

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # ========================================================================
    # APPLICATION SETTINGS
    # ========================================================================
    app_name: str = "TravelAI Backend"
    app_version: str = "2.1.0"
    debug: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # ========================================================================
    # EXTERNAL API KEYS
    # ========================================================================
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    openrouter_api_key: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    bright_data_api_token: Optional[str] = os.getenv("BRIGHT_DATA_API_TOKEN")
    amadeus_client_id: Optional[str] = os.getenv("AMADEUS_CLIENT_ID")
    amadeus_client_secret: Optional[str] = os.getenv("AMADEUS_CLIENT_SECRET")
    
    # ========================================================================
    # AUTHENTICATION & DATABASE
    # ========================================================================
    clerk_secret_key: Optional[str] = os.getenv("CLERK_SECRET_KEY")
    convex_url: Optional[str] = os.getenv("CONVEX_URL")
    convex_deployment: str = os.getenv("CONVEX_DEPLOYMENT", "production")
    
    # ========================================================================
    # EXTERNAL SERVICES
    # ========================================================================
    waypoint_base_url: str = os.getenv("WAYPOINT_BASE_URL", "http://localhost:8000")
    waypoint_enabled: bool = os.getenv("WAYPOINT_ENABLED", "true").lower() in ("true", "1", "yes")
    
    # ========================================================================
    # CORS & SECURITY
    # ========================================================================
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8000", 
        "https://fantastic-spork-alpha.vercel.app",
        "https://*.vercel.app"
    ]
    
    # ========================================================================
    # PERFORMANCE & LIMITS
    # ========================================================================
    api_timeout: int = int(os.getenv("API_TIMEOUT", "30"))
    max_concurrent_requests: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "100"))
    
    # ========================================================================
    # FEATURE FLAGS
    # ========================================================================
    enable_ai_features: bool = os.getenv("ENABLE_AI_FEATURES", "true").lower() in ("true", "1", "yes")
    enable_external_apis: bool = os.getenv("ENABLE_EXTERNAL_APIS", "true").lower() in ("true", "1", "yes")
    enable_caching: bool = os.getenv("ENABLE_CACHING", "false").lower() in ("true", "1", "yes")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables

# ============================================================================
# SETTINGS INSTANCE (Singleton Pattern)
# ============================================================================

_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get application settings instance (singleton pattern)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

# ============================================================================
# ENVIRONMENT HELPERS
# ============================================================================

def is_development() -> bool:
    """Check if running in development mode"""
    return get_settings().environment == "development"

def is_production() -> bool:
    """Check if running in production mode"""
    return get_settings().environment == "production"

def is_testing() -> bool:
    """Check if running in test mode"""
    return get_settings().environment == "testing"

def has_required_api_keys() -> dict:
    """Check which API keys are available"""
    settings = get_settings()
    return {
        "gemini": bool(settings.gemini_api_key),
        "openrouter": bool(settings.openrouter_api_key),
        "clerk": bool(settings.clerk_secret_key),
        "convex": bool(settings.convex_url),
        "amadeus": bool(settings.amadeus_client_id and settings.amadeus_client_secret),
        "bright_data": bool(settings.bright_data_api_token)
    }

def get_api_config() -> dict:
    """Get API configuration summary"""
    settings = get_settings()
    api_keys = has_required_api_keys()
    
    return {
        "environment": settings.environment,
        "debug": settings.debug,
        "version": settings.app_version,
        "available_services": {
            "ai_chat": api_keys["gemini"] or api_keys["openrouter"],
            "user_storage": api_keys["convex"] and api_keys["clerk"],
            "web_scraping": api_keys["bright_data"],
            "flight_search": api_keys["amadeus"],
            "waypoint_integration": settings.waypoint_enabled
        },
        "feature_flags": {
            "ai_features": settings.enable_ai_features,
            "external_apis": settings.enable_external_apis,
            "caching": settings.enable_caching
        }
    }
