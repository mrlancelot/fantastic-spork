"""
Restaurant Service Layer
Uses existing Tavily-based restaurant search
"""

from typing import Dict, List, Optional
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from core.logger import setup_logger

# Import existing restaurant agent
try:
    from services.restaurant_agent import RestaurantAgent
except ImportError:
    # Fallback if the import path is different
    try:
        from restaurant_agent import RestaurantAgent
    except ImportError:
        RestaurantAgent = None


class RestaurantService:
    """Service layer for restaurant searches using Tavily"""
    
    def __init__(self):
        self.logger = setup_logger('RestaurantService')
        self.agent = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize the restaurant agent"""
        if not self.initialized:
            if RestaurantAgent:
                self.agent = RestaurantAgent()
                await self.agent.initialize()
                self.initialized = True
                self.logger.info("Restaurant service initialized with Tavily")
            else:
                self.logger.warning("RestaurantAgent not available, using mock data")
                self.initialized = True
                
    async def search(self, request: Dict) -> Dict:
        """
        Search restaurants using Tavily
        
        Args:
            request: {
                'destination': str,
                'cuisine': Optional[str],
                'query': Optional[str]
            }
        """
        destination = request.get('destination', '')
        query = request.get('query', f"best restaurants in {destination}")
        
        self.logger.info(f"Searching restaurants: {query}")
        
        # Ensure agent is initialized
        await self.initialize()
        
        try:
            if self.agent:
                # Use existing Tavily agent
                response = await self.agent.scrape_restaurants(query=query)
                
                # Extract restaurants from response
                restaurants = []
                if hasattr(response, 'restaurants'):
                    restaurants = response.restaurants
                elif isinstance(response, dict):
                    restaurants = response.get('restaurants', [])
                    
                # Process restaurants
                processed = self._process_restaurants(restaurants)
                
                self.logger.info(f"Found {len(processed)} restaurants via Tavily")
                
                return {
                    'status': 'success',
                    'total': len(processed),
                    'restaurants': processed,
                    'source': 'Tavily Web Search',
                    'analysis': self._analyze_restaurants(processed),
                    'recommendations': self._get_recommendations(processed, request)
                }
            else:
                # Return mock data if Tavily not available
                return self._get_mock_restaurants(destination)
                
        except Exception as e:
            self.logger.error(f"Restaurant search error: {e}", exc_info=True)
            return {
                'status': 'error',
                'error': str(e),
                'restaurants': [],
                'total': 0
            }
            
    def _process_restaurants(self, restaurants: List) -> List[Dict]:
        """Process and format restaurant data"""
        processed = []
        
        for r in restaurants[:20]:  # Limit to top 20
            # Handle different data formats
            if hasattr(r, '__dict__'):
                restaurant = r.__dict__
            elif isinstance(r, dict):
                restaurant = r
            else:
                continue
                
            # Ensure required fields
            processed_restaurant = {
                'name': restaurant.get('name', 'Unknown'),
                'cuisine': restaurant.get('cuisine', 'International'),
                'rating': restaurant.get('rating', 0),
                'price_level': restaurant.get('price_level', '$$'),
                'address': restaurant.get('address', ''),
                'description': restaurant.get('description', ''),
                'link': restaurant.get('link', ''),
                'phone': restaurant.get('phone', ''),
                'hours': restaurant.get('hours', 'Check website'),
                'highlights': restaurant.get('highlights', [])
            }
            
            # Add price description
            processed_restaurant['price_description'] = self._get_price_description(
                processed_restaurant['price_level']
            )
            
            processed.append(processed_restaurant)
            
        # Sort by rating
        processed.sort(key=lambda x: x.get('rating', 0), reverse=True)
        
        return processed
        
    def _analyze_restaurants(self, restaurants: List[Dict]) -> Dict:
        """Analyze restaurant data"""
        if not restaurants:
            return {}
            
        # Cuisine distribution
        cuisines = {}
        for r in restaurants:
            cuisine = r.get('cuisine', 'Unknown')
            cuisines[cuisine] = cuisines.get(cuisine, 0) + 1
            
        # Price distribution
        price_levels = {}
        for r in restaurants:
            level = r.get('price_level', '$$')
            price_levels[level] = price_levels.get(level, 0) + 1
            
        # Rating stats
        ratings = [r.get('rating', 0) for r in restaurants if r.get('rating')]
        
        return {
            'cuisine_types': dict(sorted(cuisines.items(), key=lambda x: x[1], reverse=True)[:5]),
            'price_distribution': price_levels,
            'rating_stats': {
                'avg': sum(ratings) / len(ratings) if ratings else 0,
                'max': max(ratings) if ratings else 0,
                'min': min(ratings) if ratings else 0
            },
            'total_restaurants': len(restaurants)
        }
        
    def _get_recommendations(self, restaurants: List[Dict], request: Dict) -> Dict:
        """Get restaurant recommendations"""
        if not restaurants:
            return {}
            
        recommendations = {}
        
        # Top rated
        if restaurants:
            top_rated = restaurants[0]  # Already sorted by rating
            recommendations['top_rated'] = {
                'restaurant': top_rated,
                'reason': f"Highest rated at {top_rated.get('rating', 'N/A')}/5"
            }
            
        # Best for specific cuisine
        cuisine = request.get('cuisine')
        if cuisine:
            cuisine_matches = [
                r for r in restaurants 
                if cuisine.lower() in r.get('cuisine', '').lower()
            ]
            if cuisine_matches:
                recommendations['best_cuisine_match'] = {
                    'restaurant': cuisine_matches[0],
                    'reason': f"Best {cuisine} restaurant"
                }
                
        # Budget friendly
        budget_options = [
            r for r in restaurants 
            if r.get('price_level') in ['$', '$$']
        ]
        if budget_options:
            recommendations['budget_friendly'] = {
                'restaurant': budget_options[0],
                'reason': "Great food at reasonable prices"
            }
            
        # Fine dining
        fine_dining = [
            r for r in restaurants 
            if r.get('price_level') in ['$$$', '$$$$']
        ]
        if fine_dining:
            recommendations['fine_dining'] = {
                'restaurant': fine_dining[0],
                'reason': "Upscale dining experience"
            }
            
        return recommendations
        
    def _get_price_description(self, price_level: str) -> str:
        """Convert price level to description"""
        descriptions = {
            '$': 'Budget-friendly',
            '$$': 'Moderate',
            '$$$': 'Upscale',
            '$$$$': 'Fine dining'
        }
        return descriptions.get(price_level, 'Moderate')
        
    def _get_mock_restaurants(self, destination: str) -> Dict:
        """Return mock restaurants if Tavily not available"""
        mock_restaurants = [
            {
                'name': f'The Local Kitchen - {destination}',
                'cuisine': 'Local Cuisine',
                'rating': 4.5,
                'price_level': '$$',
                'address': f'123 Main St, {destination}',
                'description': 'Authentic local flavors in a cozy setting',
                'link': '#',
                'price_description': 'Moderate'
            },
            {
                'name': f'Sunset Grill - {destination}',
                'cuisine': 'International',
                'rating': 4.3,
                'price_level': '$$$',
                'address': f'456 Ocean Blvd, {destination}',
                'description': 'Fine dining with panoramic views',
                'link': '#',
                'price_description': 'Upscale'
            },
            {
                'name': f'Street Food Market - {destination}',
                'cuisine': 'Street Food',
                'rating': 4.7,
                'price_level': '$',
                'address': f'Downtown Market, {destination}',
                'description': 'Diverse street food from local vendors',
                'link': '#',
                'price_description': 'Budget-friendly'
            }
        ]
        
        return {
            'status': 'success',
            'total': len(mock_restaurants),
            'restaurants': mock_restaurants,
            'source': 'Mock Data (Tavily unavailable)',
            'analysis': self._analyze_restaurants(mock_restaurants),
            'recommendations': self._get_recommendations(mock_restaurants, {'destination': destination})
        }