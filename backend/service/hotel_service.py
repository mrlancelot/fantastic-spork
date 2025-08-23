"""
Hotel Service Layer
Orchestrates hotel searches using scrapers
"""

from typing import Dict, List, Optional
import sys
from pathlib import Path
import logging

sys.path.append(str(Path(__file__).parent.parent))

from service.api_utils import APIUtils
from database.travel_repository import TravelRepository


class HotelService:
    
    def __init__(self):
        self.logger = logging.getLogger('HotelService')
        self.api_utils = APIUtils()
        self.repository = TravelRepository()
        
    async def initialize(self):
        pass
            
    async def close(self):
        pass
            
    async def search(self, request: Dict) -> Dict:
        self.logger.info(f"Processing hotel search: {request['destination']}")
        print(f"DEBUG: Starting hotel search for {request['destination']}")
        
        try:
            print("DEBUG: Generating hotel URLs...")
            url_results = await self.api_utils.generate_hotel_urls(
                destination=request['destination'],
                check_in=request['check_in'],
                check_out=request['check_out'],
                adults=request.get('adults', 2),
                rooms=request.get('rooms', 1)
            )
            
            print(f"DEBUG: Generated {len(url_results) if url_results else 0} URLs")
            if url_results:
                for idx, result in enumerate(url_results):
                    print(f"DEBUG: URL {idx+1}: {result.get('platform', 'unknown')} - {result.get('url', 'N/A')[:100]}...")
            
            if not url_results:
                print("DEBUG: No URLs were generated!")
                return {
                    'status': 'error',
                    'error': 'No URLs generated',
                    'hotels': [],
                    'total': 0
                }
            
            urls = [result['url'] for result in url_results]
            print(f"DEBUG: Scraping {len(urls)} URLs...")
            html_contents = await self.api_utils.scrape_urls_parallel(urls)
            print(f"DEBUG: Scraped {len(html_contents)} pages")
            
            print("DEBUG: Extracting hotel data from scraped content...")
            hotels = await self.api_utils.extract_hotel_data(html_contents, urls)
            print(f"DEBUG: Extracted {len(hotels)} hotels")
            
            for hotel in hotels:
                if 'price' not in hotel or hotel['price'] == 0:
                    hotel['price'] = self._extract_price_value(hotel.get('price_formatted', ''))
                    # If still no price, try to extract from any available field
                    if hotel['price'] == 0 and 'price' in str(hotel).lower():
                        import re
                        price_matches = re.findall(r'\$?(\d+)', str(hotel))
                        if price_matches:
                            hotel['price'] = float(price_matches[0])
            
            # Save top 5 hotels to database (2 cheapest + 3 best rated)
            if hotels:
                try:
                    # Prepare hotel data for database
                    hotels_for_db = []
                    for hotel in hotels:
                        # Determine platform from URL
                        url = hotel.get('url', '').lower()
                        source = hotel.get('source', '').lower()
                        
                        # Handle price being None
                        price = hotel.get('price')
                        if price is None:
                            price = 0
                        
                        hotels_for_db.append({
                            'name': hotel.get('name', 'Unknown Hotel'),
                            'address': hotel.get('location', hotel.get('address', '')),
                            'check_in_date': request.get('check_in', ''),
                            'check_out_date': request.get('check_out', ''),
                            'price': price,
                            'rating': hotel.get('rating'),
                            'amenities': hotel.get('amenities', []),
                            'source': 'airbnb' if 'airbnb' in url or 'airbnb' in source else 'booking',
                            'property_type': hotel.get('room_type', hotel.get('property_type', 'hotel')),
                            'booking_url': hotel.get('url'),
                            'image_url': hotel.get('image_url'),
                            'reviews_count': hotel.get('reviews_count')
                        })
                    
                    # Save to database (top 5: 2 cheapest + 3 best rated)
                    hotel_ids = await self.repository.create_hotels_batch(
                        hotels_for_db,
                        itinerary_id=request.get('itinerary_id')
                    )
                    self.logger.info(f"Saved top {len(hotel_ids)} hotels to database")
                except Exception as e:
                    self.logger.error(f"Failed to save hotels to database: {e}")
                    # Continue anyway - don't block the response
            
            response = {
                'status': 'success',
                'hotels': hotels,
                'total': len(hotels),
                'best_price': min([h['price'] for h in hotels if h.get('price')], default=None) if hotels else None,
                'analysis': self._analyze_hotels(hotels),
                'recommendations': self._get_recommendations(hotels, request),
                'filters': self._get_available_filters(hotels),
                'search_urls': url_results
            }
            
            self.logger.info(f"Found {len(hotels)} hotels")
            
            return response
            
        except Exception as e:
            print(f"DEBUG: Exception occurred: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"DEBUG: Traceback:\n{traceback.format_exc()}")
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
        
        # Count by price range - handle None values properly
        budget = len([h for h in hotels if h.get('price') is not None and h.get('price') < 100])
        mid_range = len([h for h in hotels if h.get('price') is not None and 100 <= h.get('price') < 200])
        luxury = len([h for h in hotels if h.get('price') is not None and h.get('price') >= 200])
        
        # Amenities frequency
        all_amenities = []
        for hotel in hotels:
            all_amenities.extend(hotel.get('amenities', []))
        
        amenity_counts = {}
        for amenity in all_amenities:
            amenity_counts[amenity] = amenity_counts.get(amenity, 0) + 1
            
        # Top amenities
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
        
        # Cheapest option (only consider hotels with valid prices)
        hotels_with_price = [h for h in hotels if h.get('price') and h.get('price') > 0]
        if hotels_with_price:
            cheapest = min(hotels_with_price, key=lambda h: h.get('price', float('inf')))
            recommendations['cheapest'] = {
                'hotel': cheapest,
                'reason': f"Lowest price at {cheapest.get('price_formatted', 'N/A')}"
            }
        else:
            # Fallback if no valid prices
            if hotels:
                cheapest = hotels[0]
                recommendations['cheapest'] = {
                    'hotel': cheapest,
                    'reason': "Price information not available"
                }
        
        # Best rated (if ratings available)
        rated_hotels = [h for h in hotels if h.get('rating')]
        if rated_hotels:
            best_rated = max(rated_hotels, key=lambda h: h.get('rating', 0))
            recommendations['best_rated'] = {
                'hotel': best_rated,
                'reason': f"Highest rating of {best_rated.get('rating')}/10 with {best_rated.get('reviews_count', 0)} reviews"
            }
            
        # Best value (balance of price, rating, and amenities)
        for hotel in hotels:
            score = 100
            
            # Price factor
            if hotels_with_price:
                min_price = min([h.get('price', 1) for h in hotels_with_price])
                if min_price == 0:
                    min_price = 1  # Avoid division by zero
                if hotel.get('price') and hotel.get('price') > 0:
                    price_ratio = hotel.get('price') / min_price
                    score -= (price_ratio - 1) * 20
            else:
                # No price info available, skip price factor
                pass
            
            # Rating factor
            if hotel.get('rating'):
                score += hotel.get('rating', 0) * 5
                
            # Amenities factor
            amenity_count = len(hotel.get('amenities', []))
            score += amenity_count * 2
            
            # Reviews factor
            reviews = hotel.get('reviews_count')
            if reviews and reviews > 100:
                score += 10
                
            hotel['value_score'] = score
            
        best_value = max(hotels, key=lambda h: h.get('value_score', 0))
        recommendations['best_value'] = {
            'hotel': best_value,
            'reason': "Best combination of price, rating, and amenities"
        }
        
        # Best for business
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
            
        # Best location (closest to center)
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
            
        # Collect unique values
        amenities = set()
        locations = set()
        room_types = set()
        
        for hotel in hotels:
            # Amenities
            for amenity in hotel.get('amenities', []):
                amenities.add(amenity)
                
            # Location
            if hotel.get('location'):
                locations.add(hotel['location'])
                
            # Room type
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
                # Extract main location part
                loc = hotel['location'].split(',')[0].strip()
                locations.add(loc)
        return sorted(list(locations))[:10]  # Top 10 locations
    
    def _extract_price_value(self, price_str: str) -> float:
        """Extract numeric price from string like '$150' or '150 USD'"""
        import re
        if not price_str:
            return 0
        # Extract numbers from string
        numbers = re.findall(r'\d+', price_str)
        if numbers:
            return float(numbers[0])
        return 0


# Global hotel service instance
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
    
    # Build request object for hotel service
    request = {
        'destination': destination,
        'check_in': check_in,
        'check_out': check_out,
        'adults': adults,
        'rooms': rooms,
        'children': 0
    }
    
    # Get hotel service and search
    hotel_service = await get_global_hotel_service()
    result = await hotel_service.search(request)
    
    # Store result in context state if ctx is provided
    if ctx and hasattr(ctx, 'store'):
        try:
            async with ctx.store.edit_state() as ctx_state:
                if "state" not in ctx_state:
                    ctx_state["state"] = {}
                ctx_state["state"]["hotels"] = result
        except Exception as e:
            # Log but don't fail if context storage fails
            pass
    
    return json.dumps(result, indent=2)