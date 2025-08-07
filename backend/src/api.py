"""TravelAI Backend API - Complete Integration with Waypoint-BE Services

This is the primary entry point for the TravelAI MVP backend API with full Amadeus integration.
Includes all travel services from waypoint-be project.
"""

import os
import json
import httpx
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio

# Load environment variables
load_dotenv(Path(__file__).parent.parent / '.env')

# Import agent functionality
import sys
sys.path.append(str(Path(__file__).parent.parent))
from agent import run_agent_with_calculator, run_agent_basic, run_agent_with_mcp

# Import all travel services
from .services.agent_workflow import get_agent_workflow_service
from .services.restaurant_agent import RestaurantAgent
from .services.flights import (
    search_flights,
    AmadeusFlightService as FlightSearchService,
    FlightSearchRequest,
    FlexibleFlightSearch,
    FlexibleSearchRequest,
    CheapestDateSearch,
    CheapestDateSearchRequest
)
from .services.travel_services import (
    HotelSearchService,
    HotelSearchRequest,
    ActivitySearchService,
    ActivitySearchRequest,
    FlightStatusService,
    FlightStatusRequest,
    CheckInLinksService,
    CheckInLinksRequest,
    TransferSearchService,
    TransferSearchRequest
)
from .services.market_insights import (
    MarketInsightsService,
    FlightInspirationRequest,
    TravelAnalyticsRequest,
    BusiestPeriodRequest,
    FlightDelayRequest,
    TripPurposeRequest,
    AirportRoutesRequest,
    HotelSentimentsRequest,
    PriceAnalysisRequest
)

# Import existing services for backward compatibility
from .services.smart_planner import SmartPlannerService
from .services.user_service import UserService
from .agents.ai_agent import AIAgent
from .agents.workflow_agent import WorkflowAgent
from .models.requests import (
    DailySlot, DailyPlan, SmartItinerary, ChatRequest, WeatherRequest,
    SmartPlannerRequest, StoreUserRequest
)
from .core.config import get_settings
from .core.exceptions import TravelAIException

try:
    from convex import ConvexClient
except ImportError:
    ConvexClient = None

# Initialize settings
settings = get_settings()

# Define tags metadata for better organization in Swagger UI
tags_metadata = [
    {
        "name": "System",
        "description": "System health and status endpoints",
    },
    {
        "name": "Flights - Search & Booking",
        "description": "Search and book flights, find cheapest dates and flexible options",
    },
    {
        "name": "Flights - Operations",
        "description": "Flight status tracking and check-in services",
    },
    {
        "name": "Flights - Analytics",
        "description": "Flight price analysis and historical data",
    },
    {
        "name": "Flights - Predictions",
        "description": "ML-powered flight delay predictions",
    },
    {
        "name": "Flights - Inspiration & Planning",
        "description": "Flight inspiration and destination discovery",
    },
    {
        "name": "Hotels",
        "description": "Hotel search, booking, and sentiment analysis",
    },
    {
        "name": "Activities & Tours",
        "description": "Find and book tours, activities, and experiences",
    },
    {
        "name": "Transfers & Ground Transport",
        "description": "Airport transfers and ground transportation",
    },
    {
        "name": "Airports",
        "description": "Airport information and route data",
    },
    {
        "name": "Market Analytics",
        "description": "Travel market insights, trends, and analytics",
    },
    {
        "name": "Trip Intelligence",
        "description": "Smart trip analysis and predictions",
    },
    {
        "name": "Restaurants",
        "description": "Restaurant discovery and recommendations",
    },
    {
        "name": "AI Agents",
        "description": "AI-powered travel planning agents",
    },
    {
        "name": "Smart Planner",
        "description": "AI-powered daily itinerary planning",
    },
    {
        "name": "User Management",
        "description": "User authentication and profile management",
    },
]

