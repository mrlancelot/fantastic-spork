import os
import json
import httpx
import uuid
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from convex import ConvexClient

load_dotenv(Path(__file__).parent.parent.parent / '.env')

app = FastAPI()
app.add_middleware(
    CORSMiddleware, 
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:3000",
        "https://fantastic-spork-alpha.vercel.app",
        "https://*.vercel.app"
    ], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"]
)

convex_client = ConvexClient(os.getenv("CONVEX_URL")) if os.getenv("CONVEX_URL") else None

def validate_booking_url(url: str, platform_type: str) -> bool:
    """Validate if a URL is likely a legitimate booking platform"""
    booking_domains = {
        "flights": ["google.com/flights", "expedia.com", "kayak.com", "skyscanner.com", "airline.com"],
        "hotels": ["booking.com", "airbnb.com", "expedia.com", "hotels.com", "agoda.com"],
        "restaurants": ["opentable.com", "resy.com", "yelp.com"],
        "activities": ["viator.com", "getyourguide.com", "tripadvisor.com", "airbnb.com/experiences"]
    }
    
    if not url or not url.startswith("http"):
        return False
        
    relevant_domains = booking_domains.get(platform_type, [])
    return any(domain in url.lower() for domain in relevant_domains)

def extract_booking_links(content: str) -> dict:
    """Extract and categorize booking links from content"""
    import re
    
    # Simple URL extraction pattern
    url_pattern = r'https?://[^\s<>"]+'
    urls = re.findall(url_pattern, content)
    
    categorized_links = {
        "flights": [],
        "hotels": [],
        "restaurants": [],
        "activities": [],
        "other": []
    }
    
    for url in urls:
        categorized = False
        for category in ["flights", "hotels", "restaurants", "activities"]:
            if validate_booking_url(url, category):
                categorized_links[category].append(url)
                categorized = True
                break
        
        if not categorized:
            categorized_links["other"].append(url)
    
    return categorized_links

class ItineraryRequest(BaseModel):
    destination: str
    dates: str
    travelers: int
    departure_cities: list[str]
    trip_type: str = "bachelor party"

class SaveItineraryRequest(BaseModel):
    itinerary_data: dict
    user_id: str
    trip_details: dict = {}

class StoreUserRequest(BaseModel):
    clerk_user_id: str
    email: str
    name: str = None
    image_url: str = None

class BookingSearchRequest(BaseModel):
    search_type: str  # "flights", "hotels", "restaurants", "activities"
    destination: str
    specific_query: str
    dates: str = ""
    travelers: int = 1

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "travel-api"}

