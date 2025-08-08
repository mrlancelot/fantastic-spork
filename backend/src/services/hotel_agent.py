import os
from llama_index.core.agent.workflow import ReActAgent
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.tools.mcp import BasicMCPClient
from llama_index.tools.mcp.base import McpToolSpec
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from llama_index.core.agent.workflow import AgentStream, AgentOutput, ToolCallResult, ToolCall
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Hotel(BaseModel):
    name: str = Field(description="Name of the hotel")
    brand: str = Field(description="Hotel brand/chain (e.g., Marriott, Hilton)")
    address: str = Field(description="Complete hotel address")
    city: str = Field(description="City where the hotel is located")
    neighborhood: str = Field(description="Neighborhood or district")
    star_rating: str = Field(description="Hotel star rating (1-5 stars)")
    guest_rating: str = Field(description="Guest review rating (e.g., 4.2/5)")
    review_count: str = Field(description="Number of reviews")
    price_per_night: str = Field(description="Price per night with currency")
    total_price: str = Field(description="Total price for the stay")
    amenities: List[str] = Field(description="List of hotel amenities")
    room_type: str = Field(description="Type of room (Standard, Deluxe, Suite, etc.)")
    check_in_time: str = Field(description="Check-in time")
    check_out_time: str = Field(description="Check-out time")
    cancellation_policy: str = Field(description="Cancellation policy")
    booking_url: str = Field(description="Direct URL to book this hotel")
    hotel_website: str = Field(description="Official hotel website")
    phone_number: str = Field(description="Hotel phone number")
    image_urls: List[str] = Field(description="List of hotel image URLs")

class HotelSearchOutput(BaseModel):
    hotels: List[Hotel] = Field(description="List of available hotels")
    search_query: str = Field(description="The search query used")
    total_results: int = Field(description="Total number of hotels found")

class HotelAgent:
    """Agent for hotel search using MCP (Model Context Protocol) tools."""
    
    def __init__(self, api_token: str = None):
        """Initialize the MCP hotel agent with API token."""
        self.api_token = api_token or os.getenv("BRIGHT_DATA_API_TOKEN")
        if not self.api_token:
            raise ValueError("BRIGHT_DATA_API_TOKEN is required")
        
        self.agent = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize the MCP client and agent."""
        if self._initialized:
            return
            
        try:
            # Create MCP client
            http_client = BasicMCPClient(f"https://mcp.brightdata.com/sse?token={self.api_token}&unlocker=mcp_unlocker")
            
            # Create MCP tool specification
            mcp_tool_spec = McpToolSpec(
                client=http_client,
                allowed_tools=["search_engine"],
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
                    timeout=30.0,
                    request_timeout=30.0
                )
                logger.info("Google GenAI LLM initialized successfully for hotel agent")
            except Exception as llm_error:
                logger.error(f"Failed to initialize Google GenAI LLM for hotel agent: {llm_error}")
                raise Exception(f"LLM initialization failed: {llm_error}")
            
            self.agent = ReActAgent(
                tools=tools,
                name="hotel_search_agent",
                description="Extracts hotel booking information from webpages",
                llm=llm,
                system_prompt="""You are a hotel search expert with comprehensive web scraping capabilities. Your tools include:

search_engine: Get search results from Google
Structured extractors: Fast, reliable data from major platforms
Browser automation: Navigate, click, type, screenshot for complex interactions

Your goal is to find the best hotel options by:
1. Searching major hotel booking sites (Booking.com, Hotels.com, Expedia, Agoda, Trivago)
2. Using search_engine to find relevant hotel booking pages
3. Extracting comprehensive hotel information including:
    - Hotel names and descriptions
    - Exact location details
    - Star ratings and guest review scores
    - Nightly rates and total costs with currency
    - Complete amenities lists
    - Hotel images/logos
    - Direct booking URLs

IMPORTANT:
- Always provide accurate, real hotel data with current pricing
- Try multiple sites if needed for comprehensive results
- Focus on finding at least 3-5 different hotel options with varying price points, locations, and amenities
- NEVER RETURN EMPTY RESULTS - always return at least 2-3 hotels if available
- Prioritize hotels with good ratings, reasonable prices, and desirable locations
- Include direct booking URLs for each hotel
- Focus on hotels that are currently available for the specified dates

