"""
Flight Service Layer
Orchestrates flight searches using scrapers
"""

from typing import Dict, List, Optional
import sys
from pathlib import Path
import json
import logging

sys.path.append(str(Path(__file__).parent.parent))

from service.api_utils import APIUtils
from database.travel_repository import TravelRepository

logger = logging.getLogger(__name__)

class FlightService:
    
    def __init__(self):
        self.api_utils = APIUtils()
        self.repository = TravelRepository()
        
    async def close(self):
        pass
            
    async def search(self, request: Dict) -> Dict:
        logger.info(f"Processing flight search: {request['origin']} → {request['destination']}")
        
        try:
            url_results = await self.api_utils.generate_flight_urls(
                origin=request['origin'],
                destination=request['destination'],
                departure_date=request['departure_date'],
                return_date=request.get('return_date'),
                adults=request.get('adults', 1),
                travel_class=request.get('class', 'economy')
            )
            
            if not url_results:
                return {
                    'status': 'error',
                    'error': 'No URLs generated',
                    'flights': [],
                    'total': 0
                }
            
            flights = await self.api_utils.generate_flight_metadata(
                origin=request['origin'],
                destination=request['destination'],
                departure_date=request['departure_date'],
                return_date=request.get('return_date'),
                adults=request.get('adults', 1),
                travel_class=request.get('class', 'economy')
            )
            
            # Save top 3 flights to database (async, non-blocking)
            if flights:
                try:
                    # Prepare flight data for database
                    flights_for_db = []
                    for flight in flights:
                        flights_for_db.append({
                            'origin': request['origin'],
                            'destination': request['destination'],
                            'airline': flight.get('airline', 'Unknown'),
                            'flight_number': flight.get('flight_number', ''),
                            'departure_date': flight.get('departure_time', request['departure_date']),
                            'arrival_date': flight.get('arrival_time'),
                            'price': flight.get('price', 0),
                            'stops': flight.get('stops', 0),
                            'duration': flight.get('duration'),
                            'booking_url': flight.get('booking_url')
                        })
                    
                    # Save to database (top 3 by price)
                    flight_ids = await self.repository.create_flights_batch(
                        flights_for_db,
                        itinerary_id=request.get('itinerary_id')
                    )
                    logger.info(f"Saved top {len(flight_ids)} flights to database")
                except Exception as e:
                    logger.error(f"Failed to save flights to database: {e}")
                    # Continue anyway - don't block the response
            
            flight_options = []
            for flight in flights:
                if flight.get('flight_type') == 'outbound':
                    option = {
                        'basic_info': {
                            'airline': flight.get('airline'),
                            'price': flight.get('price_formatted'),
                            'price_value': flight.get('price', 0),
                            'stops_value': flight.get('stops', 0)
                        },
                        'outbound': {
                            'airline': flight.get('airline'),
                            'departure_time': flight.get('departure_time'),
                            'arrival_time': flight.get('arrival_time'),
                            'duration': flight.get('duration'),
                            'origin': flight.get('origin'),
                            'destination': flight.get('destination'),
                            'layover': flight.get('layover')
                        }
                    }
                    flight_options.append(option)
            
            response = {
                'status': 'success',
                'flights': flights,
                'flight_options': flight_options,
                'total': len(flights),
                'best_price': min([f['price'] for f in flights if f.get('price')], default=None) if flights else None,
                'analysis': self._analyze_flights(flights),
                'recommendations': self._get_recommendations(flights, request),
                'search_urls': url_results,
                'note': 'Prices are estimates. Click search URLs for live pricing on Kayak.'
            }
            
            logger.info(f"Found {len(flights)} flights")
            
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
