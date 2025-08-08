"""Amadeus Flight Search Service with AI Lookups"""

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

# Models
class FlightSearchRequest(BaseModel):
    origin: str
    destination: str
    departure_date: str
    return_date: Optional[str] = None
    trip_type: str = "one-way"
    adults: int = 1
    children: int = 0
    seat_class: str = "economy"

class FlexibleSearchRequest(BaseModel):
    origin: str
    destination: str
    departure_month: str
    trip_length_days: int = 7
    adults: int = 1
    seat_class: str = "economy"
    max_searches: int = 5

class CheapestDateSearchRequest(BaseModel):
    origin: str
    destination: str
    departure_date: Optional[str] = None  # If provided, search around this date
    one_way: bool = False
    duration: Optional[int] = None  # Trip duration in days for round trips
    non_stop: bool = False
    max_price: Optional[int] = None
    view_by: str = "MONTH"  # MONTH, DATE, DURATION, WEEK, COUNTRY

class FlightInfo(BaseModel):
    airline: str
    departure_time: str
    arrival_time: str
    duration: str
    stops: int
    price: str
    is_best: bool = False
    booking_url: Optional[str] = None
    flight_number: Optional[str] = None
    departure_airport: Optional[str] = None
    arrival_airport: Optional[str] = None

class FlightSearchResponse(BaseModel):
    origin_code: str
    destination_code: str
    departure_date: str
    return_date: Optional[str]
    current_price: Optional[str]
    outbound_flights: List[FlightInfo]
    return_flights: Optional[List[FlightInfo]] = None
    total_flights: int

class DateOption(BaseModel):
    departure_date: str
    return_date: str
    total_price: float
    cheapest_flight: str
    flights_found: int

class FlexibleSearchResponse(BaseModel):
    origin_code: str
    destination_code: str
    month_searched: str
    trip_length_days: int
    cheapest_option: Optional[DateOption]
    all_options: List[DateOption]
    searches_performed: int

class CheapestDateResult(BaseModel):
    departure_date: str
    return_date: Optional[str]
    price: float
    price_formatted: str
    links: Dict[str, str]

class CheapestDateSearchResponse(BaseModel):
    origin: str
    destination: str
    currency: str
    cheapest_overall: Optional[CheapestDateResult]
    dates: List[CheapestDateResult]
    message: Optional[str] = None

# Legacy models
class Flight(BaseModel):
    airline: str
    origin: str
    destination: str
    departure: str
    arrival: str
    duration: str
    price: str
    stops: int
    booking_url: str
    flight_number: Optional[str] = None

class SearchResults(BaseModel):
    outbound: List[Flight]
    return_flights: Optional[List[Flight]] = None
    best_options: dict
    searches: int = 1
    total: int


