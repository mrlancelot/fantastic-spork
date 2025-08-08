"""Master Travel Agent with GLM-4.5 and Web Search Integration"""

import os
import sys
import json
import asyncio
import logging
from typing import Optional, List, Dict, Any, AsyncGenerator
from datetime import datetime, timedelta
from pathlib import Path
from pydantic import BaseModel, Field
import aiohttp
from enum import Enum

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
logger.debug(f"Added to sys.path: {Path(__file__).parent.parent}")
logger.debug(f"Current working directory: {os.getcwd()}")

class AgentAction(str, Enum):
    THINKING = "thinking"
    SEARCHING = "searching"
    ANALYZING = "analyzing"
    CALLING_SERVICE = "calling_service"
    COMPLETE = "complete"
    ERROR = "error"

class AgentThought(BaseModel):
    action: AgentAction
    content: str
    service: Optional[str] = None
    data: Optional[Dict] = None

class TripRequest(BaseModel):
    destination: str
    start_date: str
    end_date: str
    origin: str = "New York"
    budget: Optional[float] = 5000
    travelers: int = 1
    interests: List[str] = ["food", "culture"]
    preferences: Optional[Dict] = {}

class WebSearchTool:
    """Web search using Tavily API"""
    
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        self.base_url = "https://api.tavily.com/search"
        logger.debug(f"WebSearchTool initialized. API key present: {bool(self.api_key)}")
        
    async def search(self, query: str, search_depth: str = "advanced") -> Dict:
        """Search web for travel information"""
        logger.debug(f"Web search for: {query}")
        if not self.api_key:
            logger.warning("Tavily API key not set, returning empty results")
            return {"results": [], "answer": "Web search unavailable"}
            
        headers = {"Content-Type": "application/json"}
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": search_depth,
            "include_answer": True,
            "include_raw_content": False,
            "max_results": 5
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=headers, json=payload, timeout=30) as response:
                    if response.status == 200:
                        return await response.json()
                    return {"results": [], "answer": "Search failed"}
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return {"results": [], "answer": str(e)}

