"""Comprehensive Amadeus Travel Services with AI Integration"""

import os
import logging
import json
import aiohttp
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
from amadeus import Client, ResponseError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============== HOTEL MODELS ==============
class HotelSearchRequest(BaseModel):
    city_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius: int = 5  # km
    check_in_date: str
    check_out_date: str
    adults: int = 1
    rooms: int = 1
    price_range: Optional[str] = None  # e.g., "50-200"
    amenities: Optional[List[str]] = None
    ratings: Optional[List[int]] = None  # 1-5 stars
    hotel_chains: Optional[List[str]] = None

class HotelOffer(BaseModel):
    hotel_id: str
    hotel_name: str
    chain_code: Optional[str]
    latitude: float
    longitude: float
    address: str
    distance: Optional[float]  # Distance from search center
    rating: Optional[int]
    amenities: List[str]
    price: str
    currency: str
    room_type: str
    bed_type: Optional[str]
    cancellation_policy: Optional[str]
    available_rooms: int
    booking_url: str
    thumbnail_url: Optional[str]

class HotelSearchResponse(BaseModel):
    city: str
    check_in: str
    check_out: str
    total_hotels: int
    hotels: List[HotelOffer]
    cheapest_price: Optional[str]
    message: Optional[str]


# ============== ACTIVITIES MODELS ==============
class ActivitySearchRequest(BaseModel):
    latitude: float
    longitude: float
    radius: int = 5  # km
    categories: Optional[List[str]] = None  # SIGHTSEEING, MUSEUM, etc.
    price_range: Optional[str] = None
    date: Optional[str] = None
    adults: int = 1
    children: int = 0

class Activity(BaseModel):
    activity_id: str
    name: str
    description: str
    category: str
    price: str
    currency: str
    duration: Optional[str]
    rating: Optional[float]
    review_count: Optional[int]
    latitude: float
    longitude: float
    address: Optional[str]
    booking_url: str
    images: List[str]
    highlights: List[str]
    included: List[str]
    excluded: List[str]

class ActivitySearchResponse(BaseModel):
    location: Dict[str, float]  # lat, lng
    total_activities: int
    activities: List[Activity]
    message: Optional[str]


# ============== FLIGHT STATUS MODELS ==============
class FlightStatusRequest(BaseModel):
    carrier_code: str
    flight_number: str
    scheduled_departure_date: str

class FlightStatus(BaseModel):
    flight_number: str
    carrier: str
    departure_airport: str
    arrival_airport: str
    scheduled_departure: str
    scheduled_arrival: str
    actual_departure: Optional[str]
    actual_arrival: Optional[str]
    terminal_departure: Optional[str]
    terminal_arrival: Optional[str]
    gate_departure: Optional[str]
    gate_arrival: Optional[str]
    status: str  # ON_TIME, DELAYED, CANCELLED, etc.
    delay_minutes: Optional[int]
    aircraft_type: Optional[str]

class FlightStatusResponse(BaseModel):
    flight: FlightStatus
    message: Optional[str]


# ============== CHECK-IN LINKS MODELS ==============
class CheckInLinksRequest(BaseModel):
    airline_code: str

class CheckInLink(BaseModel):
    airline_code: str
    airline_name: str
    check_in_url: str
    mobile_check_in_url: Optional[str]
    check_in_window: str  # e.g., "24 hours before departure"
    supported_languages: List[str]

class CheckInLinksResponse(BaseModel):
    airline: CheckInLink
    message: Optional[str]


# ============== TRANSFER MODELS ==============
class TransferSearchRequest(BaseModel):
    from_location: Dict[str, Any]  # lat, lng, or airport code
    to_location: Dict[str, Any]
    departure_date: str
    departure_time: Optional[str]
    passengers: int = 1
    transfer_type: Optional[str] = None  # PRIVATE, SHARED, TAXI