You MUST return your response in the exact JSON format with a 'hotels' field containing a list of hotel objects.""",
                output_cls=HotelSearchOutput,
            )
            
            self._initialized = True
            
        except Exception as e:
            raise Exception(f"Failed to initialize MCP agent: {e}")
    
    async def search_hotels(self, 
                           city: str, 
                           check_in_date: str, 
                           check_out_date: str,
                           guests: int = 2,
                           rooms: int = 1,
                           price_range: str = "any") -> HotelSearchOutput:
        """Search for hotels in a specific city."""
        if not self._initialized:
            await self.initialize()
        
        query = f"Find hotels in {city} for check-in {check_in_date} and check-out {check_out_date}"
        query += f" for {guests} guest(s) in {rooms} room(s)"
        if price_range != "any":
            query += f" in {price_range} price range"
        
        try:
            handler = self.agent.run(query)
            response = await handler
            return response.structured_response
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error in searching hotels: {error_msg}")
            
            # Check for specific JSON parsing errors
            if "Expecting property name enclosed in double quotes" in error_msg:
                logger.error("JSON parsing error detected - likely malformed API response from Google GenAI")
                # Try to reinitialize the agent and retry once
                try:
                    self._initialized = False
                    await self.initialize()
                    handler = self.agent.run(query)
                    response = await handler
                    return response.structured_response
                except Exception as retry_error:
                    logger.error(f"Retry also failed: {retry_error}")
            
            # Return empty result with error information
            return HotelSearchOutput(
                hotels=[],
                search_query=query,
                total_results=0
            )
    
    async def search_budget_hotels(self, 
                                  city: str, 
                                  check_in_date: str, 
                                  check_out_date: str,
                                  guests: int = 2) -> HotelSearchOutput:
        """Search for budget-friendly hotels in a specific city."""
        if not self._initialized:
            await self.initialize()
        
        try:
            query = f"Find the cheapest budget hotels in {city} for check-in {check_in_date} and check-out {check_out_date} for {guests} guest(s). Focus on hostels, budget hotels, and best deals under $100 per night."
            response = await self.agent.run(query)
            return response.structured_response
        except Exception as e:
            logger.error(f"Error in searching budget hotels: {e}")
            return HotelSearchOutput(
                hotels=[],
                search_query=query,
                total_results=0
            )
    
    async def search_luxury_hotels(self, 
                                  city: str, 
                                  check_in_date: str, 
                                  check_out_date: str,
                                  guests: int = 2) -> HotelSearchOutput:
        """Search for luxury hotels in a specific city."""
        if not self._initialized:
            await self.initialize()
        
        try:
            query = f"Find luxury 4-5 star hotels in {city} for check-in {check_in_date} and check-out {check_out_date} for {guests} guest(s). Focus on premium hotels with excellent amenities, spas, fine dining, and top ratings."
            response = await self.agent.run(query)
            return response.structured_response
        except Exception as e:
            logger.error(f"Error in searching luxury hotels: {e}")
            return HotelSearchOutput(
                hotels=[],
                search_query=query,
                total_results=0
            )
    
    async def run_custom_query(self, query: str) -> HotelSearchOutput:
        """Run a custom hotel search query."""
        if not self._initialized:
            await self.initialize()
        
        try:
            response = await self.agent.run(query)
            return response.structured_response
        except Exception as e:
            logger.error(f"Error in running custom query: {e}")
            return HotelSearchOutput(
                hotels=[],
                search_query=query,
                total_results=0
            )


# Convenience functions
async def search_hotels(city: str, 
                       check_in_date: str, 
                       check_out_date: str,
                       guests: int = 2,
                       rooms: int = 1,
                       price_range: str = "any") -> HotelSearchOutput:
    """Convenience function to search hotels."""
    try:
        agent = HotelAgent()
        return await agent.search_hotels(city, check_in_date, check_out_date, guests, rooms, price_range)
    except Exception as e:
        logger.error(f"Error in search_hotels: {e}")
        raise

async def search_budget_hotels(city: str, 
                              check_in_date: str, 
                              check_out_date: str,
                              guests: int = 2) -> HotelSearchOutput:
    """Convenience function to search for budget hotels."""
    try:
        agent = HotelAgent()
        return await agent.search_budget_hotels(city, check_in_date, check_out_date, guests)
    except Exception as e:
        logger.error(f"Error in search_budget_hotels: {e}")
        raise

async def search_luxury_hotels(city: str, 
                              check_in_date: str, 
                              check_out_date: str,
                              guests: int = 2) -> HotelSearchOutput:
    """Convenience function to search for luxury hotels."""
    try:
        agent = HotelAgent()
        return await agent.search_luxury_hotels(city, check_in_date, check_out_date, guests)
    except Exception as e:
        logger.error(f"Error in search_luxury_hotels: {e}")
        raise
