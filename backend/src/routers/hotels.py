"""Hotel Services Router - Amadeus Integration"""

from fastapi import APIRouter, HTTPException
from typing import Optional
from ..services.travel_services import (
    HotelSearchService,
    HotelSearchRequest
)
from ..services.market_insights import (
    MarketInsightsService,
    HotelSentimentsRequest
)

router = APIRouter()

@router.post("/search")
async def search_hotels(request: HotelSearchRequest):
    """
    Search hotels using Amadeus GDS
    Real-time hotel availability and pricing
    """
    try:
        service = HotelSearchService()
        result = await service.search_hotels(request)
        
        if not result.hotels:
            raise HTTPException(
                status_code=404,
                detail="No hotels found for the given criteria"
            )
        
        return {
            "status": "success",
            "data": result.dict()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Hotel search error: {str(e)}"
        )

@router.get("/search")
async def search_hotels_get(
    city_code: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    check_in_date: str = None,
    check_out_date: str = None,
    adults: int = 1,
    rooms: int = 1
):
    """Search hotels - GET endpoint"""
    if not city_code and not (latitude and longitude):
        raise HTTPException(
            status_code=400,
            detail="Either city_code or latitude/longitude required"
        )
    
    if not check_in_date or not check_out_date:
        raise HTTPException(
            status_code=400,
            detail="check_in_date and check_out_date are required"
        )
    
    request = HotelSearchRequest(
        city_code=city_code,
        latitude=latitude,
        longitude=longitude,
        check_in_date=check_in_date,
        check_out_date=check_out_date,
        adults=adults,
        rooms=rooms
    )
    
    return await search_hotels(request)

@router.post("/sentiments")
async def get_hotel_sentiments(request: HotelSentimentsRequest):
    """Get hotel sentiment analysis from Amadeus"""
    try:
        service = MarketInsightsService()
        result = await service.get_hotel_sentiments(request)
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Hotel sentiments error: {str(e)}"
        )