# Create FastAPI app with proper metadata
app = FastAPI(
    title="TravelAI Backend API with Amadeus Integration",
    description="""
    🚀 **Comprehensive Travel API Platform**
    
    This API provides access to real Amadeus travel services, AI agents, and smart planning features.
    
    ## Features
    
    - ✈️ **Flight Services**: Search, book, track status, find cheapest dates
    - 🏨 **Hotels**: Search accommodations and analyze guest sentiments
    - 🎯 **Activities**: Discover tours and experiences
    - 🚗 **Transfers**: Book ground transportation
    - 📊 **Analytics**: Market insights and travel trends
    - 🤖 **AI Agents**: Intelligent travel planning assistance
    - 🔮 **Predictions**: ML-powered delay and trip purpose predictions
    - 📅 **Smart Planner**: AI-powered daily itinerary creation
    
    ## Environment
    
    Using Amadeus API for real travel data.
    """,
    version="3.0.0",
    openapi_tags=tags_metadata,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Configure CORS for all environments
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000", 
        "http://localhost:8000",
        "https://fantastic-spork-alpha.vercel.app",
        "https://*.vercel.app",
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"]
)

# Global service instances (lazy initialized)
services = {
    "planner": None,
    "user": None,
    "ai_agent": None,
    "workflow_agent": None
}

def get_planner_service() -> SmartPlannerService:
    """Get smart planner service instance"""
    if services["planner"] is None:
        services["planner"] = SmartPlannerService()
    return services["planner"]

def get_user_service() -> UserService:
    """Get user service instance"""
    if services["user"] is None:
        services["user"] = UserService()
    return services["user"]

def get_ai_agent() -> AIAgent:
    """Get AI agent instance"""
    if services["ai_agent"] is None:
        services["ai_agent"] = AIAgent()
    return services["ai_agent"]

def get_workflow_agent() -> WorkflowAgent:
    """Get workflow agent instance"""
    if services["workflow_agent"] is None:
        services["workflow_agent"] = WorkflowAgent()
    return services["workflow_agent"]

# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

@app.get("/", tags=["System"])
async def root():
    return {
        "message": "Welcome to TravelAI Backend API with Amadeus Integration",
        "version": "3.0.0",
        "docs": "/docs" if settings.debug else "Available in development mode"
    }

@app.get("/api/health", tags=["System"])
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "travelai-backend",
        "version": "3.0.0",
        "timestamp": datetime.now().isoformat(),
        "amadeus": "enabled"
    }

@app.get("/api/hello", tags=["System"])
async def hello():
    """Simple hello endpoint for testing"""
    return {
        "message": "Hello from TravelAI Backend with Amadeus!",
        "version": "3.0.0",
        "docs": "/docs" if settings.debug else "Available in development mode"
    }

@app.get("/api/test-env", tags=["System"])
async def test_environment():
    """Test environment configuration (development only)"""
    if not settings.debug:
        raise HTTPException(status_code=404, detail="Not found")
    
    return {
        "gemini_api_key": "✓" if settings.gemini_api_key else "✗",
        "convex_url": "✓" if settings.convex_url else "✗",
        "clerk_secret_key": "✓" if settings.clerk_secret_key else "✗",
        "amadeus_client_id": "✓" if os.getenv("AMADEUS_API_KEY") else "✗",
        "amadeus_client_secret": "✓" if os.getenv("AMADEUS_Secret") else "✗",
        "openrouter_api_key": "✓" if os.getenv("OPENROUTER_API_KEY") else "✗",
        "environment": "development"
    }

# ============================================================================
# USER MANAGEMENT (Write Operations)
# ============================================================================

@app.post("/api/store-user", tags=["User Management"])
async def store_user(request: StoreUserRequest):
    """Store user data from Clerk authentication (Write Operation)"""
    try:
        result = await get_user_service().store_user(request)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "User storage failed but authentication succeeded"
        }

# ============================================================================
# AI CHAT (External API)
# ============================================================================

@app.post("/api/chat", tags=["AI Agents"])
async def chat_with_ai(request: ChatRequest):
    """AI-powered chat using Gemini (External API)"""
    try:
        result = await get_ai_agent().chat_completion(request.message, request.context)
        return {
            "status": "success",
            "response": result,
            "context": request.context
        }
    except Exception as e:
        return {
            "status": "success",
            "response": f"I understand you're asking about: {request.message}. How can I help you plan your trip?",
            "fallback": True,
            "error": str(e)
        }

@app.post("/api/chat/agent", tags=["AI Agents"])
async def chat_with_workflow_agent(request: ChatRequest):
    """AI-powered chat using workflow agent (External API)"""
    try:
        result = await get_workflow_agent().process_query(request.message, request.context)
        return {
            "status": "success",
            "response": result.get("response", "I'm here to help with your travel planning!"),
            "data": result.get("data", {}),
            "action": result.get("action", "general_chat")
        }
    except Exception as e:
        return {
            "status": "success",
            "response": "I'm your travel planning assistant! How can I help you today?",
            "fallback": True,
            "error": str(e)
        }

