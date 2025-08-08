import os
from llama_index.core.agent.workflow import ReActAgent
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.tools.mcp import BasicMCPClient
from llama_index.tools.mcp.base import McpToolSpec
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List
from llama_index.core.agent.workflow import AgentStream, AgentOutput, ToolCallResult, ToolCall
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Restaurant(BaseModel):
    name: str = Field(description="the name of the restaurant")
    cuisine: str = Field(description="the cuisine of the restaurant")
    rating: float = Field(description="the rating of the restaurant")
    location: str = Field(description="the location of the restaurant")
    lunch_budget: str = Field(description="the budget of the restaurant")
    dinner_budget: str = Field(description="the budget of the restaurant")
    link: str = Field(description="the link to the restaurant")

class RestaurantOutput(BaseModel):
    restaurants: List[Restaurant] = Field(description="the list of restaurants")

class RestaurantAgent:
    """Agent for scraping restaurant information using MCP (Model Context Protocol) tools."""
    
    def __init__(self, api_token: str = None):
        """Initialize the MCP agent with API token."""
        self.api_token = api_token or os.getenv("TAVILY_API_KEY")
        if not self.api_token:
            raise ValueError("TAVILY_API_KEY is required")
        
        self.agent = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize the MCP client and agent."""
        if self._initialized:
            return
            
        try:
            # Create MCP client
            http_client = BasicMCPClient(f"https://mcp.tavily.com/mcp/?tavilyApiKey={self.api_token}")
            
            # Create MCP tool specification
            mcp_tool_spec = McpToolSpec(
                client=http_client,
                include_resources=False
            )
            
            # Get tools from MCP
            tools = await mcp_tool_spec.to_tool_list_async()

            tool_names = [tool.metadata.name for tool in tools]
            logger.info(f"Loaded MCP tools: {tool_names}")
            
            # Create the agent with better error handling
            try:
                llm = GoogleGenAI(
                    model="gemini-2.5-pro",
                    api_key=os.getenv("GOOGLE_API_KEY"),
                    temperature=0.1,
                    max_tokens=8192,
                    max_retries=3,
                    timeout=60.0
                )
                logger.info("Google GenAI LLM initialized successfully for restaurant agent")
            except Exception as llm_error:
                logger.error(f"Failed to initialize Google GenAI LLM for restaurant agent: {llm_error}")
                raise Exception(f"LLM initialization failed: {llm_error}")
            
            self.agent = ReActAgent(
                tools=tools,
                name="restaurant_agent",
                description="Extracts the top restaurants",
                llm=llm,
                system_prompt="""You are a restaurant search expert with comprehensive web scraping capabilities. Your tools include:

scrape_as_markdown: Extract content from any webpage with bot detection bypass
Structured extractors: Fast, reliable data from major platforms
Browser automation: Navigate, click, type, screenshot for complex interactions

Your goal is to find the best restaurant options by:
1. Searching major restaurant review sites (Tabelog, Yelp, OpenTable, TripAdvisor, Google Maps)
2. Using scrape_as_markdown to extract comprehensive restaurant information
3. Extracting detailed restaurant data including:
   - Restaurant names and cuisine types
   - Complete addresses with neighborhood/district information
   - Phone numbers and website URLs
   - Operating hours and reservation information
   - Ratings and review counts from multiple sources
   - Price ranges and average cost per person
   - Special features (outdoor seating, delivery, takeout, etc.)
   - Popular dishes and menu highlights
   - Photos and image URLs when available

IMPORTANT:
- Always use "scrape_as_markdown" for webpage content extraction
- Always provide accurate, real restaurant data with current information
- Try multiple sites if needed for comprehensive results
- Focus on finding at least 3-5 different restaurant options with varying cuisines, price points, and locations
- NEVER RETURN EMPTY RESULTS - always return at least 2-3 restaurants if available
- Prioritize highly-rated restaurants with good reviews and reasonable prices
- Include direct booking/contact URLs for each restaurant when available
- Focus on restaurants that are currently open and accepting customers

You MUST return your response in the exact JSON format with a 'restaurants' field containing a list of restaurant objects.""",
                output_cls=RestaurantOutput,
            )
            
            self._initialized = True
            
        except Exception as e:
            raise Exception(f"Failed to initialize MCP agent: {e}")
    
    async def scrape_restaurants(self, query: str = None, stream: bool = False) -> RestaurantOutput:
        """Scrape restaurant information using the MCP agent."""
        if not self._initialized:
            await self.initialize()
        
        try:
            default_query = "Give me the markdown of the top 3 highest rated restaurants in Tokyo"
            if stream:
                handler = self.agent.run(query or default_query)
                current_agent = None
                async for event in handler.stream_events():
                    if isinstance(event, AgentStream):
                        print(event.delta, end="", flush=True)
                    if (
                        hasattr(event, "current_agent_name")
                        and event.current_agent_name != current_agent
                    ):
                        current_agent = event.current_agent_name
                        print(f"\n{'='*50}")
                        print(f"🤖 Agent: {current_agent}")
                        print(f"{'='*50}\n")
                    elif isinstance(event, AgentOutput):
                        if event.response.content:
                            print("📤 Output:", event.response.content)
                        if event.tool_calls:
                            print(
                            "🛠️  Planning to use tools:",
                            [call.tool_name for call in event.tool_calls],
                        )
                    elif isinstance(event, ToolCallResult):
                        print(f"🔧 Tool Result ({event.tool_name}):")
                        print(f"  Arguments: {event.tool_kwargs}")
                        print(f"  Output: {event.tool_output}")
                    elif isinstance(event, ToolCall):
                        print(f"🔨 Calling Tool: {event.tool_name}")
                        print(f"  With arguments: {event.tool_kwargs}")
                result = await handler
                return result.structured_response
            else:
                response = await self.agent.run(query or default_query)
                return response.structured_response
        except Exception as e:
            logger.error(f"Error in scraping restaurants: {e}")
            return RestaurantOutput(restaurants=[])
    
    async def run_custom_query(self, query: str) -> RestaurantOutput:
        """Run a custom query using the MCP agent."""
        if not self._initialized:
            await self.initialize()
        
        try:
            response = await self.agent.run(query)
            return response.structured_response
        except Exception as e:
            logger.error(f"Error in running custom query: {e}")
            return RestaurantOutput(restaurants=[])


# Convenience function for backward compatibility
async def search_restaurants() -> RestaurantOutput:
    """Legacy function for backward compatibility."""
    try:
        agent = RestaurantAgent()
        return await agent.scrape_restaurants()
    except Exception as e:
        logger.error(f"Error in search_restaurants: {e}")
        return RestaurantOutput(restaurants=[])
