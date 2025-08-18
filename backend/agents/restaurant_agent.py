import os
from unittest import result
from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.workflow import Context
from pydantic import BaseModel, Field
from typing import List, Optional
from llama_index.core.agent.workflow import AgentStream, AgentOutput, ToolCallResult, ToolCall
import logging
from utils.llm_manager import get_powerful_llm


from constants import (
    detect_country_from_query, 
    get_country_specific_sites, 
    build_country_aware_search_query,
)


from utils.mcp_client_manager import mcp_manager

from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Restaurant(BaseModel):
    name: str = Field(description="the name of the restaurant")
    cuisine: str = Field(description="the cuisine of the restaurant")
    rating: Optional[float] = Field(default=None, description="the rating of the restaurant (optional)")
    location: str = Field(description="the location of the restaurant")
    lunch_budget: Optional[str] = Field(default=None, description="the lunch budget of the restaurant (optional)")
    dinner_budget: Optional[str] = Field(default=None, description="the dinner budget of the restaurant (optional)")
    link: Optional[str] = Field(default=None, description="the link to the restaurant (optional)")
    source: str = Field(description="the review website source from tavily_search")

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

            tools = await mcp_manager.get_tavily_tools(self.api_token)

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
                system_prompt="""You are a restaurant search expert. You MUST follow this process:

STEP 1: SEARCH FOR TOP RESTAURANTS (SINGLE TAVILY_SEARCH CALL)
Make ONE "tavily_search" call to find top restaurants in the specified location with the given budget.

STEP 2: EXTRACT DETAILS IF NEEDED (SINGLE TAVILY_EXTRACT CALL)
If tavily_search doesn't provide sufficient restaurant details, use ONE "tavily_extract" call with ALL URLs from search results to get complete webpage content.

MANDATORY WORKFLOW (MAXIMUM 2 TAVILY CALLS TOTAL):
1. Make ONE tavily_search call with the provided query
2. If search results have sufficient restaurant details, extract directly from search results
3. If not, make ONE tavily_extract call with ALL URLs from search results (batch extraction)
4. Verify reviews exist on country-specific review sites when possible (use constants from query context)
5. Compile all restaurants into the final JSON response

For each restaurant, extract these key fields:
- name: Restaurant name
- cuisine: Type of cuisine (e.g., "Japanese", "Italian", "French")  
- rating: Numerical rating (convert "5 stars" → 5.0, "4.5/5" → 4.5)
- location: Full address or area/neighborhood
- lunch_budget: Estimated lunch cost per person (e.g., "$15-25", "¥1000-2000")
- dinner_budget: Estimated dinner cost per person (e.g., "$30-50", "¥3000-5000")
- link: Direct URL to restaurant page or booking site
- source: Review website source from tavily_search

CRITICAL RULES:
- Make ONLY ONE tavily_search call first
- Only use tavily_extract if search results lack sufficient detail
- If using tavily_extract, batch ALL URLs together in ONE call
- Focus on currently open, well-reviewed restaurants (4.0+ stars)
- Prioritize results from country-specific review sites based on the detected country
- For Japan: Tabelog, Reddit, YouTube
- For USA: Yelp, OpenTable, TripAdvisor, Zagat
- For UK: TripAdvisor UK, OpenTable UK, Time Out, Square Meal
- For other countries: Use appropriate country-specific sites from the query context
- Provide reasonable budget estimates when exact prices aren't available
- Return 5-10 top restaurants from the results

You MUST return your response in the exact JSON format with a 'restaurants' field containing a list of restaurant objects.""",
                output_cls=RestaurantOutput,
            )
            self._initialized = True
        except Exception as e:
            raise Exception(f"Failed to initialize MCP agent: {e}")
    async def scrape_restaurants(self, query: str, stream: bool = False, price_range: Optional[str] = None) -> RestaurantOutput:
        """Search and extract restaurant information using the MCP agent."""
        if not self._initialized:
            await self.initialize()

        country = detect_country_from_query(query)
        if country:
            logger.info(f"Detected country: {country}")

        country_specific_sites = get_country_specific_sites(country)

        enhanced_query = build_country_aware_search_query(query, country_specific_sites, price_range)
        logger.info(f"Enhanced query: {enhanced_query}")
        max_retries = 2
        for attempt in range(max_retries):
            try:
                if stream:
                    handler = self.agent.run(enhanced_query)
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
                    response = await self.agent.run(enhanced_query)

                    if hasattr(response, 'structured_response'):
                        return response.structured_response

                    if hasattr(response, 'response') and hasattr(response.response, 'structured_output'):
                        return response.response.structured_output

                    logger.warning(f"Unexpected response structure: {type(response)}")
                    return RestaurantOutput(restaurants=[])
            except Exception as e:
                logger.error(f"Error in scrape_restaurants (attempt {attempt + 1}/{max_retries}): {e}")

                if "Expecting property name enclosed in double quotes" in str(e) and attempt < max_retries - 1:
                    logger.info("JSON parsing error detected, resetting Tavily MCP client and reinitializing agent...")

                    mcp_manager.reset_tavily()
                    self._initialized = False
                    await self.initialize()
                    continue

                if attempt == max_retries - 1:
                    logger.error(f"All retries failed for scrape_restaurants")
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

        if "job_id" in ctx_state:
            from utils.job_manager import get_job_manager
            job_manager = get_job_manager()

            flights_data = ctx_state.get("state", {}).get("flights", {})
            hotels_data = ctx_state.get("state", {}).get("hotels", {})
            flights_count = len(flights_data.get("flights", []))
            hotels_count = len(hotels_data.get("hotels", []))

            restaurants_count = 0
            if isinstance(result, str):
                try:
                    import json
                    result_dict = json.loads(result)
                    if "restaurants" in result_dict:
                        restaurants_count = len(result_dict["restaurants"])
                except:
                    pass
            elif isinstance(result, dict) and "restaurants" in result:
                restaurants_count = len(result["restaurants"])
            progress = {
                "message": f"Found {restaurants_count} restaurant recommendations",
                "step": "restaurants",
                "details": {
                    "flights_found": flights_count,
                    "hotels_found": hotels_count,
                    "restaurants_found": restaurants_count,
                    "activities_planned": 0,
                    "price_ranges": {}
                }
            }

            if flights_data.get("best_price"):
                progress["details"]["price_ranges"]["flights"] = {
                    "min": flights_data.get("best_price"),
                    "max": max([f.get("price", 0) for f in flights_data.get("flights", [])], default=0)
                }
            if hotels_data.get("best_price"):
                progress["details"]["price_ranges"]["hotels"] = {
                    "min": hotels_data.get("best_price"),
                    "max": max([h.get("price", 0) for h in hotels_data.get("hotels", [])], default=0)
                }
            job_manager.update_job_progress(ctx_state["job_id"], progress)
    return result



async def search_restaurants(query: str = "What are the top rated restaurants in Tokyo") -> RestaurantOutput:
    """Legacy function for backward compatibility."""
    try:
        agent = await get_global_restaurant_agent()
        return await agent.scrape_restaurants(query)
    except Exception as e:
        logger.error(f"Error in search_restaurants: {e}")
        return RestaurantOutput(restaurants=[])