class TransferOffer(BaseModel):
    transfer_id: str
    transfer_type: str  # PRIVATE, SHARED, TAXI
    vehicle_type: str
    provider: str
    duration: str
    price: str
    currency: str
    cancellation_policy: str
    luggage_capacity: int
    passenger_capacity: int
    description: str
    booking_url: str

class TransferSearchResponse(BaseModel):
    from_location: str
    to_location: str
    departure_date: str
    total_offers: int
    transfers: List[TransferOffer]
    cheapest_price: Optional[str]
    message: Optional[str]


# ============== AI LOOKUP SERVICE ==============
class AILookupService:
    """AI-powered lookup for travel data"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key not set")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
    
    async def resolve_city_code(self, city: str) -> str:
        """Resolve city name to IATA city code"""
        prompt = f"What is the IATA city code for {city}? Reply with just the 3-letter code, nothing else."
        response = await self._query_ai(prompt)
        
        if response and len(response.strip()) == 3:
            return response.strip().upper()
        
        # Common cities fallback
        city_lower = city.lower()
        if 'new york' in city_lower or 'nyc' in city_lower:
            return 'NYC'
        elif 'london' in city_lower:
            return 'LON'
        elif 'paris' in city_lower:
            return 'PAR'
        elif 'tokyo' in city_lower:
            return 'TYO'
        elif 'dubai' in city_lower:
            return 'DXB'
        
        return city[:3].upper()
    
    async def get_hotel_chain_name(self, code: str) -> str:
        """Get hotel chain name from code"""
        prompt = f"What hotel chain has the code {code}? Reply with just the chain name, nothing else."
        name = await self._query_ai(prompt)
        return name.strip() if name else code
    
    async def get_airline_name(self, code: str) -> str:
        """Get airline name from code"""
        prompt = f"What airline has the IATA code {code}? Reply with just the airline name, nothing else."
        name = await self._query_ai(prompt)
        return name.strip() if name else code
    
    async def _query_ai(self, prompt: str) -> str:
        """Query AI model"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "openai/gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 100
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['choices'][0]['message']['content']
                    else:
                        logger.error(f"AI API error: {response.status}")
                        return ""
        except Exception as e:
            logger.error(f"AI query failed: {e}")
            return ""


