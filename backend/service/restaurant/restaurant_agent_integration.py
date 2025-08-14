import logging
from typing import Dict, Any, List
from llama_index.core.workflow import Context
from service.restaurant.restaurant_service import RestaurantFinder
from service.restaurant.models import UserPreferences, Restaurant

logger = logging.getLogger(__name__)

async def call_restaurant_service_ddgs(ctx: Context, query: str) -> Dict[str, Any]:
    try:
        # Initialize the restaurant finder
        finder = RestaurantFinder()
        
        # Parse the query to extract location and preferences
        prefs = _parse_query_to_preferences(query)
        
        # Use itinerary mode for pre-planning
        response = await finder.find_restaurants(prefs, search_mode="itinerary")
        
        # Convert to format expected by itinerary writer
        result = {
            "restaurants": [
                {
                    "name": r.name,
                    "cuisine": r.description[:100] if r.description else "Various",
                    "rating": r.rating,
                    "location": r.address or prefs.city,
                    "lunch_budget": _price_to_budget(r.price_level, "lunch"),
                    "dinner_budget": _price_to_budget(r.price_level, "dinner"),
                    "link": r.source_urls[0] if r.source_urls else None,
                    "source": "DDGS + Gemini Analysis",
                    "why_recommended": r.why_recommended,
                    "match_score": r.match_score
                }
                for r in response.restaurants[:10]  # Limit to top 10
            ],
            "metadata": {
                "total_found": response.total_results_found,
                "search_time": response.search_metadata.get("search_time_seconds", 0),
                "from_cache": response.search_metadata.get("from_cache", False)
            }
        }
        
        # Store in context
        async with ctx.store.edit_state() as ctx_state:
            ctx_state["state"]["restaurants"] = result
            
        logger.info(f"DDGS restaurant service found {len(result['restaurants'])} restaurants")
        return result
        
    except Exception as e:
        logger.error(f"Error in DDGS restaurant service: {e}")
        return {"restaurants": [], "error": str(e)}

def _parse_query_to_preferences(query: str) -> UserPreferences:
    """Parse natural language query to UserPreferences.
    
    This is a simple parser that extracts common patterns.
    In production, you might want to use an LLM for better parsing.
    """
    query_lower = query.lower()
    
    # Extract city (common patterns)
    city = "Unknown"
    city_keywords = ["in ", "at ", "near ", "around "]
    for keyword in city_keywords:
        if keyword in query_lower:
            parts = query_lower.split(keyword)
            if len(parts) > 1:
                # Take the next word(s) as city
                city_part = parts[1].split()[0:2]  # Take up to 2 words
                city = " ".join(city_part).strip(",. ")
                break
    
    # Extract food type
    food_type = "restaurant"
    food_keywords = ["italian", "japanese", "chinese", "thai", "korean", "french", 
                     "mexican", "indian", "vietnamese", "american", "sushi", "ramen",
                     "pizza", "burger", "steak", "seafood", "vegetarian", "vegan"]
    for keyword in food_keywords:
        if keyword in query_lower:
            food_type = keyword
            break
    
    # Extract budget
    budget_level = "$$"
    if "cheap" in query_lower or "budget" in query_lower or "affordable" in query_lower:
        budget_level = "$"
    elif "expensive" in query_lower or "luxury" in query_lower or "high-end" in query_lower:
        budget_level = "$$$$"
    elif "upscale" in query_lower or "fine dining" in query_lower:
        budget_level = "$$$"
    
    # Extract party size
    party_size = 2  # Default
    import re
    size_match = re.search(r'(\d+)\s*people|party of\s*(\d+)|group of\s*(\d+)', query_lower)
    if size_match:
        for group in size_match.groups():
            if group:
                party_size = int(group)
                break
    
    # Extract dietary restrictions
    dietary_restrictions = []
    dietary_keywords = {
        "vegetarian": "vegetarian",
        "vegan": "vegan",
        "halal": "halal",
        "kosher": "kosher",
        "gluten-free": "gluten-free",
        "gluten free": "gluten-free"
    }
    for keyword, restriction in dietary_keywords.items():
        if keyword in query_lower:
            dietary_restrictions.append(restriction)
    
    return UserPreferences(
        city=city.title(),
        food_type=food_type,
        party_size=party_size,
        budget_level=budget_level,
        dietary_restrictions=dietary_restrictions
    )

def _price_to_budget(price_level: str, meal_type: str) -> str:
    """Convert price level to budget string."""
    if not price_level:
        return "$15-30" if meal_type == "lunch" else "$30-50"
    
    price_map = {
        "$": ("$10-15", "$15-25"),
        "$$": ("$15-25", "$25-40"),
        "$$$": ("$25-40", "$40-70"),
        "$$$$": ("$40+", "$70+")
    }
    
    lunch_price, dinner_price = price_map.get(price_level, ("$15-30", "$30-50"))
    return lunch_price if meal_type == "lunch" else dinner_price