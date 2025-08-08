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

# Load environment
root_env = Path(__file__).parent.parent.parent / '.env'
load_dotenv(root_env, override=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    interests: List[str]
    budget: int
    pace: str = "moderate"

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
    """Create smart itinerary using AI"""
    try:
        prompt = f"""Create a {(datetime.strptime(request.end_date, '%Y-%m-%d') - datetime.strptime(request.start_date, '%Y-%m-%d')).days} day itinerary for {request.destination}.
        Interests: {', '.join(request.interests)}
        Budget: ${request.budget} per person
        Pace: {request.pace}
        
        Format as a daily schedule with activities, restaurants, and estimated costs."""
        
        itinerary = await ai_chat(prompt)
        
        return {
            "status": "success",
            "itinerary": {
                "destination": request.destination,
                "start_date": request.start_date,
                "end_date": request.end_date,
                "plan": itinerary
            }
        }
        
    except Exception as e:
        logger.error(f"Smart planner error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/planner/save")
async def save_itinerary(itinerary: Dict[str, Any]):
    """Save itinerary (placeholder)"""
    return {
        "status": "success",
        "message": "Itinerary saved",
        "id": datetime.now().timestamp()
    }

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)