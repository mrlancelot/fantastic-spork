"""
Centralized LLM Manager for all agents.
Provides consistent LLM configuration and fallback logic across the application.
"""

import os
import logging
from typing import Optional, Dict, Any, Union
from enum import Enum
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.llms.openai import OpenAI
from dotenv import load_dotenv


from .cerebras_llm import CerebrasLLM

load_dotenv()
logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    """Supported LLM providers."""
    GOOGLE_GEMINI = "google_gemini"
    OPENAI = "openai"
    OPENROUTER = "openrouter"
    CEREBRAS = "cerebras"

class LLMProfile(Enum):
    """Pre-configured LLM profiles for different use cases."""
    FAST = "fast"
    BALANCED = "balanced"
    POWERFUL = "powerful"
    BUDGET = "budget"
    CEREBRAS_FAST = "cerebras_fast"

class LLMManager:
    """Singleton manager for LLM instances with centralized configuration."""
    _instance: Optional['LLMManager'] = None
    _llm_cache: Dict[str, Any] = {}

    _profile_configs = {
        LLMProfile.FAST: {
            "provider": LLMProvider.GOOGLE_GEMINI,
            "model": "models/gemini-2.5-flash",
            "temperature": 0.1,
            "max_tokens": 4096,
            "max_retries": 3,
            "timeout": 30.0,
            "request_timeout": 30.0
        },
        LLMProfile.BALANCED: {
            "provider": LLMProvider.GOOGLE_GEMINI,
            "model": "models/gemini-2.5-flash",
            "temperature": 0.1,
            "max_tokens": 4096,
            "max_retries": 3,
            "timeout": 30.0,
            "request_timeout": 30.0
        },
        LLMProfile.POWERFUL: {
            "provider": LLMProvider.GOOGLE_GEMINI,
            "model": "models/gemini-2.5-flash",
            "temperature": 0.1,
            "max_tokens": 8192,
            "max_retries": 3,
            "timeout": 60.0,
            "request_timeout": 60.0
        },
        LLMProfile.BUDGET: {
            "provider": LLMProvider.GOOGLE_GEMINI,
            "model": "models/gemini-2.5-flash",
            "temperature": 0.3,
            "max_tokens": 4096,
            "max_retries": 3,
            "timeout": 30.0,
            "request_timeout": 30.0
        },
        LLMProfile.CEREBRAS_FAST: {
            "provider": LLMProvider.GOOGLE_GEMINI,
            "model": "models/gemini-2.5-flash",
            "temperature": 0.1,
            "max_tokens": 4096,
            "max_retries": 3,
            "timeout": 30.0,
            "request_timeout": 30.0
        }
    }
    def __new__(cls) -> 'LLMManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    def get_llm(
        self, 
        profile: LLMProfile = LLMProfile.BALANCED,
        provider: Optional[LLMProvider] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> Union[GoogleGenAI, OpenAI, CerebrasLLM]:
        """
        Get an LLM instance with the specified configuration.
        Args:
            profile: Pre-configured profile to use
            provider: Override the provider from profile
            model: Override the model from profile
            **kwargs: Additional parameters to override profile defaults
        Returns:
            Configured LLM instance
        Raises:
            ValueError: If required API keys are missing
            Exception: If LLM initialization fails
        """

        cache_key = f"{profile.value}_{provider}_{model}_{hash(frozenset(kwargs.items()))}"

        if cache_key in self._llm_cache:
            logger.debug(f"Returning cached LLM instance: {cache_key}")
            return self._llm_cache[cache_key]

        config = self._profile_configs[profile].copy()

        if provider:
            config["provider"] = provider
        if model:
            config["model"] = model
        config.update(kwargs)

        llm_instance = self._create_llm_instance(config)

        self._llm_cache[cache_key] = llm_instance
        logger.info(f"Created and cached LLM instance: {config['provider'].value} - {config['model']}")
        return llm_instance
    def _create_llm_instance(self, config: Dict[str, Any]) -> Union[GoogleGenAI, OpenAI, CerebrasLLM]:
        """Create an LLM instance based on configuration."""
        provider = config["provider"]
        try:
            if provider == LLMProvider.GOOGLE_GEMINI:
                return self._create_google_gemini(config)
            elif provider == LLMProvider.OPENAI:
                return self._create_openai(config)
            elif provider == LLMProvider.OPENROUTER:
                return self._create_openrouter(config)
            elif provider == LLMProvider.CEREBRAS:
                return self._create_cerebras(config)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
        except Exception as e:
            logger.error(f"Failed to create LLM instance for {provider.value}: {e}")

            if provider != LLMProvider.GOOGLE_GEMINI:
                logger.info("Attempting fallback to Google Gemini Fast")
                fallback_config = self._profile_configs[LLMProfile.FAST].copy()
                return self._create_google_gemini(fallback_config)
            raise
    def _create_google_gemini(self, config: Dict[str, Any]) -> GoogleGenAI:
        """Create a Google Gemini LLM instance."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required for Google Gemini")
        return GoogleGenAI(
            model=config["model"],
            api_key=api_key,
            temperature=config.get("temperature", 0.1),
            max_tokens=config.get("max_tokens", 4096),
            max_retries=config.get("max_retries", 3),
            timeout=config.get("timeout", 30.0),
            request_timeout=config.get("request_timeout", 30.0)
        )
    def _create_openai(self, config: Dict[str, Any]) -> OpenAI:
        """Create an OpenAI LLM instance."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI")
        return OpenAI(
            model=config["model"],
            api_key=api_key,
            temperature=config.get("temperature", 0.1),
            max_tokens=config.get("max_tokens", 4096),
            max_retries=config.get("max_retries", 3),
            timeout=config.get("timeout", 30.0),
            request_timeout=config.get("request_timeout", 30.0)
        )
    def _create_openrouter(self, config: Dict[str, Any]) -> OpenAI:
        """Create an OpenRouter LLM instance."""
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required for OpenRouter")
        return OpenAI(
            model=config["model"],
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=config.get("temperature", 0.3),
            max_tokens=config.get("max_tokens", 4096),
            max_retries=config.get("max_retries", 3),
            timeout=config.get("timeout", 30.0),
            request_timeout=config.get("request_timeout", 30.0)
        )
    def _create_cerebras(self, config: Dict[str, Any]) -> CerebrasLLM:
        """Create a Cerebras LLM instance using the custom wrapper."""
        api_key = os.getenv("CEREBRAS_API_KEY")
        if not api_key:
            raise ValueError("CEREBRAS_API_KEY environment variable is required for Cerebras")
        return CerebrasLLM(
            model_name=config["model"],
            api_key=api_key,
            temperature=config.get("temperature", 0.1),
            max_tokens=config.get("max_tokens", 4096),
        )
    def clear_cache(self):
        """Clear the LLM cache (useful for testing or configuration changes)."""
        logger.info("Clearing LLM cache")
        self._llm_cache.clear()
    def get_available_providers(self) -> Dict[LLMProvider, bool]:
        """Check which LLM providers have valid API keys configured."""
        providers = {
            LLMProvider.GOOGLE_GEMINI: bool(os.getenv("GOOGLE_API_KEY")),
            LLMProvider.OPENAI: bool(os.getenv("OPENAI_API_KEY")),
            LLMProvider.OPENROUTER: bool(os.getenv("OPENROUTER_API_KEY")),
            LLMProvider.CEREBRAS: bool(os.getenv("CEREBRAS_API_KEY"))
        }
        return providers
    def update_profile_config(self, profile: LLMProfile, **kwargs):
        """Update configuration for a specific profile."""
        if profile in self._profile_configs:
            self._profile_configs[profile].update(kwargs)

            self.clear_cache()
            logger.info(f"Updated configuration for profile: {profile.value}")
        else:
            raise ValueError(f"Unknown profile: {profile}")


llm_manager = LLMManager()


def get_fast_llm(**kwargs) -> Union[GoogleGenAI, OpenAI, CerebrasLLM]:
    """Get a fast, cost-effective LLM for simple tasks."""
    return llm_manager.get_llm(LLMProfile.FAST, **kwargs)

def get_balanced_llm(**kwargs) -> Union[GoogleGenAI, OpenAI, CerebrasLLM]:
    """Get a balanced LLM for general use."""
    return llm_manager.get_llm(LLMProfile.BALANCED, **kwargs)

def get_powerful_llm(**kwargs) -> Union[GoogleGenAI, OpenAI, CerebrasLLM]:
    """Get the most capable LLM for complex tasks."""
    return llm_manager.get_llm(LLMProfile.POWERFUL, **kwargs)

def get_budget_llm(**kwargs) -> Union[GoogleGenAI, OpenAI, CerebrasLLM]:
    """Get the most cost-effective LLM available."""
    return llm_manager.get_llm(LLMProfile.BUDGET, **kwargs)

def get_cerebras_fast_llm(**kwargs) -> CerebrasLLM:
    """Get a fast Cerebras LLM for quick inference."""
    return llm_manager.get_llm(LLMProfile.CEREBRAS_FAST, **kwargs)
