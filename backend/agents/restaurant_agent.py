import os
from unittest import result
from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.workflow import Context
from pydantic import BaseModel, Field
from typing import List, Optional
from llama_index.core.agent.workflow import AgentStream, AgentOutput, ToolCallResult, ToolCall
import logging
from utils.llm_manager import get_powerful_llm

# Import constants and helper functions
from constants import (
    detect_country_from_query,
    TABELOG_BUDGET_MAPPING,
    extract_japan_location,
    extract_japan_budget,
    build_tabelog_url,
    extract_city_from_query,
    build_international_search_query,
    get_country_currency
)

# Import shared MCP client manager
from utils.mcp_client_manager import mcp_manager

from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Restaurant(BaseModel):
    name: str = Field(description="the name of the restaurant")
    cuisine: Optional[str] = Field(default=None, description="the cuisine of the restaurant (optional)")
    rating: Optional[float] = Field(default=None, description="the rating of the restaurant (optional)")
    location: Optional[str] = Field(default=None, description="the location of the restaurant")
    lunch_budget: Optional[str] = Field(default=None, description="the lunch budget of the restaurant (optional)")
    dinner_budget: Optional[str] = Field(default=None, description="the dinner budget of the restaurant (optional)")
    link: Optional[str] = Field(default=None, description="the link to the restaurant (optional)")
    source: Optional[str] = Field(default=None, description="the review website source from tavily_search (optional)")

class RestaurantOutput(BaseModel):
    restaurants: List[Restaurant] = Field(description="the list of restaurants")

