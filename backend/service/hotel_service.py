"""
Hotel Service Layer
Orchestrates hotel searches using scrapers
"""

from typing import Dict, List, Optional
import sys
from pathlib import Path
import uuid


sys.path.append(str(Path(__file__).parent.parent))

from scraper.booking_scraper import BookingComScraper
from utils.convex_client import get_db
import logging


class HotelService:
    """Service layer for hotel searches"""
    def __init__(self):
        self.logger = logging.getLogger('HotelService')
        self.scraper = BookingComScraper(headless=True)
        self.initialized = False
        self.db = get_db()
    async def initialize(self):
        """Initialize the scraper"""
        if not self.initialized:
            await self.scraper.initialize()
            self.initialized = True
            self.logger.info("Hotel service initialized")
    async def close(self):
        """Close the scraper"""
        if self.initialized:
            await self.scraper.close()
            self.initialized = False
    async def search(self, request: Dict) -> Dict:
        """
        Search hotels with enrichment and ranking
        Args:
            request: {
                'destination': str,
                'check_in': str,
                'check_out': str,
                'adults': int,
                'rooms': int,
                'children': int
            }
        """
        self.logger.info(f"Processing hotel search: {request['destination']}")

        await self.initialize()
        try:

            from scraper.booking_scraper import SearchParams

            params = SearchParams(
                destination=request['destination'],
                check_in=request['check_in'],
                check_out=request['check_out'],
                adults=request.get('adults', 2),
                children=request.get('children', 0),
                rooms=request.get('rooms', 1)
            )

            hotel_results = await self.scraper.search_hotels(params)

            hotels = []
            for hotel in hotel_results:
                hotels.append({
                    'name': hotel.name,
                    'price': self._extract_price_value(hotel.price) if hotel.price else 0,
                    'price_formatted': hotel.price,
                    'rating': hotel.rating,
                    'reviews_count': hotel.reviews_count,
                    'location': hotel.location,
                    'amenities': hotel.amenities,
                    'source': hotel.source
                })

            response = {
                'status': 'success',
                'hotels': hotels,
                'total': len(hotels),
                'best_price': min([h['price'] for h in hotels], default=None) if hotels else None,
                'analysis': self._analyze_hotels(hotels),
                'recommendations': self._get_recommendations(hotels, request),
                'filters': self._get_available_filters(hotels)
            }
            self.logger.info(f"Found {len(hotels)} hotels")

            try:
                saved_ids = await self.save_to_db(hotels)
                response['saved_hotel_ids'] = saved_ids
                self.logger.info(f"Saved {len(saved_ids)} hotels to database")
            except Exception as e:
                self.logger.error(f"Failed to save hotels to database: {e}")
            return response
        except Exception as e:
            self.logger.error(f"Hotel search error: {e}", exc_info=True)
            return {
                'status': 'error',
                'error': str(e),
                'hotels': [],
                'total': 0
            }
    def _analyze_hotels(self, hotels: List[Dict]) -> Dict:
        """Analyze hotel options"""
        if not hotels:
            return {}
        prices = [h['price'] for h in hotels if h.get('price')]
        ratings = [h['rating'] for h in hotels if h.get('rating')]

        budget = len([h for h in hotels if h.get('price', 0) < 100])
        mid_range = len([h for h in hotels if 100 <= h.get('price', 0) < 200])
        luxury = len([h for h in hotels if h.get('price', 0) >= 200])

        all_amenities = []
        for hotel in hotels:
            all_amenities.extend(hotel.get('amenities', []))
        amenity_counts = {}
        for amenity in all_amenities:
            amenity_counts[amenity] = amenity_counts.get(amenity, 0) + 1

        top_amenities = sorted(amenity_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        return {
            'price_range': {
                'min': min(prices) if prices else 0,
                'max': max(prices) if prices else 0,
                'avg': sum(prices) / len(prices) if prices else 0
            },
            'rating_stats': {
                'min': min(ratings) if ratings else 0,
                'max': max(ratings) if ratings else 0,
                'avg': sum(ratings) / len(ratings) if ratings else 0
            },
            'price_categories': {
                'budget': budget,
                'mid_range': mid_range,
                'luxury': luxury
            },
            'top_amenities': [a[0] for a in top_amenities],
            'locations': self._get_unique_locations(hotels)
        }
    def _get_recommendations(self, hotels: List[Dict], request: Dict) -> Dict:
        """Get hotel recommendations based on different criteria"""
        if not hotels:
            return {}
        recommendations = {}

        cheapest = min(hotels, key=lambda h: h.get('price', float('inf')))
        recommendations['cheapest'] = {
            'hotel': cheapest,
            'reason': f"Lowest price at {cheapest.get('price_formatted', 'N/A')}"
        }

        rated_hotels = [h for h in hotels if h.get('rating')]
        if rated_hotels:
            best_rated = max(rated_hotels, key=lambda h: h.get('rating', 0))
            recommendations['best_rated'] = {
                'hotel': best_rated,
                'reason': f"Highest rating of {best_rated.get('rating')}/10 with {best_rated.get('reviews_count', 0)} reviews"
            }

        for hotel in hotels:
            score = 100

            min_price = cheapest.get('price', 1) or 1
            price_ratio = hotel.get('price', min_price) / min_price
            score -= (price_ratio - 1) * 20

            if hotel.get('rating'):
                score += hotel.get('rating', 0) * 5

            amenity_count = len(hotel.get('amenities', []))
            score += amenity_count * 2

            reviews = hotel.get('reviews_count')
            if reviews and reviews > 100:
                score += 10
            hotel['value_score'] = score
        best_value = max(hotels, key=lambda h: h.get('value_score', 0))
        recommendations['best_value'] = {
            'hotel': best_value,
            'reason': "Best combination of price, rating, and amenities"
        }

        business_hotels = [
            h for h in hotels 
            if any(a in str(h.get('amenities', [])).lower() 
                  for a in ['business', 'wifi', 'desk', 'conference'])
        ]
        if business_hotels:
            best_business = business_hotels[0]
            recommendations['best_business'] = {
                'hotel': best_business,
                'reason': "Business-friendly with work amenities"
            }

        central_hotels = [
            h for h in hotels 
            if h.get('distance') and ('center' in str(h.get('location', '')).lower() or
                                     any(d in str(h.get('distance', '')).lower() 
                                         for d in ['0.', '1.', '2.']))
        ]
        if central_hotels:
            best_location = central_hotels[0]
            recommendations['best_location'] = {
                'hotel': best_location,
                'reason': f"Central location, {best_location.get('distance', 'close')} from center"
            }
        return recommendations
    def _get_available_filters(self, hotels: List[Dict]) -> Dict:
        """Get available filter options from search results"""
        if not hotels:
            return {}

        amenities = set()
        locations = set()
        room_types = set()
        for hotel in hotels:

            for amenity in hotel.get('amenities', []):
                amenities.add(amenity)

            if hotel.get('location'):
                locations.add(hotel['location'])

            if hotel.get('room_type'):
                room_types.add(hotel['room_type'])
        return {
            'amenities': sorted(list(amenities)),
            'locations': sorted(list(locations)),
            'room_types': sorted(list(room_types)),
            'price_ranges': [
                {'label': 'Budget (< $100)', 'min': 0, 'max': 100},
                {'label': 'Mid-range ($100-200)', 'min': 100, 'max': 200},
                {'label': 'Luxury ($200+)', 'min': 200, 'max': 999999}
            ],
            'ratings': [
                {'label': 'Excellent (9+)', 'min': 9},
                {'label': 'Very Good (8+)', 'min': 8},
                {'label': 'Good (7+)', 'min': 7}
            ]
        }
    def _get_unique_locations(self, hotels: List[Dict]) -> List[str]:
        """Get unique locations/neighborhoods"""
        locations = set()
        for hotel in hotels:
            if hotel.get('location'):

                loc = hotel['location'].split(',')[0].strip()
                locations.add(loc)
        return sorted(list(locations))[:10]
    def _extract_price_value(self, price_input) -> float:
        """Extract numeric price from string like '$150' or '$2,962' or float value"""
        import re

        if isinstance(price_input, (int, float)):

            price = float(price_input)
            if price <= 0 or price > 100000:
                self.logger.warning(f"Price {price} out of valid range, using 0")
                return 0
            return price

        if not price_input or not isinstance(price_input, str):
            return 0

        cleaned = str(price_input).replace(',', '').replace('$', '').replace('€', '').replace('£', '').strip()

        numbers = re.findall(r'\d+\.?\d*', cleaned)
        if numbers:
            try:

                price = float(numbers[0])

                if price <= 0 or price > 100000:
                    self.logger.warning(f"Extracted price {price} out of valid range, using 0")
                    return 0
                return price
            except (ValueError, IndexError):
                return 0
        return 0
    async def save_to_db(self, hotels: List[Dict], itinerary_id: Optional[str] = None, user_id: Optional[str] = None) -> List[str]:
        """
        Save hotel search results to database
        Args:
            hotels: List of hotel data to save
            itinerary_id: Optional itinerary ID to link hotels to
            user_id: Optional user ID
        Returns:
            List of saved hotel IDs
        """
        saved_ids = []
        for hotel in hotels:
            try:


                price_raw = hotel.get("price_formatted") or hotel.get("price", "0")
                price = self._extract_price_value(price_raw)

                if price <= 0:
                    self.logger.warning(f"Skipping hotel {hotel.get('name')} with invalid price: {price_raw}")
                    continue
                hotel_data = {
                    "userId": user_id or f"user_{uuid.uuid4().hex[:8]}",
                    "name": hotel.get("name", "Unknown Hotel"),
                    "address": hotel.get("location", ""),
                    "city": hotel.get("city", ""),
                    "country": hotel.get("country", ""),
                    "checkInDate": hotel.get("check_in", ""),
                    "checkOutDate": hotel.get("check_out", ""),
                    "price": price,
                    "currency": hotel.get("currency", "USD"),
                    "status": "searching"
                }

                if itinerary_id:
                    hotel_data["itineraryId"] = itinerary_id
                if hotel.get("rating"):
                    hotel_data["rating"] = float(hotel.get("rating"))
                if hotel.get("amenities") and isinstance(hotel.get("amenities"), list):
                    hotel_data["amenities"] = hotel.get("amenities")
                if hotel.get("room_type"):
                    hotel_data["roomType"] = hotel.get("room_type")
                if hotel.get("booking_reference"):
                    hotel_data["bookingReference"] = hotel.get("booking_reference")
                if hotel.get("image_url"):
                    hotel_data["imageUrl"] = hotel.get("image_url")

                hotel_id = self.db.save_hotel(hotel_data)
                saved_ids.append(hotel_id)
                self.logger.info(f"Saved hotel {hotel_id} to database")
            except Exception as e:
                self.logger.error(f"Failed to save hotel to database: {e}")
        return saved_ids



_hotel_service_instance = None

async def get_global_hotel_service():
    """Get or create the global hotel service instance."""
    global _hotel_service_instance
    if _hotel_service_instance is None:
        _hotel_service_instance = HotelService()
    return _hotel_service_instance

async def call_hotel_service(destination: str, check_in: str, check_out: str, adults: int = 2, rooms: int = 1, ctx=None) -> str:
    """Useful for searching hotels based on destination and dates.
    Args:
        destination: City or location to search hotels (e.g., "Tokyo", "Paris")
        check_in: Check-in date (e.g., "2025-11-11")
        check_out: Check-out date (e.g., "2025-11-15")
        adults: Number of adults (default: 2)
        rooms: Number of rooms (default: 1)
        ctx: Optional context for state storage
    """
    import json

    request = {
        'destination': destination,
        'check_in': check_in,
        'check_out': check_out,
        'adults': adults,
        'rooms': rooms,
        'children': 0
    }

    hotel_service = await get_global_hotel_service()
    result = await hotel_service.search(request)

    if ctx and hasattr(ctx, 'store'):
        try:
            async with ctx.store.edit_state() as ctx_state:
                if "state" not in ctx_state:
                    ctx_state["state"] = {}
                ctx_state["state"]["hotels"] = result

                if "job_id" in ctx_state:
                    from utils.job_manager import get_job_manager
                    job_manager = get_job_manager()
                    hotels_count = len(result.get("hotels", []))
                    min_price = result.get("best_price", 0)
                    max_price = max([h.get("price", 0) for h in result.get("hotels", [])], default=0) if result.get("hotels") else 0

                    flights_data = ctx_state.get("state", {}).get("flights", {})
                    flights_count = len(flights_data.get("flights", []))
                    progress = {
                        "message": f"Found {hotels_count} hotels from ${min_price} to ${max_price}",
                        "step": "hotels",
                        "details": {
                            "flights_found": flights_count,
                            "hotels_found": hotels_count,
                            "restaurants_found": 0,
                            "activities_planned": 0,
                            "price_ranges": {
                                "hotels": {"min": min_price, "max": max_price}
                            }
                        }
                    }

                    if flights_data.get("best_price"):
                        progress["details"]["price_ranges"]["flights"] = {
                            "min": flights_data.get("best_price"),
                            "max": max([f.get("price", 0) for f in flights_data.get("flights", [])], default=0)
                        }
                    job_manager.update_job_progress(ctx_state["job_id"], progress)
        except Exception as e:

            pass
    return json.dumps(result, indent=2)
