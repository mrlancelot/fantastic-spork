"""
Simplified TravelAI Backend API
Compact implementation with all endpoints using Amadeus for travel data and Google SDK for AI
"""

import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from amadeus import Client, ResponseError
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Initialize services
amadeus = Client(
    client_id=os.getenv("AMADEUS_API_KEY"),
    client_secret=os.getenv("AMADEUS_Secret"),
    hostname='test'
)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# FastAPI app
app = FastAPI(
    title="TravelAI API",
    version="2.0.0",
    description="Simplified Travel API with Amadeus and Google AI"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= MODELS =============

class FlightSearchRequest(BaseModel):
    origin: str
    destination: str
    departure_date: str
    return_date: Optional[str] = None
    adults: int = 1
    travel_class: str = "ECONOMY"
    max_results: int = 10

class HotelSearchRequest(BaseModel):
    city_code: str
    check_in_date: str
    check_out_date: str
    adults: int = 1
    radius: int = 5
    radius_unit: str = "KM"
    amenities: Optional[List[str]] = None
    ratings: Optional[List[int]] = None

class ActivitySearchRequest(BaseModel):
    latitude: float
    longitude: float
    radius: int = 5
    max_results: int = 20

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

# Import agent - Add src directory to path properly
import sys
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
logger.info(f"Added to sys.path: {current_dir}")

from agents.master_agent import MasterTravelAgent, TripRequest, AgentThought, AgentAction
from fastapi.responses import StreamingResponse
import asyncio
import json

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
    """Search flights using Amadeus"""
    try:
        origin = resolve_airport_code(request.origin)
        destination = resolve_airport_code(request.destination)
        
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=request.departure_date,
            returnDate=request.return_date,
            adults=request.adults,
            travelClass=request.travel_class,
            max=request.max_results
        )
        
        flights = []
        for offer in response.data[:request.max_results]:
            price = offer.get('price', {})
            itineraries = offer.get('itineraries', [])
            
            for itinerary in itineraries:
                segments = itinerary.get('segments', [])
                if segments:
                    first_seg = segments[0]
                    last_seg = segments[-1]
                    
                    flights.append({
                        "airline": first_seg.get('carrierCode', 'N/A'),
                        "flight_number": first_seg.get('number', 'N/A'),
                        "departure_time": first_seg.get('departure', {}).get('at', 'N/A'),
                        "arrival_time": last_seg.get('arrival', {}).get('at', 'N/A'),
                        "duration": itinerary.get('duration', 'N/A'),
                        "stops": len(segments) - 1,
                        "price": f"{price.get('currency', 'USD')} {price.get('total', 'N/A')}"
                    })
        
        return {"status": "success", "flights": flights}
        
    except ResponseError as e:
        logger.error(f"Amadeus error: {e}")
        return {"status": "error", "flights": [], "message": str(e)}
    except Exception as e:
        logger.error(f"Flight search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class FlexibleSearchRequest(BaseModel):
    origin: str
    destination: str
    departure_month: str
    trip_length_days: int = 7
    adults: int = 1

@app.post("/api/flights/flexible")
async def search_flexible_flights(request: FlexibleSearchRequest):
    """Search flexible date flights"""
    try:
        origin = resolve_airport_code(request.origin)
        destination = resolve_airport_code(request.destination)
        
        # Parse month and search multiple dates
        year, month = request.departure_month.split('-')
        results = []
        
        for day in [1, 8, 15, 22]:
            try:
                date = f"{year}-{month}-{day:02d}"
                response = amadeus.shopping.flight_offers_search.get(
                    originLocationCode=origin,
                    destinationLocationCode=destination,
                    departureDate=date,
                    adults=request.adults,
                    max=1
                )
                
                if response.data:
                    price = response.data[0].get('price', {})
                    results.append({
                        "departure_date": date,
                        "return_date": (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=request.trip_length_days)).strftime("%Y-%m-%d"),
                        "price": float(price.get('total', 0)),
                        "currency": price.get('currency', 'USD')
                    })
            except:
                continue
        
        return {
            "status": "success",
            "options": sorted(results, key=lambda x: x['price'])[:5]
        }
        
    except Exception as e:
        logger.error(f"Flexible search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class CheapestDatesRequest(BaseModel):
    origin: str
    destination: str

@app.post("/api/flights/cheapest-dates")
async def search_cheapest_dates(request: CheapestDatesRequest):
    """Find cheapest flight dates"""
    try:
        origin = resolve_airport_code(request.origin)
        destination = resolve_airport_code(request.destination)
        
        # Search next 30, 60, 90 days
        results = []
        base_date = datetime.now()
        
        for days_ahead in [30, 45, 60, 75, 90]:
            try:
                date = (base_date + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
                response = amadeus.shopping.flight_offers_search.get(
                    originLocationCode=origin,
                    destinationLocationCode=destination,
                    departureDate=date,
                    adults=1,
                    max=1
                )
                
                if response.data:
                    price = response.data[0].get('price', {})
                    results.append({
                        "date": date,
                        "price": float(price.get('total', 0)),
                        "currency": price.get('currency', 'USD')
                    })
            except:
                continue
        
        return {
            "status": "success",
            "cheapest_dates": sorted(results, key=lambda x: x['price'])[:3]
        }
        
    except Exception as e:
        logger.error(f"Cheapest dates error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/flights/status")
async def get_flight_status(
    carrier_code: str = Query(...),
    flight_number: str = Query(...),
    scheduled_departure_date: str = Query(...)
):
    """Get flight status"""
    try:
        response = amadeus.schedule.flights.get(
            carrierCode=carrier_code,
            flightNumber=flight_number,
            scheduledDepartureDate=scheduled_departure_date
        )
        
        if response.data:
            flight = response.data[0]
            return {
                "status": "success",
                "flight_status": {
                    "carrier": carrier_code,
                    "number": flight_number,
                    "departure": flight.get('flightPoints', [{}])[0].get('departure', {}),
                    "arrival": flight.get('flightPoints', [{}])[-1].get('arrival', {}),
                    "status": "scheduled"
                }
            }
        
        return {"status": "success", "flight_status": "No data available"}
        
    except Exception as e:
        logger.error(f"Flight status error: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/flights/checkin-links")
async def get_checkin_links(airline_code: str = Query(...)):
    """Get airline check-in links"""
    links = {
        "AA": "https://www.aa.com/checkin",
        "DL": "https://www.delta.com/checkin",
        "UA": "https://www.united.com/checkin",
        "SW": "https://www.southwest.com/checkin",
        "BA": "https://www.britishairways.com/checkin",
        "LH": "https://www.lufthansa.com/checkin",
        "AF": "https://www.airfrance.com/checkin",
        "EK": "https://www.emirates.com/checkin"
    }
    
    return {
        "airline": airline_code,
        "checkin_url": links.get(airline_code.upper(), f"https://www.google.com/search?q={airline_code}+check+in")
    }

# ============= HOTELS =============

@app.post("/api/hotels/search")
async def search_hotels(request: HotelSearchRequest):
    """Search hotels using Amadeus"""
    try:
        response = amadeus.reference_data.locations.hotels.by_city.get(
            cityCode=request.city_code.upper()
        )
        
        hotels = []
        for hotel in response.data[:20]:
            hotels.append({
                "id": hotel.get('hotelId'),
                "name": hotel.get('name'),
                "address": hotel.get('address', {}).get('lines', ['N/A'])[0],
                "distance": hotel.get('distance', {}).get('value', 'N/A'),
                "rating": hotel.get('rating', 'N/A')
            })
        
        return {"status": "success", "hotels": hotels}
        
    except Exception as e:
        logger.error(f"Hotel search error: {e}")
        return {"status": "error", "hotels": [], "message": str(e)}

@app.get("/api/hotels/search")
async def search_hotels_get(
    city_code: str = Query(...),
    check_in_date: str = Query(...),
    check_out_date: str = Query(...)
):
    """Search hotels GET endpoint"""
    request = HotelSearchRequest(
        city_code=city_code,
        check_in_date=check_in_date,
        check_out_date=check_out_date
    )
    return await search_hotels(request)

class HotelSentimentsRequest(BaseModel):
    hotel_ids: List[str]

@app.post("/api/hotels/sentiments")
async def get_hotel_sentiments(request: HotelSentimentsRequest):
    """Get hotel sentiments"""
    try:
        sentiments = []
        for hotel_id in request.hotel_ids[:5]:
            response = amadeus.e_reputation.hotel_sentiments.get(hotelIds=hotel_id)
            
            if response.data:
                sentiment = response.data[0]
                sentiments.append({
                    "hotel_id": hotel_id,
                    "overall_rating": sentiment.get('overallRating', 'N/A'),
                    "total_reviews": sentiment.get('numberOfReviews', 0),
                    "sentiments": sentiment.get('sentiments', {})
                })
        
        return {"status": "success", "sentiments": sentiments}
        
    except Exception as e:
        logger.error(f"Hotel sentiments error: {e}")
        return {"status": "success", "sentiments": []}

# ============= ACTIVITIES =============

@app.post("/api/activities/search")
async def search_activities(request: ActivitySearchRequest):
    """Search activities using Amadeus"""
    try:
        response = amadeus.shopping.activities.get(
            latitude=request.latitude,
            longitude=request.longitude,
            radius=request.radius,
            max=request.max_results
        )
        
        activities = []
        for activity in response.data:
            activities.append({
                "id": activity.get('id'),
                "name": activity.get('name'),
                "description": activity.get('shortDescription', 'N/A'),
                "price": activity.get('price', {}).get('amount', 'N/A'),
                "currency": activity.get('price', {}).get('currencyCode', 'USD'),
                "rating": activity.get('rating', 'N/A'),
                "pictures": activity.get('pictures', [])[:1]
            })
        
        return {"status": "success", "activities": activities}
        
    except Exception as e:
        logger.error(f"Activities search error: {e}")
        return {"status": "success", "activities": []}

@app.get("/api/activities/search")
async def search_activities_get(
    latitude: float = Query(...),
    longitude: float = Query(...),
    radius: int = Query(default=5)
):
    """Search activities GET endpoint"""
    request = ActivitySearchRequest(
        latitude=latitude,
        longitude=longitude,
        radius=radius
    )
    return await search_activities(request)

# ============= ANALYTICS =============

@app.get("/api/analytics/flight-inspiration")
async def get_flight_inspiration(origin: str = Query(...)):
    """Get flight inspiration"""
    try:
        origin = resolve_airport_code(origin)
        response = amadeus.shopping.flight_destinations.get(origin=origin)
        
        destinations = []
        for dest in response.data[:10]:
            destinations.append({
                "destination": dest.get('destination'),
                "departure_date": dest.get('departureDate'),
                "return_date": dest.get('returnDate'),
                "price": f"{dest.get('price', {}).get('total', 'N/A')}"
            })
        
        return {"status": "success", "destinations": destinations}
        
    except Exception as e:
        logger.error(f"Flight inspiration error: {e}")
        return {"status": "error", "destinations": []}

@app.get("/api/analytics/most-traveled")
async def get_most_traveled(
    origin_city_code: str = Query(...),
    period: str = Query(...)
):
    """Get most traveled destinations"""
    try:
        response = amadeus.travel.analytics.air_traffic.traveled.get(
            originCityCode=origin_city_code.upper(),
            period=period
        )
        
        destinations = []
        for item in response.data[:10]:
            destinations.append({
                "destination": item.get('destination'),
                "trips": item.get('analytics', {}).get('travelers', {}).get('score', 0),
                "country": item.get('subType', 'N/A')
            })
        
        return {"status": "success", "destinations": destinations}
        
    except Exception as e:
        logger.error(f"Most traveled error: {e}")
        return {"status": "error", "destinations": []}

@app.get("/api/analytics/most-booked")
async def get_most_booked(
    origin_city_code: str = Query(...),
    period: str = Query(...)
):
    """Get most booked destinations"""
    try:
        response = amadeus.travel.analytics.air_traffic.booked.get(
            originCityCode=origin_city_code.upper(),
            period=period
        )
        
        destinations = []
        for item in response.data[:10]:
            destinations.append({
                "destination": item.get('destination'),
                "bookings": item.get('analytics', {}).get('travelers', {}).get('score', 0)
            })
        
        return {"status": "success", "destinations": destinations}
        
    except Exception as e:
        logger.error(f"Most booked error: {e}")
        return {"status": "error", "destinations": []}

@app.get("/api/analytics/busiest-period")
async def get_busiest_period(
    city_code: str = Query(...),
    period: str = Query(...),
    direction: str = Query(default="ARRIVING")
):
    """Get busiest travel period"""
    try:
        response = amadeus.travel.analytics.air_traffic.busiest_period.get(
            cityCode=city_code.upper(),
            period=period,
            direction=direction
        )
        
        periods = []
        for item in response.data:
            periods.append({
                "period": item.get('period'),
                "travelers": item.get('analytics', {}).get('travelers', {}).get('score', 0)
            })
        
        return {"status": "success", "periods": periods}
        
    except Exception as e:
        logger.error(f"Busiest period error: {e}")
        return {"status": "error", "periods": []}

class FlightDelayRequest(BaseModel):
    origin_airport: str
    destination_airport: str
    departure_date: str
    departure_time: str
    arrival_date: str
    arrival_time: str
    airline_code: str
    flight_number: str
    aircraft_code: str = "321"

@app.post("/api/analytics/flight-delay-prediction")
async def predict_flight_delay(request: FlightDelayRequest):
    """Predict flight delay using Amadeus"""
    try:
        response = amadeus.travel.predictions.flight_delay.get(
            originLocationCode=request.origin_airport.upper(),
            destinationLocationCode=request.destination_airport.upper(),
            departureDate=request.departure_date,
            departureTime=request.departure_time,
            arrivalDate=request.arrival_date,
            arrivalTime=request.arrival_time,
            aircraftCode=request.aircraft_code,
            carrierCode=request.airline_code.upper(),
            flightNumber=request.flight_number,
            duration="PT5H"
        )
        
        if response.data:
            prediction = response.data[0]
            return {
                "status": "success",
                "prediction": {
                    "probability": prediction.get('probability', 'N/A'),
                    "result": prediction.get('result', 'N/A')
                }
            }
        
        return {"status": "success", "prediction": {"probability": "N/A", "result": "No data"}}
        
    except Exception as e:
        logger.error(f"Delay prediction error: {e}")
        return {"status": "error", "prediction": {}}

class TripPurposeRequest(BaseModel):
    origin_airport: str
    destination_airport: str
    departure_date: str
    return_date: str
    search_date: str

@app.post("/api/analytics/trip-purpose-prediction")
async def predict_trip_purpose(request: TripPurposeRequest):
    """Predict trip purpose"""
    try:
        response = amadeus.travel.predictions.trip_purpose.get(
            originLocationCode=request.origin_airport.upper(),
            destinationLocationCode=request.destination_airport.upper(),
            departureDate=request.departure_date,
            returnDate=request.return_date
        )
        
        if response.data:
            return {
                "status": "success",
                "purpose": response.data.get('result', 'LEISURE')
            }
        
        return {"status": "success", "purpose": "LEISURE"}
        
    except Exception as e:
        logger.error(f"Trip purpose error: {e}")
        return {"status": "success", "purpose": "LEISURE"}

@app.get("/api/analytics/airport-routes")
async def get_airport_routes(airport_code: str = Query(...)):
    """Get direct destinations from airport"""
    try:
        response = amadeus.airport.direct_destinations.get(
            departureAirportCode=airport_code.upper()
        )
        
        routes = []
        for dest in response.data[:20]:
            routes.append({
                "destination": dest.get('name'),
                "iataCode": dest.get('iataCode'),
                "type": dest.get('type', 'N/A')
            })
        
        return {"status": "success", "routes": routes}
        
    except Exception as e:
        logger.error(f"Airport routes error: {e}")
        return {"status": "success", "routes": []}

class PriceAnalysisRequest(BaseModel):
    origin: str
    destination: str
    departure_date: str

@app.post("/api/analytics/price-analysis")
async def analyze_prices(request: PriceAnalysisRequest):
    """Analyze flight prices"""
    try:
        origin = resolve_airport_code(request.origin)
        destination = resolve_airport_code(request.destination)
        
        response = amadeus.analytics.itinerary_price_metrics.get(
            originIataCode=origin,
            destinationIataCode=destination,
            departureDate=request.departure_date
        )
        
        if response.data:
            metrics = response.data[0]
            return {
                "status": "success",
                "metrics": {
                    "min": metrics.get('priceMetrics', [{}])[0].get('min', 'N/A'),
                    "max": metrics.get('priceMetrics', [{}])[0].get('max', 'N/A'),
                    "median": metrics.get('priceMetrics', [{}])[0].get('median', 'N/A')
                }
            }
        
        return {"status": "success", "metrics": {}}
        
    except Exception as e:
        logger.error(f"Price analysis error: {e}")
        return {"status": "success", "metrics": {}}

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
    """Master agent trip planning with streaming"""
    logger.info(f"Received trip planning request for {request.destination}")
    logger.debug(f"Full request: {request.dict()}")
    
    async def event_generator():
        agent = MasterTravelAgent()
        try:
            logger.debug("Starting agent stream...")
            async for thought in agent.plan_trip_stream(request):
                # Format as Server-Sent Event
                event_data = json.dumps(thought.dict())
                logger.debug(f"Streaming thought: {thought.action} - {thought.content[:100]}...")
                yield f"data: {event_data}\n\n"
                await asyncio.sleep(0.1)  # Small delay for streaming effect
        except Exception as e:
            logger.error(f"Agent streaming error: {e}", exc_info=True)
            error_thought = AgentThought(
                action=AgentAction.ERROR,
                content=str(e),
                service=None,
                data=None
            )
            yield f"data: {json.dumps(error_thought.dict())}\n\n"
        finally:
            logger.info("Agent stream completed")
            # Send completion signal
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )

@app.post("/api/agent/quick-search")
async def quick_search(request: ChatRequest):
    """Quick search using master agent"""
    agent = MasterTravelAgent()
    try:
        response = await agent.quick_search(request.message)
        return {
            "status": "success",
            "response": response,
            "model": "glm-4.5"
        }
    except Exception as e:
        logger.error(f"Quick search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)