class RestaurantAgent:
    """Agent for searching and extracting restaurant information using MCP (Model Context Protocol) tools."""
    
    def __init__(self, api_token: Optional[str] = None):
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
            # Get Tavily tools from shared MCP client manager
            tools = await mcp_manager.get_tavily_tools(self.api_token)
            
            # Create the agent with better error handling
            try:
                llm = get_powerful_llm()
                logger.info("LLM initialized successfully for restaurant agent")
            except Exception as llm_error:
                logger.error(f"Failed to initialize LLM for restaurant agent: {llm_error}")
                raise Exception(f"LLM initialization failed: {llm_error}")
            
            self.agent = ReActAgent(
                tools=tools,
                name="restaurant_agent",
                description="Searches and extracts top restaurants",
                llm=llm,
                system_prompt="""You are a restaurant search expert that handles queries differently based on the country.

FOR JAPAN QUERIES:
- You will receive a specific Tabelog URL to extract from
- Use tavily_extract tool with the provided URL
- The tool will extract the full page content in markdown format
- Parse the extracted content to identify restaurant information
- Focus on the first 10 restaurants from the Tabelog listing (already sorted by rating)

FOR OTHER COUNTRIES:
- Use tavily_search tool with the provided query and include_domains parameters
- The include_domains parameter restricts search to specific review sites
- Extract restaurant information from the search results
- You will be provided with the correct currency symbol to use

IMPORTANT: TAVILY_EXTRACT USAGE:
- The tool ONLY accepts a 'urls' parameter (array of URLs)
- It does NOT accept a 'query' parameter
- It returns the full page content in markdown format
- You must parse the returned content yourself to extract restaurant details
- The content will include restaurant names, ratings, locations, and other details

WHEN USING TAVILY_EXTRACT (for Japan):
- Pass only: {"urls": ["the_tabelog_url"]}
- Do NOT include a query parameter
- Parse the returned markdown content to find restaurants
- Look for patterns like ratings (e.g., "3.54"), restaurant names, locations, etc.

WHEN USING TAVILY_SEARCH (for other countries):
- The tool accepts these parameters:
  - query: The search query (e.g., "best italian restaurants in paris")
  - include_domains: Array of domains to search within (just domain names, e.g., ["yelp.com", "tripadvisor.com"])
- Example: {"query": "best restaurants in london", "include_domains": ["yelp.com"]}
- You will receive specific instructions with the query, domains, and currency to use
- Do NOT include 'country' parameter - it's not supported

EXTRACT THESE FIELDS FOR ALL RESTAURANTS:
- name: Restaurant name
- cuisine: Type of cuisine (Japanese, Italian, French, etc.)
- rating: Numerical rating (convert "4.5/5" → 4.5, "great" → 4.0, etc.)
- location: Area/neighborhood/address
- lunch_budget: Lunch price range (use local currency - e.g., "$10-15" for US, "€15-25" for France, "¥1000-2000" for Japan)
- dinner_budget: Dinner price range (use local currency - e.g., "$20-30" for US, "€25-40" for France, "¥2000-3000" for Japan)
- link: Full URL to the restaurant page
- source: Review website source (e.g., 'Tabelog', 'Yelp', 'TripAdvisor')

CRITICAL RULES:
1. ALWAYS identify and include the source website name
2. Convert ratings to numerical format (e.g., "3.54" → 3.54)
3. Provide reasonable budget estimates if not explicitly stated
4. Ensure all URLs are valid and complete
5. Focus on currently open, well-reviewed restaurants
6. Extract at least 5-10 restaurants from the results
7. For Japan: ALWAYS use tavily_extract with the provided Tabelog URL
8. For other countries: Use tavily_search with BOTH query AND include_domains parameters
   - Use the currency symbol provided in the query instructions for ALL price ranges
9. tavily_extract only accepts {"urls": ["url"]} - no query parameter
10. Parse the returned markdown content to extract restaurant data

Return the results in the specified RestaurantOutput format with a list of Restaurant objects.""",
                output_cls=RestaurantOutput,
            )
            
            self._initialized = True
            
        except Exception as e:
            raise Exception(f"Failed to initialize MCP agent: {e}")
    
    async def scrape_restaurants(self, query: str, stream: bool = False, price_range: Optional[str] = None) -> RestaurantOutput:
        """Search and extract restaurant information using the MCP agent."""
        if not self._initialized:
            await self.initialize()
        
        # Detect country from query
        country = detect_country_from_query(query)
        if country:
            logger.info(f"Detected country: {country}")
        
        # Handle Japan queries with Tabelog URL construction and tavily_extract
        if country == "japan":
            return await self._handle_japan_query(query, price_range, stream)
        
        # Handle other countries with existing tavily_search logic
        return await self._handle_other_countries_query(query, price_range, stream, country)
    
    async def _handle_japan_query(self, query: str, price_range: Optional[str], stream: bool) -> RestaurantOutput:
        """Handle Japan-specific queries using Tabelog URL construction and tavily_extract."""
        
        # Extract location from query
        area = extract_japan_location(query)
        
        # Prioritize API price_range parameter over query text budget detection
        budget_info = None
        if price_range and price_range in TABELOG_BUDGET_MAPPING:
            budget_info = TABELOG_BUDGET_MAPPING[price_range]
            logger.info(f"Using API price_range parameter: {price_range}")
        else:
            # Fall back to extracting budget from query text
            budget_info = extract_japan_budget(query)
            if budget_info:
                logger.info(f"Extracted budget from query text")
        
        # Build Tabelog URL with proper budget parameters
        tabelog_url = build_tabelog_url(area, budget_info)
        budget_description = budget_info["description"] if budget_info else "All price ranges"
        
        logger.info(f"Japan query - Area: {area}, Budget: {budget_description}")
        logger.info(f"Constructed Tabelog URL: {tabelog_url}")
        
        # No extraction query needed - tavily_extract only accepts URLs
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                if stream:
                    handler = self.agent.run(f"Extract restaurant information from this Tabelog page: {tabelog_url}. The page is already sorted by rating, so focus on the first 10 restaurants listed.")
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
                    if hasattr(result, 'structured_response'):
                        return result.structured_response
                    if hasattr(result, 'response') and hasattr(result.response, 'structured_output'):
                        return result.response.structured_output
                    logger.warning(f"Unexpected result structure: {type(result)}")
                    return RestaurantOutput(restaurants=[])
                else:
                    response = await self.agent.run(f"Extract restaurant information from this Tabelog page: {tabelog_url}. The page is already sorted by rating, so focus on the first 10 restaurants listed.")
                    if hasattr(response, 'structured_response'):
                        return response.structured_response
                    if hasattr(response, 'response') and hasattr(response.response, 'structured_output'):
                        return response.response.structured_output
                    logger.warning(f"Unexpected response structure: {type(response)}")
                    return RestaurantOutput(restaurants=[])
            except Exception as e:
                logger.error(f"Error in Japan query (attempt {attempt + 1}/{max_retries}): {e}")
                
                if "Expecting property name enclosed in double quotes" in str(e) and attempt < max_retries - 1:
                    logger.info("JSON parsing error detected, resetting Tavily MCP client and reinitializing agent...")
                    mcp_manager.reset_tavily()
                    self._initialized = False
                    await self.initialize()
                    continue
                
                if attempt == max_retries - 1:
                    logger.error(f"All retries failed for Japan query")
                    return RestaurantOutput(restaurants=[])
    
    async def _handle_other_countries_query(self, query: str, price_range: Optional[str], stream: bool, country: Optional[str]) -> RestaurantOutput:
        """Handle non-Japan queries using tavily_search with proper city and domain filtering."""
        # Extract city from query
        city = extract_city_from_query(query, country)
        
        if not city:
            logger.warning(f"No city detected in query: {query}")
            # Fallback to generic search
            city = None
        else:
            logger.info(f"Detected city: {city} for country: {country}")
        
        # Build search query with city and country-specific domains
        search_params = build_international_search_query(query, city, country, price_range)
        
        # Get currency for the country
        currency = get_country_currency(country) if country else "$"
        
        logger.info(f"Search parameters for {country or 'unknown country'}: {search_params}")
        logger.info(f"Currency for {country}: {currency}")
        
        # Format domains for tavily_search (remove https://)
        clean_domains = [domain.replace('https://', '').replace('http://', '') for domain in search_params['include_domains']]
        
        agent_query = f"""Search for restaurants using these exact parameters:
query: "{search_params['query']}"
include_domains: {clean_domains}

Use tavily_search with both the query and include_domains parameters as shown above.
Do NOT add a 'country' parameter.
Extract the top 10 restaurants from the search results.
IMPORTANT: Express all price ranges using the currency symbol "{currency}" (e.g., lunch: "{currency}15-25", dinner: "{currency}30-50").
Make sure to include the city "{city or 'San Francisco'}" in the location field for each restaurant."""
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                if stream:
                    handler = self.agent.run(agent_query)
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
                    if hasattr(result, 'structured_response'):
                        return result.structured_response
                    if hasattr(result, 'response') and hasattr(result.response, 'structured_output'):
                        return result.response.structured_output
                    logger.warning(f"Unexpected result structure: {type(result)}")
                    return RestaurantOutput(restaurants=[])
                else:
                    response = await self.agent.run(agent_query)
                    if hasattr(response, 'structured_response'):
                        return response.structured_response
                    if hasattr(response, 'response') and hasattr(response.response, 'structured_output'):
                        return response.response.structured_output
                    logger.warning(f"Unexpected response structure: {type(response)}")
                    return RestaurantOutput(restaurants=[])
            except Exception as e:
                logger.error(f"Error in other countries query (attempt {attempt + 1}/{max_retries}): {e}")
                
                if "Expecting property name enclosed in double quotes" in str(e) and attempt < max_retries - 1:
                    logger.info("JSON parsing error detected, resetting Tavily MCP client and reinitializing agent...")
                    mcp_manager.reset_tavily()
                    self._initialized = False
                    await self.initialize()
                    continue
                
                if attempt == max_retries - 1:
                    logger.error(f"All retries failed for other countries query")
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

# Global restaurant agent instance to avoid multiple initializations
_global_restaurant_agent = None

async def get_global_restaurant_agent() -> RestaurantAgent:
    """Get or create the global restaurant agent instance."""
    global _global_restaurant_agent
    if _global_restaurant_agent is None:
        _global_restaurant_agent = RestaurantAgent()
        await _global_restaurant_agent.initialize()
    return _global_restaurant_agent

async def call_restaurant_agent(ctx: Context, query: str) -> str:
    """Useful for recording research notes based on a specific prompt."""
    agent = await get_global_restaurant_agent()
    
    result = await agent.scrape_restaurants(query=query)

    async with ctx.store.edit_state() as ctx_state:
        ctx_state["state"]["restaurants"] = result
    return result


# Convenience function for backward compatibility
async def search_restaurants(query: str = "What are the top rated restaurants in Tokyo") -> RestaurantOutput:
    """Legacy function for backward compatibility."""
    try:
        agent = await get_global_restaurant_agent()
        return await agent.scrape_restaurants(query)
    except Exception as e:
        logger.error(f"Error in search_restaurants: {e}")
        return RestaurantOutput(restaurants=[])