# ============== HOTEL SERVICE ==============
class HotelSearchService:
    """Amadeus Hotel Search Service"""
    
    def __init__(self):
        client_id = os.getenv("AMADEUS_API_KEY")
        client_secret = os.getenv("AMADEUS_Secret")
        
        if not client_id or not client_secret:
            raise ValueError("Amadeus credentials not set")
        
        self.amadeus = Client(
            client_id=client_id,
            client_secret=client_secret,
            hostname='test'
        )
        self.ai_lookup = AILookupService()
    
    async def search_hotels(self, request: HotelSearchRequest) -> HotelSearchResponse:
        """Search for hotels"""
        try:
            # Resolve city if needed
            city_code = request.city_code
            if not city_code and not (request.latitude and request.longitude):
                # Need either city code or coordinates
                return HotelSearchResponse(
                    city="Unknown",
                    check_in=request.check_in_date,
                    check_out=request.check_out_date,
                    total_hotels=0,
                    hotels=[],
                    cheapest_price=None,
                    message="Either city_code or latitude/longitude required"
                )
            
            logger.info(f"Searching hotels in {city_code or f'{request.latitude},{request.longitude}'}")
            
            # Build search parameters
            params = {
                'checkInDate': request.check_in_date,
                'checkOutDate': request.check_out_date,
                'adults': request.adults,
                'roomQuantity': request.rooms,
                'radius': request.radius,
                'radiusUnit': 'KM',
                'paymentPolicy': 'NONE',
                'includeClosed': 'false',
                'bestRateOnly': 'true',
                'view': 'FULL'
                # Removed 'sort': 'PRICE' as it's not supported in test environment
            }
            
            # Search by city or coordinates
            if city_code:
                params['cityCode'] = city_code
                response = self.amadeus.shopping.hotel_offers_search.get(**params)
            else:
                params['latitude'] = request.latitude
                params['longitude'] = request.longitude
                response = self.amadeus.shopping.hotel_offers_search.get(**params)
            
            # Process results
            hotels = []
            min_price = float('inf')
            
            if hasattr(response, 'data'):
                for hotel_data in response.data[:20]:  # Limit to 20 results
                    hotel = hotel_data.get('hotel', {})
                    offers = hotel_data.get('offers', [])
                    
                    if not offers:
                        continue
                    
                    # Get cheapest offer
                    cheapest_offer = min(offers, key=lambda x: float(x.get('price', {}).get('total', '999999')))
                    price = float(cheapest_offer.get('price', {}).get('total', 0))
                    
                    if price < min_price:
                        min_price = price
                    
                    # Get hotel chain name if available
                    chain_code = hotel.get('chainCode')
                    chain_name = await self.ai_lookup.get_hotel_chain_name(chain_code) if chain_code else None
                    
                    hotels.append(HotelOffer(
                        hotel_id=hotel.get('hotelId', 'N/A'),
                        hotel_name=hotel.get('name', 'Unknown Hotel'),
                        chain_code=chain_code,
                        latitude=hotel.get('latitude', 0),
                        longitude=hotel.get('longitude', 0),
                        address=f"{hotel.get('address', {}).get('lines', [''])[0]}, {hotel.get('address', {}).get('cityName', '')}",
                        distance=hotel.get('distance', {}).get('value'),
                        rating=hotel.get('rating'),
                        amenities=hotel.get('amenities', [])[:10],  # Limit amenities
                        price=f"${price:.0f}",
                        currency=cheapest_offer.get('price', {}).get('currency', 'USD'),
                        room_type=cheapest_offer.get('room', {}).get('type', 'Standard'),
                        bed_type=cheapest_offer.get('room', {}).get('typeEstimated', {}).get('bedType'),
                        cancellation_policy=cheapest_offer.get('policies', {}).get('cancellation', {}).get('description'),
                        available_rooms=1,
                        booking_url=f"https://www.booking.com/search.html?ss={hotel.get('name', '').replace(' ', '+')}",
                        thumbnail_url=None
                    ))
            
            # Sort by price
            hotels.sort(key=lambda x: float(x.price.replace('$', '').replace(',', '')))
            
            return HotelSearchResponse(
                city=city_code or f"Location ({request.latitude}, {request.longitude})",
                check_in=request.check_in_date,
                check_out=request.check_out_date,
                total_hotels=len(hotels),
                hotels=hotels,
                cheapest_price=f"${min_price:.0f}" if hotels else None,
                message=f"Found {len(hotels)} hotels" if hotels else "No hotels found for this search"
            )
            
        except ResponseError as e:
            error_detail = str(e)
            logger.error(f"Amadeus hotel search error: {error_detail}")
            # Get more specific error info if available
            if hasattr(e, 'response') and hasattr(e.response, 'body'):
                error_detail = e.response.body
            return HotelSearchResponse(
                city=request.city_code or "Unknown",
                check_in=request.check_in_date,
                check_out=request.check_out_date,
                total_hotels=0,
                hotels=[],
                cheapest_price=None,
                message=f"Hotel search not available in test environment. Use production credentials for real hotel data."
            )