class AILookupService:
    """AI-powered lookup and data processing for flights"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key not set")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
    
    async def process_flight_data(self, amadeus_data: Dict, origin: str, dest: str, date: str) -> Dict:
        """Process raw Amadeus data - bypass AI and process directly"""
        # Since AI is unreliable, let's process directly
        return amadeus_data  # Return raw data for direct processing
    
    async def resolve_airport_code(self, city: str) -> str:
        """Resolve city name to airport code using AI"""
        # If already looks like airport code, verify it
        if len(city) == 3 and city.isupper():
            prompt = f"Is {city} a valid IATA airport code? Reply with just YES or NO."
            response = await self._query_ai(prompt)
            if response and "YES" in response.upper():
                return city
        
        # Special handling for common cities
        city_lower = city.lower()
        if 'london' in city_lower:
            return 'LHR'  # Heathrow is the main London airport
        elif 'new york' in city_lower or 'nyc' in city_lower:
            return 'JFK'
        elif 'los angeles' in city_lower:
            return 'LAX'
        elif 'san francisco' in city_lower:
            return 'SFO'
        elif 'paris' in city_lower:
            return 'CDG'
        elif 'tokyo' in city_lower:
            return 'NRT'
        
        # Ask AI for the airport code
        prompt = f"What is the main IATA airport code for {city}? If it's London, use LHR. Reply with just the 3-letter code, nothing else."
        code = await self._query_ai(prompt)
        
        if code and len(code.strip()) == 3:
            return code.strip().upper()
        
        # If AI fails, use first 3 letters as last resort
        logger.warning(f"AI couldn't resolve airport for {city}, using first 3 letters")
        return city[:3].upper()
    
    async def get_airline_name(self, code: str) -> str:
        """Get airline name from code using AI"""
        prompt = f"What airline has the IATA code {code}? Reply with just the airline name, nothing else."
        name = await self._query_ai(prompt)
        
        if name:
            return name.strip()
        
        # If AI fails, return the code
        logger.warning(f"AI couldn't resolve airline {code}")
        return code
    
    async def _query_ai(self, prompt: str) -> str:
        """Query AI model for text responses"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "z-ai/glm-4.5",  # Switch to more reliable model
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
    
    async def _query_ai_json(self, prompt: str) -> Dict:
        """Query AI model for JSON responses"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "z-ai/glm-4.5",  # Switch to more reliable model
            "messages": [
                {"role": "system", "content": "You are a flight data analyst. Always respond with valid JSON only, no explanations."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 4000
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result['choices'][0]['message']['content']
                        # Remove markdown code blocks if present
                        if '```json' in content:
                            content = content.split('```json')[1].split('```')[0].strip()
                        elif '```' in content:
                            content = content.split('```')[1].split('```')[0].strip()
                        
                        # Try to parse as JSON
                        try:
                            return json.loads(content)
                        except json.JSONDecodeError:
                            logger.error(f"AI returned invalid JSON: {content[:200]}")
                            return {}
                    else:
                        logger.error(f"AI API error: {response.status}")
                        return {}
        except Exception as e:
            logger.error(f"AI JSON query failed: {e}")
            return {}


class CheapestDateSearch:
    """Amadeus Cheapest Date Search"""
    
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
    
    async def search_cheapest_dates(self, request: CheapestDateSearchRequest) -> CheapestDateSearchResponse:
        """Search for cheapest flight dates by checking multiple dates"""
        # Resolve airports
        origin = await self.ai_lookup.resolve_airport_code(request.origin)
        dest = await self.ai_lookup.resolve_airport_code(request.destination)
        
        logger.info(f"Searching cheapest dates: {origin} to {dest}")
        
        try:
            from datetime import datetime, timedelta
            
            # Determine search range
            if request.departure_date:
                base_date = datetime.strptime(request.departure_date, '%Y-%m-%d')
            else:
                base_date = datetime.now() + timedelta(days=30)  # Start from 30 days out
            
            dates = []
            cheapest = None
            min_price = float('inf')
            
            # Search across multiple dates (check 10 different dates)
            for days_offset in range(-3, 7):  # Search 3 days before to 6 days after
                search_date = base_date + timedelta(days=days_offset)
                departure_str = search_date.strftime('%Y-%m-%d')
                
                # Skip past dates
                if search_date < datetime.now():
                    continue
                
                try:
                    # Search for flights on this date
                    params = {
                        'originLocationCode': origin,
                        'destinationLocationCode': dest,
                        'departureDate': departure_str,
                        'adults': 1,
                        'max': 3,  # Just get a few to check price
                        'currencyCode': 'USD'
                    }
                    
                    # Add return date if not one-way
                    return_date = None
                    if not request.one_way:
                        duration = request.duration or 7
                        return_date = (search_date + timedelta(days=duration)).strftime('%Y-%m-%d')
                        params['returnDate'] = return_date
                    
                    # Get flight offers
                    response = self.amadeus.shopping.flight_offers_search.get(**params)
                    
                    if hasattr(response, 'data') and response.data:
                        # Get cheapest price for this date
                        min_offer = min(response.data, key=lambda x: float(x['price']['total']))
                        price = float(min_offer['price']['total'])
                        
                        date_result = CheapestDateResult(
                            departure_date=departure_str,
                            return_date=return_date,
                            price=price,
                            price_formatted=f"${price:.0f}",
                            links={
                                'booking': f"https://www.kayak.com/flights/{origin}-{dest}/{departure_str}",
                                'details': f"/flights/search"
                            }
                        )
                        dates.append(date_result)
                        
                        if price < min_price:
                            min_price = price
                            cheapest = date_result
                            
                except ResponseError:
                    continue  # Skip dates with no availability
            
            # Sort dates by price
            dates.sort(key=lambda x: x.price)
            
            return CheapestDateSearchResponse(
                origin=origin,
                destination=dest,
                currency='USD',
                cheapest_overall=cheapest,
                dates=dates[:10],  # Return top 10 cheapest dates
                message=f"Found {len(dates)} date options with prices" if dates else "No flights found for this route in the date range"
            )
            
        except Exception as e:
            logger.error(f"Cheapest date search error: {e}")
            return CheapestDateSearchResponse(
                origin=origin,
                destination=dest,
                currency='USD',
                cheapest_overall=None,
                dates=[],
                message=f"Error searching for cheapest dates: {str(e)}"
            )


class AmadeusFlightService:
    """Amadeus Flight Search Service"""
    
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
    
    async def _resolve_airport(self, city: str) -> str:
        """Convert city to airport code using AI"""
        return await self.ai_lookup.resolve_airport_code(city)
    
    def _parse_duration(self, duration: str) -> str:
        """Convert PT5H30M to 5h 30m"""
        if not duration:
            return "N/A"
        
        duration = duration.replace("PT", "")
        hours = minutes = 0
        
        if "H" in duration:
            parts = duration.split("H")
            hours = int(parts[0])
            if "M" in parts[-1]:
                minutes = int(parts[-1].replace("M", ""))
        elif "M" in duration:
            minutes = int(duration.replace("M", ""))
        
        return f"{hours}h {minutes}m"
    
    def _generate_booking_url(self, origin: str, dest: str, date: str, carrier: str, flight_num: str, offer_id: str) -> str:
        """Generate booking URL for the flight"""
        # Airline direct booking URLs with proper formatting
        airline_urls = {
            'AA': f"https://www.aa.com/booking/search?origin={origin}&destination={dest}&departureDate={date}&tripType=oneWay",
            'UA': f"https://www.united.com/en/us/fsl/mobile/booking?f={origin}&t={dest}&d={date}",
            'DL': f"https://www.delta.com/flight-search/search-results?origin={origin}&destination={dest}&departureDate={date}",
            'BA': f"https://www.britishairways.com/travel/book/public/en_gb?from={origin}&to={dest}&outboundDate={date}",
            'LH': f"https://www.lufthansa.com/us/en/flight-search?origin={origin}&destination={dest}&outboundDate={date}",
            'AF': f"https://www.airfrance.com/us/en/search?origin={origin}&destination={dest}&departureDate={date}",
            'KL': f"https://www.klm.com/search/offers?origin={origin}&destination={dest}&departureDate={date}",
            'EK': f"https://www.emirates.com/flights/{origin.lower()}-{dest.lower()}/",
            'B6': f"https://www.jetblue.com/booking/flights?from={origin}&to={dest}&depart={date}",
            'AS': f"https://www.alaskaair.com/flights/from-{origin}/to-{dest}?departureDate={date}",
            'WN': f"https://www.southwest.com/air/booking?originationAirportCode={origin}&destinationAirportCode={dest}&departureDate={date}",
            'F9': f"https://www.flyfrontier.com/flights/from-{origin}/to-{dest}?departureDate={date}",
            'NK': f"https://www.spirit.com/book/flights?from={origin}&to={dest}&departDate={date}",
            'SY': f"https://www.suncountry.com/booking/search?origin={origin}&destination={dest}&departureDate={date}"
        }
        
        # Check if we have a direct airline URL
        if carrier in airline_urls:
            return airline_urls[carrier]
        
        # Default to Google Flights which works universally
        return f"https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI1LTA5LTAzag0IAhIJL20vMDJfMjg2cg0IAhIJL20vMDNfM2Q0&tfu=EgYIARABGAA".replace('2025-09-03', date).replace('02_286', origin).replace('03_3d4', dest)
    
    async def _extract_flights(self, offers: List[Dict], return_trip: bool = False) -> List[FlightInfo]:
        """Extract flights from Amadeus response"""
        flights = []
        seen_flights = set()  # Track unique flights
        
        # Sort offers by price first
        sorted_offers = sorted(offers, key=lambda x: float(x.get('price', {}).get('total', '999999')))
        
        for i, offer in enumerate(sorted_offers[:50]):  # Process more offers
            try:
                itinerary_idx = 1 if return_trip and len(offer.get('itineraries', [])) > 1 else 0
                itinerary = offer['itineraries'][itinerary_idx]
                segments = itinerary['segments']
                
                first_seg = segments[0]
                last_seg = segments[-1]
                
                # Create unique key to avoid duplicates
                flight_key = f"{first_seg.get('carrierCode')}{first_seg.get('number')}_{first_seg['departure']['at']}_{last_seg['arrival']['at']}"
                
                if flight_key in seen_flights:
                    continue  # Skip duplicate
                seen_flights.add(flight_key)
                
                # Get airline name using AI
                airline_code = first_seg.get('carrierCode', 'Unknown')
                airline_name = await self.ai_lookup.get_airline_name(airline_code)
                
                # Build flight number
                flight_number = f"{airline_code}{first_seg.get('number', '')}"
                
                # Generate booking URL
                booking_url = self._generate_booking_url(
                    first_seg['departure']['iataCode'],
                    last_seg['arrival']['iataCode'],
                    first_seg['departure']['at'].split('T')[0],
                    airline_code,
                    flight_number,
                    offer.get('id', '')
                )
                
                flights.append(FlightInfo(
                    airline=airline_name,
                    departure_time=first_seg['departure']['at'].split('T')[1][:5],
                    arrival_time=last_seg['arrival']['at'].split('T')[1][:5],
                    duration=self._parse_duration(itinerary.get('duration', '')),
                    stops=len(segments) - 1,
                    price=f"${float(offer['price']['total']):.0f}",
                    is_best=(i == 0),
                    booking_url=booking_url,
                    flight_number=flight_number,
                    departure_airport=first_seg['departure']['iataCode'],
                    arrival_airport=last_seg['arrival']['iataCode']
                ))
                
                # Limit to 20 unique flights for better selection
                if len(flights) >= 20:
                    break
                    
            except (KeyError, IndexError) as e:
                logger.debug(f"Skipping offer: {e}")
        
        # Sort flights by price and mark the cheapest as best
        if flights:
            flights.sort(key=lambda x: float(x.price.replace('$', '').replace(',', '')))
            flights[0].is_best = True
            for i in range(1, len(flights)):
                flights[i].is_best = False
        
        return flights[:10]  # Return top 10 after sorting
    
    async def search(self, request: FlightSearchRequest) -> FlightSearchResponse:
        """Search flights with comprehensive data processing"""
        origin = await self._resolve_airport(request.origin)
        dest = await self._resolve_airport(request.destination)
        
        logger.info(f"Searching flights: {origin} to {dest} on {request.departure_date}")
        
        try:
            params = {
                'originLocationCode': origin,
                'destinationLocationCode': dest,
                'departureDate': request.departure_date,
                'adults': request.adults,
                'max': 100,  # Get maximum results for better coverage
                'nonStop': 'false',
                'currencyCode': 'USD'
            }
            
            if request.children:
                params['children'] = request.children
            if request.return_date:
                params['returnDate'] = request.return_date
            if request.seat_class != "economy":
                params['travelClass'] = request.seat_class.upper()
            
            # Get raw Amadeus response
            response = self.amadeus.shopping.flight_offers_search.get(**params)
            offers = response.data if hasattr(response, 'data') else []
            
            # Get dictionaries if available
            dictionaries = response.result.get('dictionaries', {}) if hasattr(response, 'result') else {}
            
            # Skip AI processing for now - use direct extraction
            outbound = await self._extract_flights(offers)
            return_flights = None
            
            if request.return_date and offers:
                return_flights = await self._extract_flights(offers, return_trip=True)
            
            # Get min price
            prices = [float(f.price.replace('$', '')) for f in outbound if f.price != 'N/A']
            current_price = f"${min(prices):.0f}" if prices else None
            
            return FlightSearchResponse(
                origin_code=origin,
                destination_code=dest,
                departure_date=request.departure_date,
                return_date=request.return_date,
                current_price=current_price,
                outbound_flights=outbound,
                return_flights=return_flights,
                total_flights=len(outbound) + (len(return_flights) if return_flights else 0)
            )
            
        except ResponseError as e:
            logger.error(f"Amadeus error: {e}")
            return FlightSearchResponse(
                origin_code=origin,
                destination_code=dest,
                departure_date=request.departure_date,
                return_date=request.return_date,
                current_price=None,
                outbound_flights=[],
                return_flights=None,
                total_flights=0
            )
    
    async def _extract_flights_enhanced(self, ai_data: Dict, offers: List[Dict], return_trip: bool = False) -> List[FlightInfo]:
        """Extract flights - always use direct extraction for reliability"""
        # Skip AI processing and use direct extraction
        return await self._extract_flights(offers, return_trip)
    
    async def _parse_ai_flights(self, ai_data: Dict, return_trip: bool) -> List[FlightInfo]:
        """Parse AI-processed flight data"""
        flights = []
        
        # Handle AI response structure
        flight_list = ai_data.get('return_flights' if return_trip else 'outbound_flights', [])
        if not flight_list and 'flights' in ai_data:
            flight_list = ai_data['flights']
        
        for flight in flight_list[:10]:
            flights.append(FlightInfo(
                airline=flight.get('airline_name', flight.get('airline', 'Unknown')),
                departure_time=flight.get('departure_time', 'N/A'),
                arrival_time=flight.get('arrival_time', 'N/A'),
                duration=flight.get('duration', 'N/A'),
                stops=flight.get('stops', 0),
                price=flight.get('price', 'N/A'),
                is_best=flight.get('is_best', False),
                booking_url=flight.get('booking_url'),
                flight_number=flight.get('flight_number'),
                departure_airport=flight.get('departure_airport'),
                arrival_airport=flight.get('arrival_airport')
            ))
        
        return flights


class FlexibleFlightSearch:
    """Flexible date search"""
    
    def __init__(self):
        self.service = AmadeusFlightService()
    
    async def search_flexible_dates(self, request: FlexibleSearchRequest) -> FlexibleSearchResponse:
        """Search multiple dates for best prices"""
        origin = await self.service._resolve_airport(request.origin)
        dest = await self.service._resolve_airport(request.destination)
        
        year, month = map(int, request.departure_month.split('-'))
        options = []
        
        for day in range(1, 29, 7):
            if len(options) >= request.max_searches:
                break
            
            try:
                dep_date = f"{year:04d}-{month:02d}-{day:02d}"
                ret_date = (datetime(year, month, day) + timedelta(days=request.trip_length_days)).strftime('%Y-%m-%d')
                
                response = self.service.amadeus.shopping.flight_offers_search.get(
                    originLocationCode=origin,
                    destinationLocationCode=dest,
                    departureDate=dep_date,
                    returnDate=ret_date,
                    adults=request.adults,
                    travelClass=request.seat_class.upper(),
                    max=3
                )
                
                if response.data:
                    min_offer = min(response.data, key=lambda x: float(x['price']['total']))
                    airline_code = min_offer['itineraries'][0]['segments'][0]['carrierCode']
                    airline_name = await self.service.ai_lookup.get_airline_name(airline_code)
                    
                    options.append(DateOption(
                        departure_date=dep_date,
                        return_date=ret_date,
                        total_price=float(min_offer['price']['total']),
                        cheapest_flight=airline_name,
                        flights_found=len(response.data)
                    ))
                    
            except ResponseError:
                continue
        
        options.sort(key=lambda x: x.total_price)
        
        return FlexibleSearchResponse(
            origin_code=origin,
            destination_code=dest,
            month_searched=request.departure_month,
            trip_length_days=request.trip_length_days,
            cheapest_option=options[0] if options else None,
            all_options=options,
            searches_performed=len(options)
        )


# Legacy function for GET /flights
async def search_flights(from_city: str, to_city: str, departure: str, return_date: Optional[str] = None) -> SearchResults:
    """Legacy endpoint support"""
    service = AmadeusFlightService()
    
    response = await service.search(FlightSearchRequest(
        origin=from_city,
        destination=to_city,
        departure_date=departure,
        return_date=return_date,
        trip_type="round-trip" if return_date else "one-way"
    ))
    
    outbound = [
        Flight(
            airline=f.airline,
            origin=response.origin_code,
            destination=response.destination_code,
            departure=f.departure_time,
            arrival=f.arrival_time,
            duration=f.duration,
            price=f.price,
            stops=f.stops,
            booking_url=f.booking_url if f.booking_url else "https://www.kayak.com/flights",
            flight_number=f.flight_number
        ) for f in response.outbound_flights
    ]
    
    return_flights = None
    if response.return_flights:
        return_flights = [
            Flight(
                airline=f.airline,
                origin=response.destination_code,
                destination=response.origin_code,
                departure=f.departure_time,
                arrival=f.arrival_time,
                duration=f.duration,
                price=f.price,
                stops=f.stops,
                booking_url=f.booking_url if f.booking_url else "https://www.kayak.com/flights",
                flight_number=f.flight_number
            ) for f in response.return_flights
        ]
    
    return SearchResults(
        outbound=outbound,
        return_flights=return_flights,
        best_options={"current_price": response.current_price, "total_found": response.total_flights},
        total=response.total_flights
    )