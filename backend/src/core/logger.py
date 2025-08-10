"""
Unified logging system for TravelAI
Provides consistent, clean logging across all components
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


# Color codes for terminal output
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""
    
    COLORS = {
        'DEBUG': Colors.GRAY,
        'INFO': Colors.BLUE,
        'WARNING': Colors.YELLOW,
        'ERROR': Colors.RED,
        'CRITICAL': Colors.MAGENTA
    }
    
    def format(self, record):
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{Colors.RESET}"
        
        # Add emoji indicators
        if levelname == 'INFO':
            record.msg = f"ℹ️  {record.msg}"
        elif levelname == 'WARNING':
            record.msg = f"⚠️  {record.msg}"
        elif levelname == 'ERROR':
            record.msg = f"❌ {record.msg}"
        elif levelname == 'DEBUG':
            record.msg = f"🔍 {record.msg}"
            
        return super().format(record)


def setup_logger(
    name: str,
    level: str = "INFO",
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Create a logger with console and optional file output
    
    Args:
        name: Logger name (usually module name)
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file to write logs to
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Set level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Console handler with color formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = ColoredFormatter(
        '%(asctime)s | %(name)-15s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Create file handler
        file_path = log_dir / log_file
        file_handler = logging.FileHandler(file_path)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(filename)s:%(lineno)d | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


class AgentLogger:
    """Specialized logger for agent operations"""
    
    def __init__(self, agent_name: str):
        self.logger = setup_logger(agent_name, log_file=f"{agent_name.lower()}.log")
        
    def thinking(self, thought: str):
        """Log agent thinking process"""
        self.logger.info(f"🧠 THINKING: {thought}")
        
    def searching(self, source: str, query: str):
        """Log search operations"""
        self.logger.info(f"🔍 SEARCHING {source}: {query}")
        
    def found(self, source: str, count: int):
        """Log search results"""
        self.logger.info(f"✅ FOUND {count} results from {source}")
        
    def analyzing(self, what: str):
        """Log analysis operations"""
        self.logger.info(f"🔬 ANALYZING: {what}")
        
    def recommending(self, what: str):
        """Log recommendations"""
        self.logger.info(f"💡 RECOMMENDING: {what}")
        
    def error(self, error: str, exc_info=False):
        """Log errors"""
        self.logger.error(f"ERROR: {error}", exc_info=exc_info)
        
    def performance(self, operation: str, duration: float):
        """Log performance metrics"""
        self.logger.debug(f"⚡ PERFORMANCE: {operation} took {duration:.2f}s")


class ScraperLogger:
    """Specialized logger for scraper operations"""
    
    def __init__(self, scraper_name: str):
        self.logger = setup_logger(scraper_name, log_file="scrapers.log")
        self.scraper_name = scraper_name
        
    def start(self, url: str):
        """Log scraper start"""
        self.logger.info(f"🚀 Starting {self.scraper_name} scraper: {url}")
        
    def progress(self, message: str):
        """Log scraper progress"""
        self.logger.debug(f"⏳ {message}")
        
    def extracted(self, count: int, item_type: str):
        """Log extraction results"""
        self.logger.info(f"📊 Extracted {count} {item_type}")
        
    def cached(self, key: str):
        """Log cache hit"""
        self.logger.debug(f"💾 Cache hit for key: {key}")
        
    def error(self, error: str, retry: bool = False):
        """Log scraper errors"""
        if retry:
            self.logger.warning(f"⚠️  Error (will retry): {error}")
        else:
            self.logger.error(f"❌ Error: {error}")


# Create default logger
default_logger = setup_logger("TravelAI")


def log_startup():
    """Log application startup"""
    default_logger.info("="*60)
    default_logger.info("🚀 TravelAI Backend Starting")
    default_logger.info(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    default_logger.info("="*60)


def log_shutdown():
    """Log application shutdown"""
    default_logger.info("="*60)
    default_logger.info("👋 TravelAI Backend Shutting Down")
    default_logger.info("="*60)