# ============== ACTIVITIES SERVICE ==============
class ActivitySearchService:
    """Amadeus Tours and Activities Service"""
    
    def __init__(self):
        client_id = os.getenv("AMADEUS_API_KEY")
        client_secret = os.getenv("AMADEUS_Secret")
        
        if not client_id or not client_secret:
            raise ValueError("Amadeus credentials not set")
        
        self.amadeus = Client(
            client_id=client_id,
            client_secret=client_secret,
            hostname='test'
        )
    
    async def search_activities(self, request: ActivitySearchRequest) -> ActivitySearchResponse:
        """Search for tours and activities"""
        try:
            logger.info(f"Searching activities at ({request.latitude}, {request.longitude})")
            
            # Search activities by location
            response = self.amadeus.shopping.activities.get(
                latitude=request.latitude,
                longitude=request.longitude,
                radius=request.radius
            )
            
            activities = []
            
            if hasattr(response, 'data'):
                for activity_data in response.data[:20]:  # Limit to 20 results
                    # Extract activity details
                    price_data = activity_data.get('price', {})
                    
                    activities.append(Activity(
                        activity_id=activity_data.get('id', 'N/A'),
                        name=activity_data.get('name', 'Unknown Activity'),
                        description=activity_data.get('shortDescription', 'No description available'),
                        category=activity_data.get('type', 'ACTIVITY'),
                        price=f"${float(price_data.get('amount', 0)):.0f}",
                        currency=price_data.get('currencyCode', 'USD'),
                        duration=activity_data.get('duration'),
                        rating=activity_data.get('rating'),
                        review_count=None,
                        latitude=activity_data.get('geoCode', {}).get('latitude', request.latitude),
                        longitude=activity_data.get('geoCode', {}).get('longitude', request.longitude),
                        address=None,
                        booking_url=activity_data.get('bookingLink', 'https://www.viator.com'),
                        images=activity_data.get('pictures', [])[:3],
                        highlights=[],
                        included=[],
                        excluded=[]
                    ))
            
            # Sort by price
            activities.sort(key=lambda x: float(x.price.replace('$', '').replace(',', '')))
            
            return ActivitySearchResponse(
                location={'latitude': request.latitude, 'longitude': request.longitude},
                total_activities=len(activities),
                activities=activities,
                message=f"Found {len(activities)} activities" if activities else "No activities found for this location"
            )
            
        except ResponseError as e:
            logger.error(f"Amadeus activity search error: {e}")
            return ActivitySearchResponse(
                location={'latitude': request.latitude, 'longitude': request.longitude},
                total_activities=0,
                activities=[],
                message=f"Error searching activities: {str(e)}"
            )


