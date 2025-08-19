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
        return {
            "status": "success",
            "result": result,
            "message": "Restaurant search completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restaurant search failed: {str(e)}")