class MasterTravelAgent:
    """Intelligent travel planning agent with GLM-4.5 and service integration"""
    
    def __init__(self):
        logger.info("Initializing MasterTravelAgent...")
        
        # Log environment variables status
        env_vars = {
            "OPENROUTER_API_KEY": bool(os.getenv("OPENROUTER_API_KEY")),
            "TAVILY_API_KEY": bool(os.getenv("TAVILY_API_KEY")),
            "AMADEUS_API_KEY": bool(os.getenv("AMADEUS_API_KEY")),
            "AMADEUS_Secret": bool(os.getenv("AMADEUS_Secret")),
            "BRIGHT_DATA_API_TOKEN": bool(os.getenv("BRIGHT_DATA_API_TOKEN")),
            "GOOGLE_API_KEY": bool(os.getenv("GOOGLE_API_KEY"))
        }
        logger.debug(f"Environment variables status: {env_vars}")
        
        # Initialize services (lazy loading)
        self.flight_service = None
        self.hotel_agent = None
        self.restaurant_agent = None
        self.hotel_service = None
        self.activity_service = None
        self.market_insights = None
        self.web_search = WebSearchTool()
        
        # OpenRouter for GLM-4.5
        self.llm_api_key = os.getenv("OPENROUTER_API_KEY")
        self.llm_base_url = "https://openrouter.ai/api/v1/chat/completions"
        logger.info(f"Agent initialized. LLM configured: {bool(self.llm_api_key)}")
        
    async def _init_services(self):
        """Lazy initialize services to avoid import errors"""
        logger.debug("Starting service initialization...")
        
        # Initialize day planner
        if not hasattr(self, 'day_planner'):
            try:
                from .day_planner_agent import DayPlannerAgent
                self.day_planner = DayPlannerAgent()
                logger.info("Day planner initialized successfully")
            except Exception as e:
                logger.error(f"Could not initialize day planner: {e}")
                self.day_planner = None
        
        if not self.flight_service:
            logger.debug("Initializing flight service...")
            try:
                # Direct import from services directory
                from services.flights import AmadeusFlightService, FlightSearchRequest
                self.flight_service = AmadeusFlightService()
                self.FlightSearchRequest = FlightSearchRequest
                logger.info("Flight service initialized successfully")
            except ImportError as e:
                logger.error(f"Import error for flight service: {e}")
                logger.debug(f"sys.path: {sys.path}")
            except Exception as e:
                logger.error(f"Could not initialize flight service: {e}", exc_info=True)
                
        if not self.hotel_agent:
            logger.debug("Initializing hotel agent...")
            try:
                from services.hotel_agent import HotelAgent
                self.hotel_agent = HotelAgent()
                logger.info("Hotel agent initialized successfully")
            except ImportError as e:
                logger.error(f"Import error for hotel agent: {e}")
            except Exception as e:
                logger.error(f"Could not initialize hotel agent: {e}", exc_info=True)
                
        if not self.restaurant_agent:
            logger.debug("Initializing restaurant agent...")
            try:
                from services.restaurant_agent import RestaurantAgent
                self.restaurant_agent = RestaurantAgent()
                logger.info("Restaurant agent initialized successfully")
            except ImportError as e:
                logger.error(f"Import error for restaurant agent: {e}")
            except Exception as e:
                logger.error(f"Could not initialize restaurant agent: {e}", exc_info=True)
    
    async def _think_with_glm(self, context: str, thinking_mode: bool = True) -> str:
        """Use GLM-4.5 for reasoning with thinking mode"""
        if not self.llm_api_key:
            logger.warning("OpenRouter API key not set")
            return "I need to analyze this request but API key is not configured."
        
        logger.debug(f"Calling GLM-4.5 with thinking_mode={thinking_mode}")
            
        headers = {
            "Authorization": f"Bearer {self.llm_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "TravelAI Agent"
        }
        
        # Use GLM-4.5 with thinking mode
        data = {
            "model": "z-ai/glm-4.5",
            "messages": [
                {
                    "role": "system",
                    "content": """You are a master travel planning agent. You have access to:
                    1. Flight search (Amadeus API)
                    2. Hotel search (MCP agents)
                    3. Restaurant search (Tavily MCP)
                    4. Activity search
                    5. Web search for real-time info
                    
                    Be concise, professional, and actionable. No emojis.
                    Focus on practical recommendations with costs."""
                },
                {"role": "user", "content": context}
            ],
            "temperature": 0.3,
            "max_tokens": 2000,
            "stream": False,
            "reasoning": {
                "enabled": thinking_mode,
                "effort": "high" if thinking_mode else "low"
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.llm_base_url, headers=headers, json=data, timeout=60) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result['choices'][0]['message']['content']
                        # Extract reasoning if present
                        if '<think>' in content and '</think>' in content:
                            # Remove thinking tags for clean output
                            content = content.replace('<think>', '').replace('</think>', '')
                        return content
                    else:
                        error_text = await response.text()
                        logger.error(f"LLM API error: {response.status} - {error_text}")
                        return "Unable to process request"
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return f"Analysis error: {str(e)}"
    
    async def search_flights(self, origin: str, destination: str, 
                            departure_date: str, return_date: Optional[str] = None) -> Dict:
        """Search flights using existing service"""
        logger.info(f"Searching flights: {origin} -> {destination} on {departure_date}")
        await self._init_services()
        
        if not self.flight_service:
            logger.warning("Flight service not available after initialization")
            return {"error": "Flight service not available", "outbound_flights": [], "return_flights": []}
            
        try:
            request = self.FlightSearchRequest(
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                return_date=return_date,
                adults=1
            )
            response = await self.flight_service.search(request)
            return response.dict()
        except Exception as e:
            logger.error(f"Flight search error: {e}")
            return {"error": str(e), "outbound_flights": [], "return_flights": []}
    
    async def search_hotels(self, city: str, check_in: str, check_out: str) -> Dict:
        """Search hotels using MCP agent"""
        await self._init_services()
        
        if not self.hotel_agent:
            return {"error": "Hotel service not available", "hotels": []}
            
        try:
            await self.hotel_agent.initialize()
            response = await self.hotel_agent.search_hotels(
                city=city,
                check_in_date=check_in,
                check_out_date=check_out,
                guests=2
            )
            return response.dict()
        except Exception as e:
            logger.error(f"Hotel search error: {e}")
            return {"error": str(e), "hotels": []}
    
    async def search_restaurants(self, query: str) -> Dict:
        """Search restaurants using MCP agent"""
        await self._init_services()
        
        if not self.restaurant_agent:
            return {"error": "Restaurant service not available", "restaurants": []}
            
        try:
            await self.restaurant_agent.initialize()
            response = await self.restaurant_agent.scrape_restaurants(
                query=f"Find the best restaurants in {query}"
            )
            return response.dict()
        except Exception as e:
            logger.error(f"Restaurant search error: {e}")
            return {"error": str(e), "restaurants": []}
    
    async def search_web_for_context(self, query: str) -> Dict:
        """Search web for additional context"""
        return await self.web_search.search(query)
    
    async def plan_trip_stream(self, request: TripRequest) -> AsyncGenerator[AgentThought, None]:
        """Stream the agent's thinking and actions"""
        logger.info(f"Starting trip planning for {request.destination}")
        logger.debug(f"Request details: {request.dict()}")
        
        # Step 1: Initial thinking
        yield AgentThought(
            action=AgentAction.THINKING,
            content=f"Planning trip to {request.destination} from {request.start_date} to {request.end_date} with budget ${request.budget}"
        )
        
        # Step 2: Use GLM-4.5 to analyze the request
        analysis_prompt = f"""
        Analyze this travel request:
        - Destination: {request.destination}
        - Dates: {request.start_date} to {request.end_date}
        - Budget: ${request.budget}
        - Travelers: {request.travelers}
        - Interests: {', '.join(request.interests)}
        
        What are the key things to research for this trip?
        List 3 specific things to search for.
        """
        
        analysis = await self._think_with_glm(analysis_prompt, thinking_mode=True)
        
        yield AgentThought(
            action=AgentAction.THINKING,
            content=f"Analysis: {analysis[:300]}..."
        )
        
        # Step 3: Web search for context
        yield AgentThought(
            action=AgentAction.SEARCHING,
            content=f"Searching for current information about {request.destination}",
            service="web_search"
        )
        
        web_context = await self.search_web_for_context(
            f"{request.destination} travel guide {request.start_date} events weather tips safety"
        )
        
        if web_context.get('answer'):
            yield AgentThought(
                action=AgentAction.ANALYZING,
                content=f"Found travel context: {web_context.get('answer', '')[:300]}..."
            )
        
        # Step 4: Search flights
        yield AgentThought(
            action=AgentAction.CALLING_SERVICE,
            content=f"Searching flights from {request.origin} to {request.destination}",
            service="flight_service"
        )
        
        flights = await self.search_flights(
            request.origin, 
            request.destination, 
            request.start_date, 
            request.end_date
        )
        
        flight_summary = {
            "found": len(flights.get('outbound_flights', [])),
            "cheapest": None,
            "best": []
        }
        
        if flights.get('outbound_flights'):
            outbound = flights['outbound_flights']
            flight_summary['cheapest'] = outbound[0].get('price', 'N/A')
            flight_summary['best'] = outbound[:3]
            
            yield AgentThought(
                action=AgentAction.ANALYZING,
                content=f"Found {len(outbound)} flights. Cheapest: {flight_summary['cheapest']}",
                data={"flights": flight_summary['best']}
            )
        
        # Step 5: Search hotels
        yield AgentThought(
            action=AgentAction.CALLING_SERVICE,
            content=f"Searching hotels in {request.destination}",
            service="hotel_service"
        )
        
        hotels = await self.search_hotels(
            request.destination, 
            request.start_date, 
            request.end_date
        )
        
        hotel_summary = {
            "found": len(hotels.get('hotels', [])),
            "best": hotels.get('hotels', [])[:3]
        }
        
        if hotel_summary['best']:
            yield AgentThought(
                action=AgentAction.ANALYZING,
                content=f"Found {hotel_summary['found']} hotels in {request.destination}",
                data={"hotels": hotel_summary['best']}
            )
        
        # Step 6: Search restaurants
        yield AgentThought(
            action=AgentAction.CALLING_SERVICE,
            content=f"Finding restaurants in {request.destination}",
            service="restaurant_service"
        )
        
        restaurants = await self.search_restaurants(request.destination)
        
        restaurant_summary = {
            "found": len(restaurants.get('restaurants', [])),
            "best": restaurants.get('restaurants', [])[:3]
        }
        
        if restaurant_summary['best']:
            yield AgentThought(
                action=AgentAction.ANALYZING,
                content=f"Found {restaurant_summary['found']} top-rated restaurants",
                data={"restaurants": restaurant_summary['best']}
            )
        
        # Step 7: Search for activities based on interests
        for interest in request.interests[:2]:  # Limit to 2 interests
            yield AgentThought(
                action=AgentAction.SEARCHING,
                content=f"Searching for {interest} activities in {request.destination}",
                service="web_search"
            )
            
            activities = await self.search_web_for_context(
                f"{request.destination} best {interest} activities attractions must-see"
            )
            
            if activities.get('answer'):
                yield AgentThought(
                    action=AgentAction.ANALYZING,
                    content=f"Found {interest} recommendations",
                    data={"activity_type": interest, "info": activities.get('answer', '')[:300]}
                )
        
        # Step 8: Final comprehensive analysis
        yield AgentThought(
            action=AgentAction.THINKING,
            content="Creating optimized itinerary with all findings..."
        )
        
        # Use GLM-4.5 to create final recommendations
        final_context = f"""
        Create a concise, actionable travel plan for {request.destination} from {request.start_date} to {request.end_date}.
        
        Budget: ${request.budget}
        Travelers: {request.travelers}
        
        Found:
        - {flight_summary['found']} flights (cheapest: {flight_summary['cheapest']})
        - {hotel_summary['found']} hotels
        - {restaurant_summary['found']} restaurants
        
        Web search context: {web_context.get('answer', 'No additional context')[:500]}
        
        Interests: {', '.join(request.interests)}
        
        Provide:
        1. Top 3 recommendations for flights, hotels, restaurants
        2. Estimated total cost breakdown
        3. 3-5 specific activities based on their interests
        4. Any important travel tips from the web search
        
        Be specific with prices and practical details. No emojis.
        """
        
        final_plan = await self._think_with_glm(final_context, thinking_mode=True)
        
        yield AgentThought(
            action=AgentAction.COMPLETE,
            content=final_plan,
            data={
                "summary": {
                    "flights": flight_summary,
                    "hotels": hotel_summary,
                    "restaurants": restaurant_summary,
                    "total_options": {
                        "flights": flight_summary['found'],
                        "hotels": hotel_summary['found'],
                        "restaurants": restaurant_summary['found']
                    }
                }
            }
        )
    
    async def quick_search(self, query: str) -> str:
        """Quick search for simple queries"""
        # First do a web search
        web_results = await self.search_web_for_context(query)
        
        # Then use GLM-4.5 to process
        context = f"""
        User query: {query}
        Web search results: {web_results.get('answer', '')}
        
        Provide a helpful, concise response. Be specific and actionable.
        No emojis or fluff.
        """
        
        return await self._think_with_glm(context, thinking_mode=False)

# Convenience function for API endpoint
async def process_travel_request(request: TripRequest) -> AsyncGenerator[str, None]:
    """Process travel request with streaming response"""
    agent = MasterTravelAgent()
    
    async for thought in agent.plan_trip_stream(request):
        # Format for SSE streaming
        yield f"data: {json.dumps(thought.dict())}\n\n"