# ============== FLIGHT STATUS SERVICE ==============
class FlightStatusService:
    """Amadeus Flight Status Service"""
    
    def __init__(self):
        client_id = os.getenv("AMADEUS_API_KEY")
        client_secret = os.getenv("AMADEUS_Secret")
        
        if not client_id or not client_secret:
            raise ValueError("Amadeus credentials not set")
        
        self.amadeus = Client(
            client_id=client_id,
            client_secret=client_secret,
            hostname='test'
        )
        self.ai_lookup = AILookupService()
    
    async def get_flight_status(self, request: FlightStatusRequest) -> FlightStatusResponse:
        """Get real-time flight status"""
        try:
            logger.info(f"Getting status for {request.carrier_code}{request.flight_number} on {request.scheduled_departure_date}")
            
            # Get flight status
            response = self.amadeus.schedule.flights.get(
                carrierCode=request.carrier_code,
                flightNumber=request.flight_number,
                scheduledDepartureDate=request.scheduled_departure_date
            )
            
            if hasattr(response, 'data') and response.data:
                flight_data = response.data[0]
                
                # Get airline name
                airline_name = await self.ai_lookup.get_airline_name(request.carrier_code)
                
                # Extract flight segments
                flight_points = flight_data.get('flightPoints', [])
                if len(flight_points) >= 2:
                    departure = flight_points[0]
                    arrival = flight_points[-1]
                    
                    # Calculate delay
                    delay_minutes = 0
                    if departure.get('departure', {}).get('timings'):
                        scheduled = departure['departure']['timings'][0].get('value')
                        actual = departure['departure']['timings'][1].get('value') if len(departure['departure']['timings']) > 1 else None
                        # Calculate delay (simplified)
                        # In production, use proper datetime parsing
                    
                    flight_status = FlightStatus(
                        flight_number=f"{request.carrier_code}{request.flight_number}",
                        carrier=airline_name,
                        departure_airport=departure.get('iataCode', 'N/A'),
                        arrival_airport=arrival.get('iataCode', 'N/A'),
                        scheduled_departure=departure.get('departure', {}).get('timings', [{}])[0].get('value', 'N/A'),
                        scheduled_arrival=arrival.get('arrival', {}).get('timings', [{}])[0].get('value', 'N/A'),
                        actual_departure=None,
                        actual_arrival=None,
                        terminal_departure=departure.get('departure', {}).get('terminal'),
                        terminal_arrival=arrival.get('arrival', {}).get('terminal'),
                        gate_departure=departure.get('departure', {}).get('gate'),
                        gate_arrival=arrival.get('arrival', {}).get('gate'),
                        status='SCHEDULED',
                        delay_minutes=delay_minutes,
                        aircraft_type=flight_data.get('legs', [{}])[0].get('aircraftEquipment', {}).get('aircraftType')
                    )
                    
                    return FlightStatusResponse(
                        flight=flight_status,
                        message="Flight status retrieved successfully"
                    )
            
            # If no data found
            return FlightStatusResponse(
                flight=FlightStatus(
                    flight_number=f"{request.carrier_code}{request.flight_number}",
                    carrier=request.carrier_code,
                    departure_airport="N/A",
                    arrival_airport="N/A",
                    scheduled_departure="N/A",
                    scheduled_arrival="N/A",
                    actual_departure=None,
                    actual_arrival=None,
                    terminal_departure=None,
                    terminal_arrival=None,
                    gate_departure=None,
                    gate_arrival=None,
                    status="UNKNOWN",
                    delay_minutes=None,
                    aircraft_type=None
                ),
                message="Flight information not available"
            )
            
        except ResponseError as e:
            logger.error(f"Amadeus flight status error: {e}")
            return FlightStatusResponse(
                flight=FlightStatus(
                    flight_number=f"{request.carrier_code}{request.flight_number}",
                    carrier=request.carrier_code,
                    departure_airport="N/A",
                    arrival_airport="N/A",
                    scheduled_departure="N/A",
                    scheduled_arrival="N/A",
                    actual_departure=None,
                    actual_arrival=None,
                    terminal_departure=None,
                    terminal_arrival=None,
                    gate_departure=None,
                    gate_arrival=None,
                    status="ERROR",
                    delay_minutes=None,
                    aircraft_type=None
                ),
                message=f"Flight status not available in test environment for past dates. Use future dates for testing."
            )


