from fastapi import APIRouter, HTTPException
from typing import Optional, List
from pydantic import BaseModel, Field
from service.restaurant.restaurant_service import RestaurantFinder
from service.restaurant.models import UserPreferences

router = APIRouter(tags=["Restaurants - Search & Booking"])

# Request models for different search modes
class ItineraryRestaurantRequest(BaseModel):
    """Request for pre-planned itinerary restaurant search"""
    city: str = Field(description="City to search in (e.g., Tokyo, New York, Paris)")
    food_type: Optional[str] = Field(default="restaurant", description="Type of food/cuisine (e.g., ramen, sushi, italian, thai)")
    party_size: Optional[int] = Field(default=2, description="Number of people (1-20)")
    budget_level: Optional[str] = Field(default="$$", description="Budget level: $ (cheap), $$ (moderate), $$$ (upscale), $$$$ (luxury)")
    occasion: Optional[str] = Field(default=None, description="Special occasion (e.g., anniversary, birthday, business)")
    dietary_restrictions: Optional[List[str]] = Field(default_factory=list, description="Dietary restrictions (e.g., vegetarian, vegan, halal, kosher, gluten-free)")
    allergies: Optional[List[str]] = Field(default_factory=list, description="Food allergies (e.g., peanuts, shellfish, dairy)")
    preferred_ambiance: Optional[List[str]] = Field(default_factory=list, description="Preferred ambiance (e.g., romantic, casual, quiet, lively)")
    must_have: Optional[List[str]] = Field(default_factory=list, description="Must-have features (e.g., english menu, private room, view)")
    avoid: Optional[List[str]] = Field(default_factory=list, description="Things to avoid (e.g., smoking, loud music, chains)")
    special_requirements: Optional[List[str]] = Field(default_factory=list, description="Special requirements (e.g., wheelchair accessible, kid-friendly)")
    time: Optional[str] = Field(default=None, description="Meal time (e.g., lunch, dinner, brunch)")

class NearMeRestaurantRequest(BaseModel):
    """Request for live 'food places near me' search"""
    current_location: str = Field(description="Current location/address (e.g., Shibuya Station, Times Square)")
    city: str = Field(description="Current city")
    food_type: Optional[str] = Field(default="restaurant", description="Type of food desired")
    party_size: Optional[int] = Field(default=1, description="Number of people")
    budget_level: Optional[str] = Field(default="$$", description="Budget level: $ (cheap), $$ (moderate), $$$ (upscale), $$$$ (luxury)")
    dietary_restrictions: Optional[List[str]] = Field(default_factory=list, description="Dietary restrictions")
    allergies: Optional[List[str]] = Field(default_factory=list, description="Food allergies")
    time: Optional[str] = Field(default="now", description="When to eat (now/lunch/dinner)")
    max_distance: Optional[str] = Field(default="walking", description="Maximum distance (walking/5min/10min)")

@router.post("/restaurants/itinerary")
async def search_restaurants_for_itinerary(request: ItineraryRestaurantRequest) -> dict:
    """
    Search for restaurants during trip planning phase.
    Used when creating itineraries and planning ahead.
    """
    try:
        # Convert request to UserPreferences (auto-detect country from city)
        prefs = UserPreferences(
            city=request.city,
            country="",  # Will be auto-detected from city
            food_type=request.food_type or "restaurant",
            party_size=request.party_size or 2,
            occasion=request.occasion,
            budget_level=request.budget_level or "$$",
            dietary_restrictions=request.dietary_restrictions or [],
            allergies=request.allergies or [],
            preferred_ambiance=request.preferred_ambiance or [],
            must_have=request.must_have or [],
            avoid=request.avoid or [],
            special_requirements=request.special_requirements or [],
            time=request.time
        )
        
        # Use restaurant finder with itinerary mode
        finder = RestaurantFinder()
        result = await finder.find_restaurants(prefs, search_mode="itinerary")
        
        return {
            "status": "success",
            "mode": "itinerary_planning",
            "result": result.dict(),
            "message": f"Found {len(result.restaurants)} restaurants for your itinerary"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Itinerary restaurant search failed: {str(e)}")

@router.post("/restaurants/near-me")
async def search_restaurants_near_me(request: NearMeRestaurantRequest) -> dict:
    """
    Search for restaurants near current location.
    Used when users are at a location and want immediate dining options.
    """
    try:
        # Convert request to UserPreferences with location focus
        prefs = UserPreferences(
            city=f"{request.current_location}, {request.city}",  # Include specific location
            country="",  # Will be auto-detected from city
            food_type=request.food_type or "restaurant",
            party_size=request.party_size or 1,
            budget_level=request.budget_level or "$$",
            dietary_restrictions=request.dietary_restrictions or [],
            allergies=request.allergies or [],
            time=request.time or "now",
            special_requirements=[f"within {request.max_distance}"] if request.max_distance else []
        )
        
        # Use restaurant finder with near_me mode
        finder = RestaurantFinder()
        result = await finder.find_restaurants(prefs, search_mode="near_me")
        
        return {
            "status": "success",
            "mode": "near_me",
            "result": result.dict(),
            "message": f"Found {len(result.restaurants)} restaurants near your location"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Near me restaurant search failed: {str(e)}")

