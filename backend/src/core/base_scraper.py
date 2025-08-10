"""
Base scraper class with common functionality for all scrapers
Provides caching, retry logic, and browser management
"""

from abc import ABC, abstractmethod
from playwright.async_api import async_playwright, Page, Browser
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import asyncio
from core.logger import ScraperLogger
from core.config import get_scraper_config


class ScraperCache:
    """Simple in-memory cache for scraper results"""
    
    def __init__(self):
        self.cache = {}
        
    def get_key(self, params: Dict) -> str:
        """Generate cache key from parameters"""
        # Sort keys for consistent hashing
        sorted_params = json.dumps(params, sort_keys=True)
        return hashlib.md5(sorted_params.encode()).hexdigest()
        
    def get(self, params: Dict) -> Optional[Any]:
        """Get cached data if available and not expired"""
        key = self.get_key(params)
        if key in self.cache:
            entry = self.cache[key]
            if entry['expires'] > datetime.now():
                return entry['data']
            else:
                # Remove expired entry
                del self.cache[key]
        return None
        
    def set(self, params: Dict, data: Any, ttl: int = 3600):
        """Cache data with TTL"""
        key = self.get_key(params)
        self.cache[key] = {
            'data': data,
            'expires': datetime.now() + timedelta(seconds=ttl)
        }
        
    def clear(self):
        """Clear all cached data"""
        self.cache.clear()


class BaseScraper(ABC):
    """Base class for all scrapers with common functionality"""
    
    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__
        self.logger = ScraperLogger(self.name)
        self.config = get_scraper_config()
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.cache = ScraperCache()
        
    async def initialize(self):
        """Initialize browser with optimal settings"""
        self.logger.start("Initializing browser")
        
        try:
            playwright = await async_playwright().start()
            
            # Browser launch options
            launch_options = {
                'headless': self.config['headless'],
                'args': [
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-accelerated-2d-canvas',
                    '--disable-gpu'
                ]
            }
            
            self.browser = await playwright.chromium.launch(**launch_options)
            
            # Context options for stealth
            context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York'
            )
            
            # Add stealth scripts
            await context.add_init_script("""
                // Remove webdriver flag
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Add chrome object
                window.chrome = {
                    runtime: {}
                };
                
                // Add permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """)
            
            self.page = await context.new_page()
            self.page.set_default_timeout(self.config['timeout'])
            
            self.logger.logger.info("✅ Browser initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize browser: {e}")
            raise
            
    async def close(self):
        """Clean shutdown of browser"""
        if self.browser:
            await self.browser.close()
            self.logger.logger.info("Browser closed")
            
    async def wait_and_scroll(self, wait_time: int = 3000, scroll_times: int = 3):
        """Wait for page load and scroll to load dynamic content"""
        await self.page.wait_for_timeout(wait_time)
        
        for i in range(scroll_times):
            await self.page.evaluate('window.scrollBy(0, 1000)')
            await self.page.wait_for_timeout(500)
            self.logger.progress(f"Scrolled {i+1}/{scroll_times}")
            
    async def retry_on_failure(self, func, max_retries: int = None):
        """Retry a function on failure with exponential backoff"""
        max_retries = max_retries or self.config['max_retries']
        
        for attempt in range(max_retries):
            try:
                return await func()
            except Exception as e:
                if attempt == max_retries - 1:
                    self.logger.error(f"All retries failed: {e}")
                    raise
                    
                wait_time = 2 ** attempt  # Exponential backoff
                self.logger.error(f"Attempt {attempt + 1} failed: {e}", retry=True)
                await asyncio.sleep(wait_time)
                
    async def search_with_cache(self, params: Dict) -> Any:
        """Search with caching support"""
        # Check cache first
        cached_data = self.cache.get(params)
        if cached_data:
            self.logger.cached(self.cache.get_key(params))
            return cached_data
            
        # Perform search
        data = await self.search(params)
        
        # Cache results
        if data:
            self.cache.set(params, data, self.config['cache_ttl'])
            
        return data
        
    @abstractmethod
    async def search(self, params: Dict) -> Any:
        """
        Abstract search method to be implemented by subclasses
        
        Args:
            params: Search parameters
            
        Returns:
            Search results
        """
        pass
        
    def extract_text_safe(self, element, selector: str, default: str = "") -> str:
        """Safely extract text from an element"""
        try:
            found = element.select_one(selector)
            return found.get_text(strip=True) if found else default
        except:
            return default
            
    def extract_number_safe(self, text: str, default: float = 0.0) -> float:
        """Safely extract number from text"""
        import re
        try:
            # Remove currency symbols and commas
            cleaned = re.sub(r'[^0-9.]', '', text)
            return float(cleaned) if cleaned else default
        except:
            return default