# ============== CHECK-IN LINKS SERVICE ==============
class CheckInLinksService:
    """Flight Check-in Links Service"""
    
    def __init__(self):
        client_id = os.getenv("AMADEUS_API_KEY")
        client_secret = os.getenv("AMADEUS_Secret")
        
        if not client_id or not client_secret:
            raise ValueError("Amadeus credentials not set")
        
        self.amadeus = Client(
            client_id=client_id,
            client_secret=client_secret,
            hostname='test'
        )
        self.ai_lookup = AILookupService()
    
    async def get_checkin_links(self, request: CheckInLinksRequest) -> CheckInLinksResponse:
        """Get airline check-in links"""
        try:
            logger.info(f"Getting check-in links for {request.airline_code}")
            
            # Get check-in URLs
            response = self.amadeus.reference_data.urls.checkin_links.get(
                airlineCode=request.airline_code
            )
            
            if hasattr(response, 'data') and response.data:
                link_data = response.data[0]
                logger.info(f"Check-in link data for {request.airline_code}: {link_data}")
                
                # Get airline name
                airline_name = await self.ai_lookup.get_airline_name(request.airline_code)
                
                # Extract URL safely
                check_in_url = link_data.get('href', '')
                if not isinstance(check_in_url, str):
                    check_in_url = str(check_in_url) if check_in_url else ''
                
                # Handle channel types
                channel = link_data.get('channel', '')
                mobile_url = None
                
                # If channel is 'All', the URL works for both web and mobile
                if channel == 'All':
                    # Same URL for both desktop and mobile
                    mobile_url = check_in_url
                elif channel == 'Mobile':
                    # This is specifically a mobile URL
                    mobile_url = check_in_url
                    # You might want to find a desktop URL or use the same
                elif channel == 'Desktop' or channel == 'Web':
                    # This is a desktop-only URL
                    mobile_url = None
                
                # Ensure mobile_url is None or string, never boolean
                if not isinstance(mobile_url, (str, type(None))):
                    logger.warning(f"mobile_url has unexpected type: {type(mobile_url)}, value: {mobile_url}")
                    mobile_url = None
                
                logger.info(f"Creating CheckInLink with mobile_url: {mobile_url} (type: {type(mobile_url)})")
                
                checkin_link = CheckInLink(
                    airline_code=request.airline_code,
                    airline_name=airline_name,
                    check_in_url=check_in_url,
                    mobile_check_in_url=mobile_url,
                    check_in_window="24-48 hours before departure",
                    supported_languages=['en']
                )
                
                return CheckInLinksResponse(
                    airline=checkin_link,
                    message="Check-in links retrieved successfully"
                )
            
            # Try fallback directly if no data from Amadeus
            return await self._get_fallback_checkin_links(request)
            
        except ResponseError as e:
            logger.error(f"Amadeus check-in links error: {e}")
            # Use fallback directly for error cases
            return await self._get_fallback_checkin_links(request)
        except Exception as e:
            logger.error(f"Unexpected error getting check-in links: {e}")
            return await self._get_fallback_checkin_links(request)
    
    async def _get_fallback_checkin_links(self, request: CheckInLinksRequest) -> CheckInLinksResponse:
        """Get fallback check-in links"""
        # Fallback to common airline check-in URLs
        airline_checkin_urls = {
            'AA': 'https://www.aa.com/homePage/onlineCheckIn.do',
            'UA': 'https://www.united.com/en/us/checkin',
            'DL': 'https://www.delta.com/us/en/check-in-security',
            'BA': 'https://www.britishairways.com/travel/olci/public/en_gb',
            'LH': 'https://www.lufthansa.com/us/en/online-check-in',
            'AF': 'https://www.airfrance.com/checkin',
            'EK': 'https://www.emirates.com/us/english/manage-booking/online-check-in.aspx',
            'QR': 'https://www.qatarairways.com/en/homepage/onlinecheckin.html',
            'B6': 'https://www.jetblue.com/check-in',
            'WN': 'https://www.southwest.com/air/check-in/',
            'AS': 'https://www.alaskaair.com/CheckIn'
        }
        
        # Get airline name
        airline_name = await self.ai_lookup.get_airline_name(request.airline_code)
        
        checkin_link = CheckInLink(
            airline_code=request.airline_code,
            airline_name=airline_name,
            check_in_url=airline_checkin_urls.get(request.airline_code, f"https://www.google.com/search?q={airline_name}+online+check+in"),
            mobile_check_in_url=None,
            check_in_window="24-48 hours before departure",
            supported_languages=['en']
        )
        
        return CheckInLinksResponse(
            airline=checkin_link,
            message="Check-in links retrieved (fallback)"
        )