@app.get("/api/agent/workflow", tags=["AI Agents"])
async def agent_workflow(query: str) -> dict:
    """Run agent workflow for complex travel queries"""
    try:
        agent_workflow_service = get_agent_workflow_service()
        result = await agent_workflow_service.run_workflow(query)
        return {
            "status": "success",
            "result": result,
            "message": "Workflow executed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

# ============================================================================
# FLIGHT SEARCH (Amadeus API)
# ============================================================================

@app.post("/api/flights/search", tags=["Flights - Search & Booking"])
async def search_flights_api(request: FlightSearchRequest):
    """
    Search for flights using Amadeus API with support for both one-way and roundtrip.
    
    Example request:
    {
        "origin": "LAX",
        "destination": "JFK",
        "departure_date": "2025-01-15",
        "return_date": "2025-01-22",
        "trip_type": "round-trip",
        "adults": 2,
        "seat_class": "economy"
    }
    """
    try:
        flight_service = FlightSearchService()
        result = await flight_service.search(request)
        return {"status": "success", "flights": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flight search failed: {str(e)}")

@app.get("/api/flights", tags=["Flights - Search & Booking"])
async def get_flights(
    from_city: str,
    to_city: str,
    departure_date: str,
    return_date: Optional[str] = None
) -> dict:
    """Smart flight search with multiple airports"""
    try:
        result = await search_flights(from_city, to_city, departure_date, return_date)
        return {
            "status": "success",
            "outbound": result.outbound,
            "return_flights": result.return_flights,
            "best_options": result.best_options,
            "total_found": result.total,
            "searches_executed": result.searches
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flight search failed: {str(e)}")

@app.post("/api/flights/flexible", tags=["Flights - Search & Booking"])
async def search_flexible_dates(request: FlexibleSearchRequest):
    """Search for cheapest flight dates within a month"""
    try:
        flexible_service = FlexibleFlightSearch()
        result = await flexible_service.search_flexible_dates(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flexible search failed: {str(e)}")

@app.post("/api/flights/cheapest-dates", tags=["Flights - Search & Booking"])
async def search_cheapest_dates(request: CheapestDateSearchRequest):
    """Find the cheapest travel dates for a route using Amadeus"""
    try:
        cheapest_date_service = CheapestDateSearch()
        result = await cheapest_date_service.search_cheapest_dates(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cheapest date search failed: {str(e)}")

@app.get("/api/flights/cheapest-dates", tags=["Flights - Search & Booking"])
async def get_cheapest_dates(
    origin: str,
    destination: str,
    departure_date: Optional[str] = None,
    one_way: bool = False,
    duration: Optional[int] = None
):
    """Simple GET endpoint for cheapest date search"""
    try:
        request = CheapestDateSearchRequest(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            one_way=one_way,
            duration=duration
        )
        cheapest_date_service = CheapestDateSearch()
        result = await cheapest_date_service.search_cheapest_dates(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cheapest date search failed: {str(e)}")

# ============================================================================
# HOTEL SEARCH (Amadeus API)
# ============================================================================

@app.post("/api/hotels/search", tags=["Hotels"])
async def search_hotels_api(request: HotelSearchRequest):
    """Search for hotels using Amadeus API by city or coordinates"""
    try:
        hotel_service = HotelSearchService()
        result = await hotel_service.search_hotels(request)
        return {"status": "success", "hotels": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hotel search failed: {str(e)}")

@app.get("/api/hotels/search", tags=["Hotels"])
async def get_hotels(
    city_code: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    check_in_date: str = None,
    check_out_date: str = None,
    adults: int = 1,
    rooms: int = 1
):
    """Simple GET endpoint for hotel search"""
    try:
        request = HotelSearchRequest(
            city_code=city_code,
            latitude=latitude,
            longitude=longitude,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            adults=adults,
            rooms=rooms
        )
        hotel_service = HotelSearchService()
        result = await hotel_service.search_hotels(request)
        return {"status": "success", "hotels": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hotel search failed: {str(e)}")

@app.post("/api/hotels/sentiments", tags=["Hotels"])
async def get_hotel_sentiments(request: HotelSentimentsRequest):
    """Get hotel sentiment analysis"""
    try:
        insights_service = MarketInsightsService()
        result = await insights_service.get_hotel_sentiments(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hotel sentiments analysis failed: {str(e)}")

@app.get("/api/hotels/sentiments", tags=["Hotels"])
async def get_hotel_sentiments_get(hotel_ids: str):
    """Get hotel sentiments - GET endpoint"""
    try:
        request = HotelSentimentsRequest(hotel_ids=hotel_ids.split(','))
        insights_service = MarketInsightsService()
        result = await insights_service.get_hotel_sentiments(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hotel sentiments analysis failed: {str(e)}")

# ============================================================================
# ACTIVITIES SEARCH (Amadeus API)
# ============================================================================

@app.post("/api/activities/search", tags=["Activities & Tours"])
async def search_activities_api(request: ActivitySearchRequest):
    """Search for tours and activities using Amadeus API"""
    try:
        activity_service = ActivitySearchService()
        result = await activity_service.search_activities(request)
        return {"status": "success", "activities": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Activity search failed: {str(e)}")

@app.get("/api/activities/search", tags=["Activities & Tours"])
async def get_activities(
    latitude: float,
    longitude: float,
    radius: int = 5,
    adults: int = 1
):
    """Simple GET endpoint for activity search"""
    try:
        request = ActivitySearchRequest(
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            adults=adults
        )
        activity_service = ActivitySearchService()
        result = await activity_service.search_activities(request)
        return {"status": "success", "activities": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Activity search failed: {str(e)}")

# ============================================================================
# RESTAURANT SEARCH (AI Agent)
# ============================================================================

@app.post("/api/restaurants/search", tags=["Restaurants"])
async def search_restaurants(query: str, location: str):
    """Search restaurants using AI agent"""
    try:
        restaurant_agent = RestaurantAgent()
        result = await restaurant_agent.scrape_restaurants(f"{query} in {location}", stream=False)
        return {"status": "success", "restaurants": result}
    except Exception as e:
        return {
            "status": "success",
            "restaurants": {
                "result": [{
                    "name": f"Local Restaurant in {location}",
                    "cuisine": "Local cuisine",
                    "rating": 4.5,
                    "price_range": "$$",
                    "booking_url": "https://opentable.com"
                }]
            },
            "fallback": True,
            "error": str(e)
        }

@app.get("/api/restaurants", tags=["Restaurants"])
async def get_restaurants(query: str = None, stream: bool = False) -> dict:
    """GET endpoint for restaurant search"""
    try:
        restaurant_agent = RestaurantAgent()
        result = await restaurant_agent.scrape_restaurants(query, stream)
        return {
            "status": "success",
            "result": result,
            "message": "Restaurant search completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restaurant search failed: {str(e)}")

# ============================================================================
# FLIGHT OPERATIONS (Amadeus API)
# ============================================================================

@app.get("/api/flights/status", tags=["Flights - Operations"])
async def get_flight_status(
    carrier_code: str,
    flight_number: str,
    scheduled_departure_date: str
):
    """Get real-time flight status"""
    try:
        request = FlightStatusRequest(
            carrier_code=carrier_code,
            flight_number=flight_number,
            scheduled_departure_date=scheduled_departure_date
        )
        status_service = FlightStatusService()
        result = await status_service.get_flight_status(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flight status check failed: {str(e)}")

@app.get("/api/flights/checkin-links", tags=["Flights - Operations"])
async def get_checkin_links(airline_code: str):
    """Get airline check-in links"""
    try:
        request = CheckInLinksRequest(airline_code=airline_code)
        checkin_service = CheckInLinksService()
        result = await checkin_service.get_checkin_links(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Check-in links retrieval failed: {str(e)}")

# ============================================================================
# TRANSFERS (Amadeus API)
# ============================================================================

@app.post("/api/transfers/search", tags=["Transfers & Ground Transport"])
async def search_transfers(request: TransferSearchRequest):
    """Search for airport transfers and ground transportation"""
    try:
        transfer_service = TransferSearchService()
        result = await transfer_service.search_transfers(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transfer search failed: {str(e)}")

# ============================================================================
# MARKET INSIGHTS & ANALYTICS (Amadeus API)
# ============================================================================

@app.get("/api/flights/inspiration", tags=["Flights - Inspiration & Planning"])
async def get_flight_inspiration(
    origin: str,
    max_price: Optional[int] = None,
    departure_date: Optional[str] = None,
    one_way: bool = False,
    duration: Optional[int] = None
):
    """Get flight inspiration - where can I go for this budget?"""
    try:
        request = FlightInspirationRequest(
            origin=origin,
            max_price=max_price,
            departure_date=departure_date,
            one_way=one_way,
            duration=duration
        )
        insights_service = MarketInsightsService()
        result = await insights_service.get_flight_inspiration(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flight inspiration failed: {str(e)}")

@app.get("/api/analytics/most-traveled", tags=["Market Analytics"])
async def get_most_traveled_destinations(
    origin_city_code: str,
    period: str,  # Format: YYYY-MM
    max_results: int = 10
):
    """Get most traveled destinations from a city"""
    try:
        request = TravelAnalyticsRequest(
            origin_city_code=origin_city_code,
            period=period,
            max_results=max_results
        )
        insights_service = MarketInsightsService()
        result = await insights_service.get_most_traveled(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Travel analytics failed: {str(e)}")

@app.get("/api/analytics/most-booked", tags=["Market Analytics"])
async def get_most_booked_destinations(
    origin_city_code: str,
    period: str,  # Format: YYYY-MM
    max_results: int = 10
):
    """Get most booked destinations from a city"""
    try:
        request = TravelAnalyticsRequest(
            origin_city_code=origin_city_code,
            period=period,
            max_results=max_results
        )
        insights_service = MarketInsightsService()
        result = await insights_service.get_most_booked(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Booking analytics failed: {str(e)}")

@app.get("/api/analytics/busiest-period", tags=["Market Analytics"])
async def get_busiest_travel_period(
    city_code: str,
    period: str,  # Format: YYYY
    direction: str = "ARRIVING"
):
    """Get busiest travel periods for a city"""
    try:
        request = BusiestPeriodRequest(
            city_code=city_code,
            period=period,
            direction=direction
        )
        insights_service = MarketInsightsService()
        result = await insights_service.get_busiest_period(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Busiest period analysis failed: {str(e)}")

@app.get("/api/flights/delay-prediction", tags=["Flights - Predictions"])
async def predict_flight_delay(
    origin: str,
    destination: str,
    departure_date: str,
    departure_time: str,
    arrival_date: str,
    arrival_time: str,
    airline_code: str,
    flight_number: str,
    aircraft_code: Optional[str] = None
):
    """Predict flight delay probability"""
    try:
        request = FlightDelayRequest(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            departure_time=departure_time,
            arrival_date=arrival_date,
            arrival_time=arrival_time,
            airline_code=airline_code,
            flight_number=flight_number,
            aircraft_code=aircraft_code
        )
        insights_service = MarketInsightsService()
        result = await insights_service.predict_flight_delay(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delay prediction failed: {str(e)}")

@app.get("/api/trips/purpose-prediction", tags=["Trip Intelligence"])
async def predict_trip_purpose(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str,
    search_date: Optional[str] = None
):
    """Predict if trip is business or leisure"""
    try:
        request = TripPurposeRequest(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            search_date=search_date
        )
        insights_service = MarketInsightsService()
        result = await insights_service.predict_trip_purpose(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trip purpose prediction failed: {str(e)}")

@app.get("/api/airports/routes", tags=["Airports"])
async def get_airport_routes(
    airport_code: str,
    max_results: int = 50
):
    """Get all direct routes from an airport"""
    try:
        request = AirportRoutesRequest(
            airport_code=airport_code,
            max_results=max_results
        )
        insights_service = MarketInsightsService()
        result = await insights_service.get_airport_routes(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Airport routes lookup failed: {str(e)}")

@app.get("/api/flights/price-analysis", tags=["Flights - Analytics"])
async def analyze_flight_prices(
    origin: str,
    destination: str,
    departure_date: str,
    currency: str = "USD",
    one_way: bool = False
):
    """Analyze flight price metrics for a route"""
    try:
        request = PriceAnalysisRequest(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            currency=currency,
            one_way=one_way
        )
        insights_service = MarketInsightsService()
        result = await insights_service.analyze_flight_prices(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Price analysis failed: {str(e)}")

# ============================================================================
# SMART PLANNER (Write Operations + External APIs)
# ============================================================================

@app.post("/api/planner/smart", tags=["Smart Planner"])
async def create_smart_itinerary(request: SmartPlannerRequest):
    """Create a smart daily planner with AI recommendations (Write + External)"""
    try:
        result = await get_planner_service().create_smart_itinerary(request)
        return {
            "status": "success",
            "itinerary": result["itinerary"],
            "flight_inspiration": result.get("flight_inspiration", {}),
            "days_planned": result["days_planned"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Smart planner error: {str(e)}")

@app.post("/api/save-itinerary", tags=["Smart Planner"])
async def save_itinerary(request: Request):
    """Save smart itinerary to database (Write Operation)"""
    body = await request.json()
    try:
        result = await get_planner_service().save_itinerary(body)
        return result
    except Exception as e:
        return {
            "success": True,
            "trip_id": str(uuid.uuid4()),
            "message": "Itinerary saved (demo mode)",
            "demo_mode": True,
            "error": str(e)
        }

@app.put("/api/planner/slot/{date}/{slot_id}", tags=["Smart Planner"])
async def update_slot(date: str, slot_id: str, request: Request):
    """Update a specific slot in the itinerary (Write Operation)"""
    body = await request.json()
    try:
        result = await get_planner_service().update_slot(date, slot_id, body)
        return {
            "status": "success",
            "message": f"Slot {slot_id} updated for {date}",
            "updated_slot": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Slot update failed: {str(e)}")

@app.post("/api/planner/slot/complete", tags=["Smart Planner"])
async def complete_slot(request: Request):
    """Mark a slot as completed and trigger celebration (Write Operation)"""
    body = await request.json()
    slot_id = body.get("slot_id")
    
    try:
        result = await get_planner_service().complete_slot(slot_id)
        return {
            "status": "success",
            "message": "Slot completed!",
            "celebration": True,
            "confetti": True,
            "slot_id": slot_id,
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Slot completion failed: {str(e)}")

# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.get("/api/weather/{location}", tags=["Smart Planner"])
async def get_weather(location: str, date: str):
    """Get weather information for planning (External API)"""
    # This would connect to a weather API in production
    weather = {
        "temperature": "22°C",
        "condition": "Sunny",
        "humidity": "65%",
        "wind": "10 km/h",
        "icon": "☀️"
    }
    return {"status": "success", "weather": weather}

# ============================================================================
# GAMIFICATION ENDPOINTS (Write Operations)
# ============================================================================

@app.post("/api/achievements/check", tags=["Smart Planner"])
async def check_achievements(request: Request):
    """Check and award achievements based on user progress (Write Operation)"""
    body = await request.json()
    user_id = body.get("user_id")
    action = body.get("action")
    
    achievements = []
    if action == "slot_completed":
        achievements.append({
            "id": "first_step",
            "name": "First Steps",
            "description": "Complete your first activity",
            "icon": "👣",
            "points": 100
        })
    elif action == "perfect_day":
        achievements.append({
            "id": "perfect_day",
            "name": "Perfect Day",
            "description": "Complete all 4 slots in one day",
            "icon": "🏆",
            "points": 500
        })
    
    return {
        "status": "success",
        "new_achievements": achievements
    }

@app.post("/api/mood/track", tags=["Smart Planner"])
async def track_mood(request: Request):
    """Track user mood and energy for AI recommendations (Write Operation)"""
    body = await request.json()
    
    mood = body.get("mood")
    energy = body.get("energy", 5)
    
    suggestions = []
    if mood == "tired" or energy < 4:
        suggestions = ["Consider a relaxing cafe visit", "Maybe skip the hiking activity"]
    elif mood == "excited" and energy > 7:
        suggestions = ["Great time for adventure activities!", "Consider extending your exploration time"]
    
    return {
        "status": "success",
        "suggestions": suggestions,
        "weather_impact": False,
        "crowd_impact": False
    }

# ============================================================================
# DEVELOPMENT TOOLS
# ============================================================================

if settings.debug:
    @app.get("/api/dev/routes", tags=["System"])
    async def list_routes():
        """List all available routes (development only)"""
        routes = []
        for route in app.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                routes.append({
                    "path": route.path,
                    "methods": list(route.methods),
                    "name": route.name
                })
        return {"routes": routes}

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(TravelAIException)
async def travel_ai_exception_handler(request: Request, exc: TravelAIException):
    """Handle custom TravelAI exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_type,
            "message": exc.message,
            "details": exc.details
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP_ERROR",
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )