"""
Singleton MCP Client Manager for shared Tavily client initialization.
This prevents multiple Tavily client initializations and improves performance.
"""

import os
import logging
from typing import Optional, List
from llama_index.tools.mcp import BasicMCPClient
from llama_index.tools.mcp.base import McpToolSpec
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class MCPClientManager:
    """Singleton manager for MCP clients to avoid multiple initializations."""
    
    _instance: Optional['MCPClientManager'] = None
    _tavily_client: Optional[BasicMCPClient] = None
    _tavily_tools: Optional[List] = None
    _tavily_initialized: bool = False
    _brightdata_client: Optional[BasicMCPClient] = None
    _brightdata_tools: Optional[List] = None
    _brightdata_initialized: bool = False
    
    def __new__(cls) -> 'MCPClientManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def get_tavily_tools(self, api_token: Optional[str] = None) -> List:
        """Get Tavily MCP tools, initializing client if needed."""
        if self._tavily_initialized and self._tavily_tools:
            logger.info("Reusing existing Tavily MCP tools")
            return self._tavily_tools
        
        # Get API token
        token = api_token or os.getenv("TAVILY_API_KEY")
        if not token:
            raise ValueError("TAVILY_API_KEY is required")
        
        try:
            logger.info("Initializing Tavily MCP client...")
            
            # Create MCP client
            self._tavily_client = BasicMCPClient(f"https://mcp.tavily.com/mcp/?tavilyApiKey={token}")
            
            # Create MCP tool specification
            mcp_tool_spec = McpToolSpec(
                client=self._tavily_client,
                allowed_tools=["tavily_search", "tavily_extract"],
                include_resources=False
            )
            
            # Get tools from MCP
            self._tavily_tools = await mcp_tool_spec.to_tool_list_async()
            
            tool_names = [tool.metadata.name for tool in self._tavily_tools] if self._tavily_tools else []
            logger.info(f"Tavily MCP client initialized successfully with tools: {tool_names}")
            
            self._tavily_initialized = True
            return self._tavily_tools
            
        except Exception as e:
            logger.error(f"Failed to initialize Tavily MCP client: {e}")
            raise Exception(f"Tavily MCP client initialization failed: {e}")
    
    async def get_brightdata_tools(self, api_token: Optional[str] = None) -> List:
        """Get Bright Data MCP tools, initializing client if needed."""
        if self._brightdata_initialized and self._brightdata_tools:
            logger.info("Reusing existing Bright Data MCP tools")
            return self._brightdata_tools
        
        # Get API token
        token = api_token or os.getenv("BRIGHT_DATA_API_KEY")
        if not token:
            raise ValueError("BRIGHT_DATA_API_KEY is required")
        
        try:
            logger.info("Initializing Bright Data MCP client...")
            
            # Create MCP client
            self._brightdata_client = BasicMCPClient(f"https://mcp.brightdata.com/sse?token={token}&unlocker=mcp_unlocker")
            
            # Create MCP tool specification
            mcp_tool_spec = McpToolSpec(
                client=self._brightdata_client,
                allowed_tools=["search_engine", "scrape_as_markdown"],
                include_resources=False
            )
            
            # Get tools from MCP
            self._brightdata_tools = await mcp_tool_spec.to_tool_list_async()
            
            tool_names = [tool.metadata.name for tool in self._brightdata_tools] if self._brightdata_tools else []
            logger.info(f"Bright Data MCP client initialized successfully with tools: {tool_names}")
            
            self._brightdata_initialized = True
            return self._brightdata_tools
            
        except Exception as e:
            logger.error(f"Failed to initialize Bright Data MCP client: {e}")
            raise Exception(f"Bright Data MCP client initialization failed: {e}")
    
    def reset_tavily(self):
        """Reset the Tavily client (useful for testing or error recovery)."""
        logger.info("Resetting Tavily MCP client")
        self._tavily_client = None
        self._tavily_tools = None
        self._tavily_initialized = False
    
    def reset_brightdata(self):
        """Reset the Bright Data client (useful for testing or error recovery)."""
        logger.info("Resetting Bright Data MCP client")
        self._brightdata_client = None
        self._brightdata_tools = None
        self._brightdata_initialized = False
    
    def reset(self):
        """Reset all clients (useful for testing or error recovery)."""
        logger.info("Resetting all MCP clients")
        self.reset_tavily()
        self.reset_brightdata()

# Global instance
mcp_manager = MCPClientManager()