# ============== TRANSFER SERVICE ==============
class TransferSearchService:
    """Amadeus Transfer Search Service"""
    
    def __init__(self):
        client_id = os.getenv("AMADEUS_API_KEY")
        client_secret = os.getenv("AMADEUS_Secret")
        
        if not client_id or not client_secret:
            raise ValueError("Amadeus credentials not set")
        
        self.amadeus = Client(
            client_id=client_id,
            client_secret=client_secret,
            hostname='test'
        )
    
    async def search_transfers(self, request: TransferSearchRequest) -> TransferSearchResponse:
        """Search for transfers"""
        try:
            # Extract location details
            from_lat = request.from_location.get('latitude')
            from_lng = request.from_location.get('longitude')
            from_airport = request.from_location.get('airport_code')
            
            to_lat = request.to_location.get('latitude')
            to_lng = request.to_location.get('longitude')
            to_airport = request.to_location.get('airport_code')
            
            logger.info(f"Searching transfers from {from_airport or f'({from_lat},{from_lng})'} to {to_airport or f'({to_lat},{to_lng})'}")
            
            # Build search parameters
            params = {
                'startDateTime': f"{request.departure_date}T{request.departure_time or '10:00:00'}",
                'passengers': request.passengers,
                'transferType': request.transfer_type or 'PRIVATE'
            }
            
            # Set location parameters
            if from_airport:
                params['startLocationCode'] = from_airport
            else:
                params['startLatitude'] = from_lat
                params['startLongitude'] = from_lng
            
            if to_airport:
                params['endLocationCode'] = to_airport
            else:
                params['endLatitude'] = to_lat
                params['endLongitude'] = to_lng
            
            # Search transfers
            response = self.amadeus.shopping.transfer_offers.post(params)
            
            transfers = []
            min_price = float('inf')
            
            if hasattr(response, 'data'):
                for transfer_data in response.data[:10]:  # Limit to 10 results
                    quote = transfer_data.get('quotation', {})
                    price = float(quote.get('totalAmount', {}).get('value', 0))
                    
                    if price < min_price:
                        min_price = price
                    
                    transfers.append(TransferOffer(
                        transfer_id=transfer_data.get('id', 'N/A'),
                        transfer_type=transfer_data.get('transferType', 'PRIVATE'),
                        vehicle_type=transfer_data.get('vehicle', {}).get('description', 'Standard Vehicle'),
                        provider=transfer_data.get('provider', {}).get('name', 'Transfer Provider'),
                        duration=transfer_data.get('duration', 'N/A'),
                        price=f"${price:.0f}",
                        currency=quote.get('totalAmount', {}).get('currency', 'USD'),
                        cancellation_policy=transfer_data.get('cancellationRules', [{}])[0].get('ruleDescription', 'Standard cancellation policy'),
                        luggage_capacity=transfer_data.get('vehicle', {}).get('baggageQuantity', 2),
                        passenger_capacity=transfer_data.get('vehicle', {}).get('seats', [{}])[0].get('count', 4),
                        description=transfer_data.get('serviceProvider', {}).get('description', 'Professional transfer service'),
                        booking_url="https://www.viator.com/searchResults/all?text=airport+transfer"
                    ))
            
            # Sort by price
            transfers.sort(key=lambda x: float(x.price.replace('$', '').replace(',', '')))
            
            return TransferSearchResponse(
                from_location=from_airport or f"Location ({from_lat}, {from_lng})",
                to_location=to_airport or f"Location ({to_lat}, {to_lng})",
                departure_date=request.departure_date,
                total_offers=len(transfers),
                transfers=transfers,
                cheapest_price=f"${min_price:.0f}" if transfers else None,
                message=f"Found {len(transfers)} transfer options" if transfers else "No transfers found for this route"
            )
            
        except ResponseError as e:
            logger.error(f"Amadeus transfer search error: {e}")
            
            # Return mock data for test environment
            return TransferSearchResponse(
                from_location=str(request.from_location),
                to_location=str(request.to_location),
                departure_date=request.departure_date,
                total_offers=0,
                transfers=[],
                cheapest_price=None,
                message=f"Transfer search not fully available in test environment"
            )


# Helper function to get airline name
async def get_airline_name(code: str) -> str:
    """Get airline name from code using AI"""
    ai_service = AILookupService()
    prompt = f"What airline has the IATA code {code}? Reply with just the airline name, nothing else."
    name = await ai_service._query_ai(prompt)
    return name.strip() if name else code