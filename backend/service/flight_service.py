"""
Flight Service Layer
Orchestrates flight searches using scrapers
"""

from typing import Dict, List, Optional
import sys
from pathlib import Path
import json
import logging
import uuid

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scraper.google_flights_scraper import GoogleFlightsRoundTripScraper
from utils.convex_client import get_db

logger = logging.getLogger(__name__)

class FlightService:
    """Service layer for flight searches"""
    
    def __init__(self):
        self.scraper = GoogleFlightsRoundTripScraper(headless=True)
        self.db = get_db()
        
    async def close(self):
        """Close the scraper"""
        pass  # Original scraper handles browser lifecycle per search
            
    async def search(self, request: Dict) -> Dict:
        """
        Search flights with enrichment and ranking
        
        Args:
            request: {
                'origin': str,
                'destination': str,
                'departure_date': str,
                'return_date': Optional[str],
                'adults': int,
                'class': str
            }
        """
        logger.info(f"Processing flight search: {request['origin']} → {request['destination']}")
        
        try:
            # Use the scraper's search method - limited to 3 options for faster results
            results = await self.scraper.search_round_trip_options(
                origin=request['origin'],
                destination=request['destination'],
                departure_date=request['departure_date'],
                return_date=request.get('return_date', request['departure_date']),
                num_options=3
            )
            
            # Check for errors
            if 'error' in results:
                return {
                    'status': 'error',
                    'error': results['error'],
                    'flights': [],
                    'total': 0
                }
                
            # Get flights from flight_options
            flight_options = results.get('flight_options', [])
            
            # Convert to simpler format for compatibility
            flights = []
            for option in flight_options:
                basic_info = option.get('basic_info', {})
                outbound = option.get('outbound', {})
                flights.append({
                    'airline': basic_info.get('airline') or outbound.get('airline'),
                    'price': basic_info.get('price_value', 0),
                    'price_formatted': basic_info.get('price'),
                    'departure_time': outbound.get('departure_time'),
                    'arrival_time': outbound.get('arrival_time'),
                    'duration': outbound.get('duration'),
                    'stops': basic_info.get('stops_value', 0),
                    'origin': outbound.get('origin'),
                    'destination': outbound.get('destination')
                })
            
            # Build response in expected format
            response = {
                'status': 'success',
                'flights': flights,
                'flight_options': flight_options,  # Keep original detailed data
                'total': len(flights),
                'best_price': min([f['price'] for f in flights], default=None) if flights else None,
                'analysis': self._analyze_flights(flights),
                'recommendations': self._get_recommendations(flights, request),
                'summary': results.get('summary', {})
            }
            
            logger.info(f"Found {len(flights)} flights")
            
            # Save all search results to database
            try:
                saved_ids = await self.save_to_db(flights)
                response['saved_flight_ids'] = saved_ids
                logger.info(f"Saved {len(saved_ids)} flights to database")
            except Exception as e:
                logger.error(f"Failed to save flights to database: {e}")
            
            return response
            
        except Exception as e:
            logger.error(f"Flight search error: {e}", exc_info=True)
            return {
                'status': 'error',
                'error': str(e),
                'flights': [],
                'total': 0
            }
            
    def _analyze_flights(self, flights: List[Dict]) -> Dict:
        """Analyze flight options"""
        if not flights:
            return {}
            
        prices = [f['price'] for f in flights if f.get('price')]
        durations = [f['duration'] for f in flights if f.get('duration')]
        
        # Count by stops
        nonstop_count = len([f for f in flights if f.get('stops') == 0])
        one_stop_count = len([f for f in flights if f.get('stops') == 1])
        
        # Count by time of day
        morning = len([f for f in flights if self._is_morning(f.get('departure_time'))])
        afternoon = len([f for f in flights if self._is_afternoon(f.get('departure_time'))])
        evening = len([f for f in flights if self._is_evening(f.get('departure_time'))])
        
        return {
            'price_range': {
                'min': min(prices) if prices else 0,
                'max': max(prices) if prices else 0,
                'avg': sum(prices) / len(prices) if prices else 0
            },
            'stops_distribution': {
                'nonstop': nonstop_count,
                'one_stop': one_stop_count,
                'multiple': len(flights) - nonstop_count - one_stop_count
            },
            'departure_times': {
                'morning': morning,
                'afternoon': afternoon,
                'evening': evening
            },
            'airlines': list(set(f.get('airline') for f in flights if f.get('airline')))
        }
        
    def _get_recommendations(self, flights: List[Dict], request: Dict) -> Dict:
        """Get flight recommendations based on different criteria"""
        if not flights:
            return {}
            
        recommendations = {}
        
        # Cheapest option
        cheapest = min(flights, key=lambda f: f.get('price', float('inf')))
        recommendations['cheapest'] = {
            'flight': cheapest,
            'reason': f"Lowest price at {cheapest.get('price_formatted', 'N/A')}"
        }
        
        # Fastest option (nonstop if available)
        nonstop = [f for f in flights if f.get('stops') == 0]
        if nonstop:
            fastest = nonstop[0]  # Already sorted by price
            recommendations['fastest'] = {
                'flight': fastest,
                'reason': f"Nonstop flight, arrives quickest"
            }
            
        # Best value (balance of price and convenience)
        for flight in flights:
            score = 100
            
            # Price factor
            min_price = cheapest.get('price', 1)
            price_ratio = flight.get('price', min_price) / min_price
            score -= (price_ratio - 1) * 30
            
            # Stops factor
            score -= flight.get('stops', 0) * 20
            
            # Time factor
            if self._is_reasonable_time(flight.get('departure_time')):
                score += 10
                
            flight['value_score'] = score
            
        best_value = max(flights, key=lambda f: f.get('value_score', 0))
        recommendations['best_value'] = {
            'flight': best_value,
            'reason': "Best balance of price, convenience, and timing"
        }
        
        return recommendations
        
    def _is_morning(self, time_str: Optional[str]) -> bool:
        """Check if time is morning (5 AM - 12 PM)"""
        if not time_str:
            return False
        try:
            hour = int(time_str.split(':')[0])
            if 'PM' in time_str and hour != 12:
                hour += 12
            return 5 <= hour < 12
        except:
            return False
            
    def _is_afternoon(self, time_str: Optional[str]) -> bool:
        """Check if time is afternoon (12 PM - 5 PM)"""
        if not time_str:
            return False
        try:
            hour = int(time_str.split(':')[0])
            if 'PM' in time_str and hour != 12:
                hour += 12
            return 12 <= hour < 17
        except:
            return False
            
    def _is_evening(self, time_str: Optional[str]) -> bool:
        """Check if time is evening (5 PM - 12 AM)"""
        if not time_str:
            return False
        try:
            hour = int(time_str.split(':')[0])
            if 'PM' in time_str and hour != 12:
                hour += 12
            return hour >= 17 or hour < 5
        except:
            return False
            
    def _is_reasonable_time(self, time_str: Optional[str]) -> bool:
        """Check if departure time is reasonable (6 AM - 10 PM)"""
        if not time_str:
            return False
        try:
            hour = int(time_str.split(':')[0])
            if 'PM' in time_str and hour != 12:
                hour += 12
            return 6 <= hour <= 22
        except:
            return False
    
    async def save_to_db(self, flights: List[Dict], itinerary_id: Optional[str] = None, user_id: Optional[str] = None) -> List[str]:
        """
        Save flight search results to database
        
        Args:
            flights: List of flight data to save
            itinerary_id: Optional itinerary ID to link flights to
            user_id: Optional user ID
            
        Returns:
            List of saved flight IDs
        """
        saved_ids = []
        
        for flight in flights:
            try:
                # Transform flight data to match Convex schema
                flight_data = {
                    "userId": user_id or f"user_{uuid.uuid4().hex[:8]}",  # Required field, generate temp ID if not provided
                    "origin": flight.get("origin", ""),
                    "destination": flight.get("destination", ""),
                    "departureDate": flight.get("departure_time", ""),
                    "airline": flight.get("airline", "Unknown"),
                    "flightNumber": flight.get("flight_number", f"FL{uuid.uuid4().hex[:6].upper()}"),
                    "price": float(flight.get("price", 0)),
                    "currency": flight.get("currency", "USD"),
                    "status": "searching"
                }
                
                # Only add optional fields if they have values
                if itinerary_id:
                    flight_data["itineraryId"] = itinerary_id
                if flight.get("return_date"):
                    flight_data["returnDate"] = flight.get("return_date")
                if flight.get("duration"):
                    flight_data["duration"] = flight.get("duration")
                if flight.get("class"):
                    flight_data["class"] = flight.get("class")
                if flight.get("stops") is not None:
                    flight_data["stops"] = flight.get("stops")
                if flight.get("booking_reference"):
                    flight_data["bookingReference"] = flight.get("booking_reference")
                
                # Save to database
                flight_id = self.db.save_flight(flight_data)
                saved_ids.append(flight_id)
                logger.info(f"Saved flight {flight_id} to database")
                
            except Exception as e:
                logger.error(f"Failed to save flight to database: {e}")
                
        return saved_ids


# Global flight service instance
_flight_service_instance = None

async def get_global_flight_service():
    """Get or create the global flight service instance."""
    global _flight_service_instance
    if _flight_service_instance is None:
        _flight_service_instance = FlightService()
    return _flight_service_instance

async def call_flight_service(origin: str, destination: str, departure_date: str, return_date: Optional[str] = None, adults: int = 1, travel_class: str = "economy", ctx=None) -> str:
    """Useful for searching flights based on structured flight parameters."""
    
    # Build request object for flight service
    request = {
        'origin': origin,
        'destination': destination,
        'departure_date': departure_date,
        'return_date': return_date,
        'adults': adults,
        'class': travel_class.lower().replace('_', ' ')  # Handle enum values like 'BUSINESS_CLASS'
    }
    
    # Get flight service and search
    flight_service = await get_global_flight_service()
    result = await flight_service.search(request)
    
    # Store result in context state if ctx is provided
    if ctx and hasattr(ctx, 'store'):
        try:
            async with ctx.store.edit_state() as ctx_state:
                if "state" not in ctx_state:
                    ctx_state["state"] = {}
                ctx_state["state"]["flights"] = result
        except Exception as e:
            # Log but don't fail if context storage fails
            pass
    
    return json.dumps(result, indent=2)
