import os
import aiohttp
import json
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Restaurant(BaseModel):
    name: str = Field(description="the name of the restaurant")
    cuisine: str = Field(description="the cuisine of the restaurant")
    rating: float = Field(description="the rating of the restaurant")
    location: str = Field(description="the location of the restaurant")
    lunch_budget: str = Field(description="the budget of the restaurant")
    dinner_budget: str = Field(description="the budget of the restaurant")
    link: str = Field(description="the link to the restaurant")

class RestaurantOutput(BaseModel):
    restaurants: List[Restaurant] = Field(description="the list of restaurants")

class RestaurantAgent:
    """Agent for scraping restaurant information using Tavily API directly."""
    
    def __init__(self, api_token: str = None):
        """Initialize the agent with API token."""
        self.api_token = api_token or os.getenv("TAVILY_API_KEY")
        if not self.api_token:
            raise ValueError("TAVILY_API_KEY is required")
        
        self.base_url = "https://api.tavily.com/search"
        self._initialized = False
    
    async def initialize(self):
        """Initialize the agent (compatibility method)."""
        if self._initialized:
            return
        self._initialized = True
        logger.info("Restaurant agent initialized with Tavily API")
    
    async def scrape_restaurants(self, query: str = None, stream: bool = False) -> RestaurantOutput:
        """Search for restaurants using Tavily API."""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Default query if none provided
            if not query:
                query = "Give me the top 3 highest rated restaurants in Tokyo"
            
            # Make sure we're searching for restaurants
            if "restaurant" not in query.lower():
                query = f"restaurants {query}"
            
            logger.info(f"Searching for restaurants: {query}")
            
            # Call Tavily API
            headers = {"Content-Type": "application/json"}
            payload = {
                "api_key": self.api_token,
                "query": query,
                "search_depth": "advanced",
                "include_answer": True,
                "include_raw_content": False,
                "max_results": 10
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=headers, json=payload, timeout=30) as response:
                    if response.status != 200:
                        logger.error(f"Tavily API error: {response.status}")
                        return RestaurantOutput(restaurants=[])
                    
                    data = await response.json()
                    
                    # Parse results
                    restaurants = []
                    
                    # Try to extract restaurants from search results
                    for result in data.get('results', [])[:5]:  # Limit to 5 restaurants
                        try:
                            # Extract restaurant info from the search result
                            title = result.get('title', '')
                            content = result.get('content', '')
                            url = result.get('url', '')
                            
                            # Parse rating if available
                            rating = 4.0  # Default rating
                            if 'rating' in content.lower():
                                # Try to extract rating
                                import re
                                rating_match = re.search(r'(\d+\.?\d*)\s*(?:stars?|rating|\/5)', content.lower())
                                if rating_match:
                                    try:
                                        rating = float(rating_match.group(1))
                                    except:
                                        pass
                            
                            # Extract cuisine type
                            cuisine = "International"
                            cuisine_types = ["italian", "japanese", "chinese", "french", "american", "mexican", 
                                           "thai", "indian", "korean", "vietnamese", "mediterranean", "spanish"]
                            for c in cuisine_types:
                                if c in content.lower() or c in title.lower():
                                    cuisine = c.capitalize()
                                    break
                            
                            # Extract location from content
                            location = "City Center"
                            if 'located' in content.lower():
                                loc_parts = content.lower().split('located')
                                if len(loc_parts) > 1:
                                    location = loc_parts[1].split('.')[0].strip()[:50]
                            
                            # Create restaurant object
                            restaurant = Restaurant(
                                name=title.split('-')[0].strip() if title else f"Restaurant {len(restaurants)+1}",
                                cuisine=cuisine,
                                rating=rating,
                                location=location,
                                lunch_budget="$$",
                                dinner_budget="$$$",
                                link=url
                            )
                            restaurants.append(restaurant)
                            
                        except Exception as e:
                            logger.debug(f"Error parsing restaurant result: {e}")
                            continue
                    
                    # If we didn't get enough restaurants from results, add some from the answer
                    if len(restaurants) < 3 and data.get('answer'):
                        # Parse the answer for restaurant mentions
                        answer = data['answer']
                        lines = answer.split('\n')
                        
                        for line in lines:
                            if len(restaurants) >= 5:
                                break
                            
                            # Look for restaurant names (usually in bold or numbered lists)
                            if any(char in line for char in ['*', '-', '1', '2', '3', '4', '5']):
                                # Extract potential restaurant name
                                import re
                                name_match = re.search(r'[*\-\d.]\s*\*?\*?([^*\-\n]+)', line)
                                if name_match:
                                    name = name_match.group(1).strip()
                                    if len(name) > 3 and len(name) < 100:
                                        # Create a basic restaurant entry
                                        restaurant = Restaurant(
                                            name=name,
                                            cuisine="Various",
                                            rating=4.2,
                                            location="See details",
                                            lunch_budget="$$",
                                            dinner_budget="$$$",
                                            link=f"https://www.google.com/search?q={name.replace(' ', '+')}"
                                        )
                                        
                                        # Avoid duplicates
                                        if not any(r.name == name for r in restaurants):
                                            restaurants.append(restaurant)
                    
                    logger.info(f"Found {len(restaurants)} restaurants")
                    return RestaurantOutput(restaurants=restaurants)
                    
        except Exception as e:
            logger.error(f"Error in scraping restaurants: {e}")
            return RestaurantOutput(restaurants=[])
    
    async def run_custom_query(self, query: str) -> RestaurantOutput:
        """Run a custom query (compatibility method)."""
        return await self.scrape_restaurants(query)


# Convenience function for backward compatibility
async def search_restaurants() -> RestaurantOutput:
    """Legacy function for backward compatibility."""
    try:
        agent = RestaurantAgent()
        return await agent.scrape_restaurants()
    except Exception as e:
        logger.error(f"Error in search_restaurants: {e}")
        return RestaurantOutput(restaurants=[])