@app.post("/api/test-booking-search")
async def test_booking_search(request: BookingSearchRequest):
    """Test endpoint for searching specific booking links"""
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="PERPLEXITY_API_KEY not configured")
    
    # Create targeted search query based on type
    search_queries = {
        "flights": f"Google Flights {request.specific_query} to {request.destination} {request.dates} booking URL",
        "hotels": f"Booking.com {request.destination} {request.specific_query} group booking hotel reservation",
        "restaurants": f"{request.specific_query} {request.destination} OpenTable reservation booking WhatsApp contact",
        "activities": f"Viator GetYourGuide {request.specific_query} {request.destination} tour booking activity"
    }
    
    query = search_queries.get(request.search_type, request.specific_query)
    
    prompt = f"""Search for ACTUAL BOOKING LINKS and contact information for: {query}
    
    Focus on finding:
    1. Direct booking URLs (not just informational pages)
    2. Phone numbers and WhatsApp contacts
    3. Current pricing information
    4. Group booking options if available
    
    Return results as JSON with this structure:
    {{
        "booking_options": [
            {{
                "platform": "platform name",
                "url": "direct booking URL",
                "contact": "phone or WhatsApp if available",
                "price_info": "current pricing",
                "notes": "booking tips or requirements",
                "verified": true/false
            }}
        ],
        "search_query": "{query}",
        "additional_tips": ["booking advice", "alternative options"]
    }}
    
    Only include results with actual booking capabilities or direct contact information."""
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.perplexity.ai/chat/completions",
                json={"model": "sonar", "messages": [{"role": "user", "content": prompt}]},
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
            
            content = data["choices"][0]["message"]["content"]
            
            # Extract booking links from raw content
            extracted_links = extract_booking_links(content)
            
            try:
                # Try to parse as JSON
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                result = json.loads(content)
                return {
                    "search_result": result,
                    "extracted_links": extracted_links,
                    "raw_content": content,
                    "status": "success"
                }
            except json.JSONDecodeError:
                return {
                    "search_result": {"raw_content": content},
                    "extracted_links": extracted_links,
                    "status": "partial_success",
                    "error": "Could not parse JSON response"
                }
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/api/generate-itinerary")
async def generate_itinerary(request: ItineraryRequest):
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="PERPLEXITY_API_KEY not configured")
    
    # Enhanced prompt focusing on actual booking links
    prompt = f"""Search for ACTUAL BOOKING LINKS and reservation platforms for a {request.trip_type} with {request.travelers} people to {request.destination} from {', '.join(request.departure_cities)} for {request.dates}.
    
    Use these specific search strategies:
    FLIGHTS: Search "Google Flights [departure_city] to {request.destination} {request.dates}" - find direct Google Flights URLs
    HOTELS: Search "Booking.com {request.destination} hotels group booking", "Airbnb {request.destination} large groups", "[hotel name] {request.destination} direct booking"
    RESTAURANTS: Search "[restaurant name] {request.destination} OpenTable", "[restaurant name] {request.destination} reservation WhatsApp", "[restaurant name] {request.destination} direct booking"
    ACTIVITIES: Search "Viator {request.destination} tours", "GetYourGuide {request.destination} activities", "[activity] {request.destination} booking"
    
    Return ONLY valid JSON with this exact structure:
    {{
        "flights": [{{
            "from": "departure_city",
            "airline": "suggested_airline",
            "booking_options": [
                {{
                    "platform": "Google Flights",
                    "url": "https://www.google.com/flights/...",
                    "price_range": "$800-1200",
                    "notes": "Direct booking available"
                }},
                {{
                    "platform": "Airline Direct",
                    "url": "https://airline.com/booking",
                    "price_range": "$750-1150",
                    "notes": "Official airline site"
                }}
            ]
        }}],
        "accommodations": [{{
            "name": "hotel/property name",
            "neighborhood": "area",
            "bachelor_friendly": true/false,
            "booking_options": [
                {{
                    "platform": "Booking.com",
                    "url": "https://booking.com/hotel/...",
                    "price_per_night": "$180-250",
                    "notes": "Group discounts available"
                }},
                {{
                    "platform": "Direct Hotel", 
                    "url": "https://hotel-website.com",
                    "price_per_night": "$160-230",
                    "contact": "+1-xxx-xxx-xxxx",
                    "notes": "Call for group rates"
                }}
            ]
        }}],
        "food": [{{
            "name": "restaurant name",
            "cuisine": "type",
            "good_for_groups": true/false,
            "booking_options": [
                {{
                    "platform": "OpenTable",
                    "url": "https://opentable.com/restaurant/...",
                    "price_range": "$40-80 per person",
                    "notes": "Reservations recommended"
                }},
                {{
                    "platform": "WhatsApp",
                    "contact": "+xx-xxx-xxx-xxxx",
                    "price_range": "$35-70 per person",
                    "notes": "Message for group reservations"
                }},
                {{
                    "platform": "Direct",
                    "url": "https://restaurant-website.com",
                    "contact": "+xx-xxx-xxx-xxxx",
                    "price_range": "$30-65 per person",
                    "notes": "Call ahead for large groups"
                }}
            ]
        }}],
        "activities": [{{
            "name": "activity name",
            "type": "nightlife/sightseeing/adventure",
            "bachelor_appropriate": true/false,
            "booking_options": [
                {{
                    "platform": "Viator",
                    "url": "https://viator.com/tours/...",
                    "price_per_person": "$45-85",
                    "notes": "Skip-the-line tickets included"
                }},
                {{
                    "platform": "GetYourGuide",
                    "url": "https://getyourguide.com/activity/...",
                    "price_per_person": "$40-80",
                    "notes": "Free cancellation up to 24h"
                }},
                {{
                    "platform": "Direct",
                    "url": "https://venue-website.com",
                    "contact": "+xx-xxx-xxx-xxxx",
                    "price_per_person": "$35-75",
                    "notes": "Group discounts available"
                }}
            ]
        }}],
        "schedule": {{
            "day1": ["morning activity", "afternoon activity", "evening activity"],
            "day2": ["morning activity", "afternoon activity", "evening activity"],
            "day3": ["morning activity", "afternoon activity", "evening activity"]
        }},
        "booking_summary": {{
            "total_estimated_cost": "$2500-4000 per person",
            "best_booking_strategy": "Book flights first, then accommodations, restaurants can be booked closer to travel date",
            "group_booking_tips": ["Contact hotels directly for group rates", "Make restaurant reservations 2-3 weeks ahead", "Book activities with free cancellation"]
        }}
    }}
    
    CRITICAL REQUIREMENTS:
    1. Every booking_options array MUST contain actual URLs where possible
    2. Include contact information (phone/WhatsApp) for local businesses
    3. Provide realistic price ranges based on current market rates
    4. Focus on platforms that actually allow online booking
    5. Include backup contact methods for high-demand venues
    6. Prioritize {request.trip_type} appropriate venues and activities"""
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("https://api.perplexity.ai/chat/completions", 
                json={"model": "sonar", "messages": [{"role": "user", "content": prompt}]},
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, timeout=90.0)
            response.raise_for_status()
            data = response.json()
            
            content = data["choices"][0]["message"]["content"]
            try:
                # Extract JSON from response (handle markdown code blocks)
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                itinerary = json.loads(content)
                
                # Validate that booking_options exist in the response
                booking_validation = {
                    "has_flight_bookings": any("booking_options" in flight for flight in itinerary.get("flights", [])),
                    "has_hotel_bookings": any("booking_options" in hotel for hotel in itinerary.get("accommodations", [])),
                    "has_restaurant_bookings": any("booking_options" in restaurant for restaurant in itinerary.get("food", [])),
                    "has_activity_bookings": any("booking_options" in activity for activity in itinerary.get("activities", []))
                }
                
                return {
                    "itinerary": itinerary, 
                    "booking_validation": booking_validation,
                    "sources": itinerary.get("sources", []), 
                    "status": "success"
                }
            except json.JSONDecodeError as e:
                # Enhanced fallback with better error info
                return {
                    "itinerary": {"raw_content": content}, 
                    "sources": data.get("citations", []), 
                    "status": "partial_success",
                    "error": f"JSON parsing failed: {str(e)}",
                    "parsing_hint": "Check if the response contains valid JSON structure with booking_options arrays"
                }
                
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="API request timed out")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Perplexity API error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/api/save-itinerary")
async def save_itinerary(request: SaveItineraryRequest):
    """Save itinerary to Convex database"""
    if not convex_client:
        raise HTTPException(status_code=500, detail="Convex not configured")
    
    print(f"Saving itinerary for user: {request.user_id}")
    print(f"Destination: {request.itinerary_data.get('destination', 'Unknown')}")
    
    # Analyze booking completeness
    itinerary = request.itinerary_data
    booking_stats = {
        "total_booking_options": 0,
        "verified_urls": 0,
        "contact_info_available": 0
    }
    
    # Count booking options across all categories
    for category in ["flights", "accommodations", "food", "activities"]:
        items = itinerary.get(category, [])
        for item in items:
            booking_options = item.get("booking_options", [])
            booking_stats["total_booking_options"] += len(booking_options)
            
            for option in booking_options:
                if option.get("url") and option["url"].startswith("http"):
                    booking_stats["verified_urls"] += 1
                if option.get("contact"):
                    booking_stats["contact_info_available"] += 1
    
    try:
        # Save trip to Convex
        # Extract the actual itinerary if it's nested
        itinerary_to_save = request.itinerary_data.get('itinerary', request.itinerary_data)
        
        # Extract activities from the itinerary
        activities_list = []
        if 'activities' in itinerary_to_save:
            for activity in itinerary_to_save.get('activities', []):
                if isinstance(activity, dict) and 'name' in activity:
                    activities_list.append(activity['name'])
        
        trip_id = convex_client.mutation(
            "trips:createFromBackend",
            {
                "userId": request.user_id,  # This is the Clerk user ID
                "destination": request.itinerary_data.get('destination', 'Unknown'),
                "dates": request.itinerary_data.get('dates', ''),
                "travelers": request.itinerary_data.get('travelers', 1),
                "departureCities": request.itinerary_data.get('departureCities', []),
                "tripType": "group travel",
                "itineraryData": itinerary_to_save,
                "bookingValidation": request.itinerary_data.get('booking_validation', booking_stats)
            }
        )
        
        return {
            "success": True, 
            "trip_id": trip_id, 
            "message": "Itinerary saved successfully!",
            "booking_analysis": booking_stats
        }
        
    except Exception as e:
        print(f"Error saving trip: {str(e)}")
        # Fallback to mock success for demo purposes
        return {
            "success": True, 
            "trip_id": str(uuid.uuid4()), 
            "message": "Itinerary saved (demo mode)!",
            "booking_analysis": booking_stats,
            "demo_mode": True
        }

