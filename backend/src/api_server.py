"""
TravelAI Backend API - Enhanced with Smart Scrapers
Modular implementation using web scrapers for flights/hotels and Tavily for restaurants
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any, AsyncGenerator

from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import google.generativeai as genai

# Add src to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import our enhanced services and logging
from core.logger import setup_logger, log_startup, log_shutdown
from core.config import get_settings
from services.flight_service import FlightService
from services.hotel_service import HotelService
from services.restaurant_service import RestaurantService

# Initialize logger
logger = setup_logger("TravelAI-API")
settings = get_settings()

# Load environment - check multiple locations
env_locations = [
    Path(__file__).parent.parent.parent / '.env',  # Root .env
    Path(__file__).parent.parent / '.env',  # Backend .env
    Path.cwd() / '.env'  # Current directory .env
]

for env_path in env_locations:
    if env_path.exists():
        load_dotenv(env_path, override=True)
        logger.info(f"Loaded environment from: {env_path}")
        break
else:
    logger.warning("No .env file found in expected locations")

# Initialize services (lazy loading for scrapers)
flight_service = FlightService()
hotel_service = HotelService()
restaurant_service = RestaurantService()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# FastAPI app
app = FastAPI(
    title="TravelAI API",
    version="3.0.0",
    description="World-class Travel API with Smart Scrapers and AI"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= Startup/Shutdown Events =============

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    log_startup()
    logger.info("Initializing services...")
    # Services will initialize on first use to avoid blocking startup
    logger.info("Services ready for lazy initialization")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    log_shutdown()
    # Close scrapers if initialized
    await flight_service.close()
    await hotel_service.close()

# ============= MODELS =============

class FlightSearchRequest(BaseModel):
    """Flight search request"""
    origin: str = Field(..., description="Origin city or airport code")
    destination: str = Field(..., description="Destination city or airport code")
    departure_date: str = Field(..., description="Departure date (YYYY-MM-DD)")
    return_date: Optional[str] = Field(None, description="Return date for round trip")
    adults: int = Field(1, ge=1, le=9, description="Number of adult passengers")
    travel_class: str = Field("economy", description="Travel class")
    max_results: int = Field(10, description="Maximum results to return")

class HotelSearchRequest(BaseModel):
    """Hotel search request"""
    destination: str = Field(..., description="City or location")
    check_in: str = Field(..., description="Check-in date (YYYY-MM-DD)")
    check_out: str = Field(..., description="Check-out date (YYYY-MM-DD)")
    adults: int = Field(2, ge=1, le=10, description="Number of adults")
    rooms: int = Field(1, ge=1, le=5, description="Number of rooms")
    children: int = Field(0, ge=0, le=10, description="Number of children")

class RestaurantSearchRequest(BaseModel):
    """Restaurant search request"""
    destination: str = Field(..., description="City or location")
    cuisine: Optional[str] = Field(None, description="Preferred cuisine type")
    query: Optional[str] = Field(None, description="Custom search query")

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict] = None

class SmartPlannerRequest(BaseModel):
    destination: str
    start_date: str
    end_date: str
    travelers: int = 1
    interests: List[str] = []
    budget: int = 1000
    pace: str = "moderate"

# Import enhanced master agent with better streaming
from agents.master_agent import MasterTravelAgent, TripRequest, AgentThought, AgentAction

# ============= HELPER FUNCTIONS =============

def resolve_airport_code(city: str) -> str:
    """Simple airport code resolution"""
    city_upper = city.upper()
    if len(city_upper) == 3:
        return city_upper
    
    # Common city mappings
    mappings = {
        "NEW YORK": "JFK", "NYC": "JFK",
        "LOS ANGELES": "LAX", "LA": "LAX",
        "CHICAGO": "ORD", "CHI": "ORD",
        "LONDON": "LHR", "LON": "LHR",
        "PARIS": "CDG", "PAR": "CDG",
        "TOKYO": "NRT", "TYO": "NRT",
        "SAN FRANCISCO": "SFO", "SF": "SFO"
    }
    
    for key, code in mappings.items():
        if key in city.upper():
            return code
    
    return city[:3].upper()

async def ai_chat(message: str, context: Optional[Dict] = None) -> str:
    """Simple AI chat using Gemini"""
    try:
        prompt = message
        if context:
            prompt = f"Context: {context}\n\nUser: {message}"
        
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"AI chat error: {e}")
        return "I'm having trouble processing your request. Please try again."

# ============= ENDPOINTS =============

# User Storage (for Clerk integration)
@app.post("/api/store-user")
async def store_user(user_data: Dict[str, Any]):
    """Store user data from Clerk authentication"""
    return {
        "status": "success",
        "message": "User stored",
        "user_id": user_data.get("id", "unknown")
    }

# Health
@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "service": "travelai-backend",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/status")
async def status():
    return {
        "amadeus": "connected",
        "gemini": "connected",
        "uptime": "100%"
    }

# ============= FLIGHTS =============

@app.post("/api/flights/search")
async def search_flights(request: FlightSearchRequest):
    """
    Search for flights using Google Flights scraper
    Returns comprehensive flight data with recommendations
    """
    logger.info(f"Flight search: {request.origin} → {request.destination}")
    
    try:
        results = await flight_service.search({
            'origin': request.origin,
            'destination': request.destination,
            'departure_date': request.departure_date,
            'return_date': request.return_date,
            'adults': request.adults,
            'class': request.travel_class
        })
        
        return JSONResponse(content=results)
        
    except Exception as e:
        logger.error(f"Flight search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/flights")
async def search_flights_get(
    origin: str = Query(..., description="Origin city or airport"),
    destination: str = Query(..., description="Destination city or airport"),
    departure_date: str = Query(..., description="Departure date (YYYY-MM-DD)"),
    return_date: Optional[str] = Query(None, description="Return date"),
    adults: int = Query(1, ge=1, le=9)
):
    """GET endpoint for flight search"""
    request = FlightSearchRequest(
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        return_date=return_date,
        adults=adults,
        travel_class="economy"
    )
    return await search_flights(request)



# ============= HOTELS =============

@app.post("/api/hotels/search")
async def search_hotels(request: HotelSearchRequest):
    """
    Search for hotels using Booking.com scraper
    Returns comprehensive hotel data with recommendations
    """
    logger.info(f"Hotel search: {request.destination}")
    
    try:
        results = await hotel_service.search({
            'destination': request.destination,
            'check_in': request.check_in,
            'check_out': request.check_out,
            'adults': request.adults,
            'rooms': request.rooms,
            'children': request.children
        })
        
        return JSONResponse(content=results)
        
    except Exception as e:
        logger.error(f"Hotel search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hotels")
async def search_hotels_get(
    destination: str = Query(..., description="City or location"),
    check_in: str = Query(..., description="Check-in date (YYYY-MM-DD)"),
    check_out: str = Query(..., description="Check-out date (YYYY-MM-DD)"),
    adults: int = Query(2, ge=1, le=10),
    rooms: int = Query(1, ge=1, le=5)
):
    """GET endpoint for hotel search"""
    request = HotelSearchRequest(
        destination=destination,
        check_in=check_in,
        check_out=check_out,
        adults=adults,
        rooms=rooms,
        children=0
    )
    return await search_hotels(request)


# ============= RESTAURANTS =============

@app.post("/api/restaurants/search")
async def search_restaurants(request: RestaurantSearchRequest):
    """
    Search for restaurants using Tavily
    Returns top-rated restaurants with recommendations
    """
    logger.info(f"Restaurant search: {request.destination}")
    
    try:
        results = await restaurant_service.search({
            'destination': request.destination,
            'cuisine': request.cuisine,
            'query': request.query or f"best restaurants in {request.destination}"
        })
        
        return JSONResponse(content=results)
        
    except Exception as e:
        logger.error(f"Restaurant search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/restaurants")
async def search_restaurants_get(
    destination: str = Query(..., description="City or location"),
    cuisine: Optional[str] = Query(None, description="Cuisine type"),
):
    """GET endpoint for restaurant search"""
    request = RestaurantSearchRequest(
        destination=destination,
        cuisine=cuisine
    )
    return await search_restaurants(request)

# ============= UTILITY ENDPOINTS =============

@app.get("/api/supported-cities")
async def get_supported_cities():
    """Get list of well-supported cities"""
    return {
        "cities": [
            {"code": "NYC", "name": "New York", "country": "USA"},
            {"code": "LAX", "name": "Los Angeles", "country": "USA"},
            {"code": "CHI", "name": "Chicago", "country": "USA"},
            {"code": "MIA", "name": "Miami", "country": "USA"},
            {"code": "SFO", "name": "San Francisco", "country": "USA"},
            {"code": "LON", "name": "London", "country": "UK"},
            {"code": "PAR", "name": "Paris", "country": "France"},
            {"code": "TYO", "name": "Tokyo", "country": "Japan"},
            {"code": "DXB", "name": "Dubai", "country": "UAE"},
            {"code": "SIN", "name": "Singapore", "country": "Singapore"},
            {"code": "HKG", "name": "Hong Kong", "country": "China"},
            {"code": "SYD", "name": "Sydney", "country": "Australia"},
            {"code": "ROM", "name": "Rome", "country": "Italy"},
            {"code": "BCN", "name": "Barcelona", "country": "Spain"},
            {"code": "AMS", "name": "Amsterdam", "country": "Netherlands"}
        ]
    }

@app.get("/api/cache/clear")
async def clear_cache():
    """Clear all cached data (admin endpoint)"""
    try:
        # Clear service caches
        if hasattr(flight_service, 'scraper') and flight_service.scraper:
            flight_service.scraper.cache.clear()
        if hasattr(hotel_service, 'scraper') and hotel_service.scraper:
            hotel_service.scraper.cache.clear()
            
        logger.info("Cache cleared successfully")
        
        return {
            "status": "success",
            "message": "All caches cleared",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= PLANNER =============

@app.post("/api/planner/smart")
async def create_smart_itinerary(request: SmartPlannerRequest):
    """Create comprehensive smart itinerary using Master Agent"""
    try:
        # Calculate trip duration
        start_date = datetime.strptime(request.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(request.end_date, '%Y-%m-%d')
        trip_days = (end_date - start_date).days + 1
        
        # Initialize master agent
        agent = MasterTravelAgent()
        
        # Create trip request for agent
        trip_request = TripRequest(
            destination=request.destination,
            start_date=request.start_date,
            end_date=request.end_date,
            origin=request.origin if hasattr(request, 'origin') else "New York",
            budget=request.budget,
            travelers=request.travelers,
            interests=request.interests if request.interests else ["food", "culture"],
            preferences={"pace": request.pace}
        )
        
        # Collect agent responses
        agent_data = {
            "flights": [],
            "hotels": [],
            "restaurants": [],
            "activities": [],
            "analysis": ""
        }
        
        # Stream agent thoughts and collect data
        async for thought in agent.plan_trip_stream(trip_request):
            if thought.data:
                if "flights" in thought.data:
                    agent_data["flights"] = thought.data["flights"]
                elif "hotels" in thought.data:
                    agent_data["hotels"] = thought.data["hotels"]
                elif "restaurants" in thought.data:
                    agent_data["restaurants"] = thought.data["restaurants"]
                elif "activity_type" in thought.data:
                    agent_data["activities"].append(thought.data)
            
            if thought.action == AgentAction.COMPLETE:
                agent_data["analysis"] = thought.content
                
                # Extract specific recommendations from the AI analysis
                if thought.content:
                    analysis_lines = thought.content.split('\n')
                    for line in analysis_lines:
                        # Look for specific activity mentions
                        if 'visit' in line.lower() or 'explore' in line.lower() or 'see' in line.lower():
                            # Extract place names (usually capitalized words)
                            import re
                            places = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', line)
                            if places and not agent_data.get("specific_places"):
                                agent_data["specific_places"] = places
        
        # Generate structured daily plans with day planner agent
        daily_plans = []
        previous_activities = []  # Track what's been done
        
        # Initialize day planner if needed
        if not hasattr(agent, 'day_planner'):
            await agent._init_services()
        
        for day in range(trip_days):
            current_date = start_date + timedelta(days=day)
            
            # Use day planner for unique activities
            # Use day planner for unique activities - no fallbacks
            if not agent.day_planner:
                raise HTTPException(
                    status_code=500,
                    detail="Day planner agent not initialized"
                )
            
            day_activities = await agent.day_planner.plan_day(
                destination=request.destination,
                day_num=day + 1,
                total_days=trip_days,
                previous_activities=previous_activities,
                interests=request.interests
            )
            
            # Track activities to avoid repetition
            previous_activities.extend([
                day_activities.get('morning', ''),
                day_activities.get('lunch', ''),
                day_activities.get('afternoon', ''),
                day_activities.get('dinner', '')
            ])
            
            # Extract activities - no defaults
            morning_activity = day_activities['morning']
            lunch_activity = day_activities['lunch']
            afternoon_activity = day_activities['afternoon']
            dinner_activity = day_activities['dinner']
            
            # Parse restaurant details from agent data if available
            # This section is now handled by day_planner above
            
            # Get restaurant names for meals
            lunch_restaurant = None
            dinner_restaurant = None
            lunch_name = "Local Restaurant"
            dinner_name = "Dinner Restaurant"
            
            if agent_data["restaurants"]:
                # Use different restaurants for lunch and dinner
                lunch_idx = day % len(agent_data["restaurants"])
                dinner_idx = (day + 1) % len(agent_data["restaurants"])
                
                lunch_restaurant = agent_data["restaurants"][lunch_idx]
                dinner_restaurant = agent_data["restaurants"][dinner_idx] if len(agent_data["restaurants"]) > 1 else agent_data["restaurants"][0]
                
                # Get actual restaurant names
                lunch_name = lunch_restaurant.get("name", "Local Restaurant")
                dinner_name = dinner_restaurant.get("name", "Evening Restaurant")
            
            # Create slots with real data
            day_plan = {
                "day": day + 1,
                "date": current_date.strftime('%Y-%m-%d'),
                "dayName": current_date.strftime('%A'),
                "slots": [
                    {
                        "id": f"day{day+1}_morning",
                        "timeSlot": "morning",
                        "startTime": "09:00",
                        "endTime": "12:00",
                        "activity": morning_activity,  # Using 'activity' field for frontend compatibility
                        "title": morning_activity,
                        "description": f"Start your day exploring {request.destination}'s highlights",
                        "location": request.destination,
                        "duration": "3 hours",
                        "type": "activity",
                        "budget": request.budget / (trip_days * 3),
                        "recommendations": agent_data["activities"][:1] if agent_data["activities"] else []
                    },
                    {
                        "id": f"day{day+1}_lunch",
                        "timeSlot": "midday",
                        "startTime": "12:00",
                        "endTime": "14:00",
                        "activity": lunch_activity,  # From day planner
                        "title": lunch_activity,
                        "description": f"Experience authentic {lunch_restaurant.get('cuisine', 'local')} cuisine" if lunch_restaurant else "Enjoy local cuisine",
                        "location": lunch_restaurant.get("location", request.destination) if lunch_restaurant else request.destination,
                        "duration": "2 hours",
                        "type": "meal",
                        "budget": request.budget / (trip_days * 6),
                        "restaurant": lunch_restaurant,
                        "booking_url": lunch_restaurant.get("link") if lunch_restaurant else None
                    },
                    {
                        "id": f"day{day+1}_afternoon",
                        "timeSlot": "afternoon",
                        "startTime": "14:00",
                        "endTime": "18:00",
                        "activity": afternoon_activity,  # Real activity from agent
                        "title": afternoon_activity,
                        "description": f"Explore {request.destination}'s {request.interests[0] if request.interests else 'cultural'} attractions",
                        "location": request.destination,
                        "duration": "4 hours",
                        "type": "activity",
                        "budget": request.budget / (trip_days * 3),
                        "recommendations": agent_data["activities"][1:2] if len(agent_data["activities"]) > 1 else []
                    },
                    {
                        "id": f"day{day+1}_evening",
                        "timeSlot": "evening",
                        "startTime": "19:00",
                        "endTime": "22:00",
                        "activity": dinner_activity,  # From day planner
                        "title": dinner_activity,
                        "description": f"Savor {dinner_restaurant.get('cuisine', 'exquisite')} dishes" if dinner_restaurant else "Evening dining experience",
                        "location": dinner_restaurant.get("location", request.destination) if dinner_restaurant else request.destination,
                        "duration": "3 hours",
                        "type": "meal",
                        "budget": request.budget / (trip_days * 4),
                        "restaurant": dinner_restaurant,
                        "booking_url": dinner_restaurant.get("link") if dinner_restaurant else None
                    }
                ]
            }
            daily_plans.append(day_plan)
        
        # Create comprehensive itinerary response
        itinerary_response = {
            "status": "success",
            "itinerary_id": f"itin_{int(datetime.now().timestamp())}",
            "created_at": datetime.now().isoformat(),
            "destination": request.destination,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "duration_days": trip_days,
            "travelers": request.travelers,
            "total_budget": request.budget,
            "interests": request.interests,
            "pace": request.pace,
            "daily_plans": daily_plans,
            "recommendations": {
                "flights": agent_data["flights"],
                "hotels": agent_data["hotels"],
                "restaurants": agent_data["restaurants"],
                "activities": agent_data["activities"]
            },
            "ai_analysis": agent_data["analysis"],
            "export_format": {
                "version": "1.0",
                "type": "travelai_itinerary",
                "exportable": True
            },
            "journey_data": {
                "total_activities": len(daily_plans) * 4,
                "completed": 0,
                "progress_percentage": 0,
                "levels": trip_days,
                "current_level": 1,
                "badges": [
                    {"id": "explorer", "name": "Explorer", "icon": "🗺️", "unlocked": False},
                    {"id": "foodie", "name": "Foodie", "icon": "🍴", "unlocked": False},
                    {"id": "adventurer", "name": "Adventurer", "icon": "🎯", "unlocked": False}
                ]
            }
        }
        
        # Auto-save to Convex if user is authenticated
        try:
            # Import Convex client
            from convex import ConvexClient
            convex_url = os.getenv("CONVEX_URL")
            
            if convex_url:
                convex_client = ConvexClient(convex_url)
                
                # Note: In production, get actual user ID from authentication
                # For now, we'll include instructions for frontend to save
                itinerary_response["save_instructions"] = "Frontend should save this to Convex using richItineraries.saveFromBackend"
                logger.info(f"Itinerary ready to be saved to Convex: {itinerary_response['itinerary_id']}")
        except Exception as e:
            logger.warning(f"Could not prepare Convex save: {e}")
        
        return itinerary_response
        
    except Exception as e:
        logger.error(f"Smart planner error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to generate itinerary",
                "message": "Unable to connect to travel planning services. Please ensure all API services are configured.",
                "details": str(e),
                "required_services": ["OpenRouter API", "Amadeus API", "Tavily API"]
            }
        )


@app.post("/api/planner/save")
async def save_itinerary(request: Dict[str, Any]):
    """Save itinerary to Convex database"""
    try:
        from convex import ConvexClient
        convex_url = os.getenv("CONVEX_URL")
        
        if not convex_url:
            raise HTTPException(status_code=500, detail="Convex URL not configured")
        
        convex_client = ConvexClient(convex_url)
        
        # Transform field names from snake_case to camelCase for Convex
        journey_data = request.get('journey_data', {})
        transformed_journey = {
            "totalActivities": journey_data.get('total_activities', 0),
            "completed": journey_data.get('completed', 0),
            "progressPercentage": journey_data.get('progress_percentage', 0),
            "levels": journey_data.get('levels', 1),
            "currentLevel": journey_data.get('current_level', 1),
            "badges": journey_data.get('badges', [])
        }
        
        # Save to Convex
        result = convex_client.mutation(
            "richItineraries:saveFromBackend",
            {
                "userId": request.get('user_id'),  # Should come from frontend
                "itineraryData": {
                    "itineraryId": request.get('itinerary_id'),
                    "destination": request.get('destination'),
                    "startDate": request.get('start_date'),
                    "endDate": request.get('end_date'),
                    "durationDays": request.get('duration_days'),
                    "travelers": request.get('travelers'),
                    "totalBudget": request.get('total_budget'),
                    "interests": request.get('interests', []),
                    "pace": request.get('pace', 'moderate'),
                    "dailyPlans": request.get('daily_plans', []),
                    "recommendations": request.get('recommendations', {}),
                    "aiAnalysis": request.get('ai_analysis', ''),
                    "exportFormat": request.get('export_format', {}),
                    "journeyData": transformed_journey
                }
            }
        )
        
        return {
            "status": "success",
            "message": "Itinerary saved to Convex",
            "convex_id": str(result),
            "saved_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Save itinerary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/planner/export/{itinerary_id}")
async def export_itinerary(itinerary_id: str, format: str = "json"):
    """Export itinerary in various formats"""
    try:
        # TODO: Fetch from database/cache
        # For now, return a sample export format
        
        if format == "json":
            return {
                "status": "success",
                "format": "json",
                "itinerary_id": itinerary_id,
                "download_url": f"/api/planner/download/{itinerary_id}.json",
                "content": {
                    "message": "Export functionality will be implemented with database integration"
                }
            }
        elif format == "pdf":
            return {
                "status": "success",
                "format": "pdf",
                "message": "PDF export coming soon"
            }
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")
            
    except Exception as e:
        logger.error(f"Export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= AI CHAT =============

@app.post("/api/chat/")
async def chat(request: ChatRequest):
    """AI chat endpoint"""
    response = await ai_chat(request.message, request.context)
    return {
        "status": "success",
        "response": response,
        "model": "gemini-1.5-flash"
    }

@app.post("/api/chat/agent")
async def chat_agent(request: ChatRequest):
    """AI agent chat with travel context"""
    travel_context = f"You are a travel assistant. Help with: {request.message}"
    response = await ai_chat(travel_context, request.context)
    return {
        "status": "success",
        "response": response,
        "model": "gemini-1.5-flash"
    }

# ============= MASTER AGENT ENDPOINTS =============

@app.post("/api/agent/plan")
async def plan_trip_with_agent(request: TripRequest):
    """
    Complete trip planning with enhanced streaming responses
    Uses the world-class master agent with intelligent 5-stage planning:
    1. Understanding - Analyze the request
    2. Planning - Develop search strategy
    3. Searching - Gather data from all sources
    4. Analyzing - Process and evaluate options
    5. Recommending - Create personalized recommendations
    """
    logger.info(f"Trip planning request: {request.destination}")
    
    async def stream_generator():
        """Generate SSE stream with enhanced agent"""
        agent = MasterTravelAgent()
        try:
            async for thought in agent.plan_trip_stream(request):
                # Format as Server-Sent Event
                event_data = json.dumps(thought.dict())
                yield f"data: {event_data}\n\n"
                
            # Send completion signal
            yield f"data: [DONE]\n\n"
            
        except Exception as e:
            logger.error(f"Streaming error: {e}", exc_info=True)
            error_data = {
                "action": "ERROR",
                "content": "An error occurred during planning",
                "error": str(e)
            }
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.post("/api/agent/search")
async def quick_search(
    query: str = Body(..., description="Search query"),
    context: Optional[Dict] = Body(None, description="Additional context")
):
    """
    Quick search for travel information
    Simpler endpoint for basic queries
    """
    logger.info(f"Quick search: {query}")
    agent = MasterTravelAgent()
    
    try:
        response = await agent.quick_search(query)
        return {
            "status": "success",
            "response": response,
            "query": query,
            "context": context
        }
    except Exception as e:
        logger.error(f"Quick search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)