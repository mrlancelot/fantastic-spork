from fastapi import APIRouter, HTTPException
from typing import Optional
from agents.restaurant_agent import RestaurantAgent
from schemas import PriceRange

router = APIRouter(tags=["Restaurants - Search & Booking"])


@router.get("/restaurants")
async def restaurants(query: str = "What are the top rated restaurants in Tokyo", price_range: Optional[PriceRange] = None, stream: bool = False) -> dict:
    try:
        restaurant_agent = RestaurantAgent()
        result = await restaurant_agent.scrape_restaurants(query, stream, price_range)
        
        # Debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Result type: {type(result)}")
        logger.info(f"Result content: {result}")
        
        # Handle both RestaurantOutput object and dict responses
        if hasattr(result, 'restaurants'):
            # It's a RestaurantOutput object
            logger.info(f"RestaurantOutput detected with {len(result.restaurants)} restaurants")
            restaurants_data = [r.dict() if hasattr(r, 'dict') else r for r in result.restaurants]
        elif isinstance(result, dict) and 'restaurants' in result:
            # It's already a dict with restaurants
            logger.info(f"Dict response detected with restaurants key")
            restaurants_data = result['restaurants']
        else:
            # Fallback - treat the whole result as the response
            logger.warning(f"Unexpected result format: {type(result)}")
            restaurants_data = result if isinstance(result, list) else []
        
        return {
            "status": "success",
            "restaurants": restaurants_data,
            "total": len(restaurants_data),
            "message": "Restaurant search completed"
        }
    except Exception as e:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Restaurant search error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Restaurant search failed: {str(e)}")