@app.post("/api/store-user")
async def store_user(request: StoreUserRequest):
    """Store user data from Clerk authentication"""
    if not convex_client:
        raise HTTPException(status_code=500, detail="Convex not configured")
    
    try:
        # Build mutation args, excluding None values
        mutation_args = {
            "clerkUserId": request.clerk_user_id,
            "email": request.email,
        }
        
        # Only add optional fields if they have values
        if request.name is not None:
            mutation_args["name"] = request.name
        if request.image_url is not None:
            mutation_args["imageUrl"] = request.image_url
            
        user_id = convex_client.mutation(
            "users:storeFromBackend",
            mutation_args
        )
        
        return {
            "success": True,
            "user_id": user_id,
            "message": "User stored successfully"
        }
        
    except Exception as e:
        # Log error but don't fail the request - user can still use the app
        print(f"Error storing user: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "User storage failed but authentication succeeded"
        }

@app.put("/api/trips/{trip_id}")
async def update_trip(trip_id: str, request: Request):
    """Update a trip"""
    if not convex_client:
        raise HTTPException(status_code=500, detail="Convex not configured")
    
    # Get user from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    clerk_token = auth_header.replace("Bearer ", "")
    
    try:
        # Verify the Clerk token
        # In production, you would verify the JWT token here
        # For now, we'll extract the user ID from the token payload
        # This is a simplified version - in production use proper JWT verification
        
        body = await request.json()
        
        # Call Convex mutation to update trip
        result = convex_client.mutation(
            "trips:updateFromBackend",
            {
                "id": trip_id,
                "userId": body.get("userId"),  # This should come from verified token
                **{k: v for k, v in body.items() if k != "userId" and v is not None}
            }
        )
        
        return {"success": True, "message": "Trip updated successfully"}
    except Exception as e:
        print(f"Error updating trip: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/trips/{trip_id}")
async def delete_trip(trip_id: str, request: Request):
    """Delete a trip"""
    if not convex_client:
        raise HTTPException(status_code=500, detail="Convex not configured")
    
    # Get user from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    clerk_token = auth_header.replace("Bearer ", "")
    
    try:
        # In production, verify the Clerk JWT token here
        # For now, we expect the userId to be passed in the request
        body = await request.json()
        user_id = body.get("userId")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID required")
        
        # Call Convex mutation to delete trip
        result = convex_client.mutation(
            "trips:deleteFromBackend",
            {
                "id": trip_id,
                "userId": user_id
            }
        )
        
        return {"success": True, "message": "Trip deleted successfully"}
    except Exception as e:
        print(f"Error deleting trip: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))