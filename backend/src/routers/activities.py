"""Activities and Tours Router - Amadeus Integration"""

from fastapi import APIRouter, HTTPException
from ..services.travel_services import (
    ActivitySearchService,
    ActivitySearchRequest
)

router = APIRouter()

@router.post("/search")
async def search_activities(request: ActivitySearchRequest):
    """
    Search activities and tours using Amadeus
    Real-time availability from global suppliers
    """
    try:
        service = ActivitySearchService()
        result = await service.search_activities(request)
        
        if not result.activities:
            raise HTTPException(
                status_code=404,
                detail="No activities found for this location"
            )
        
        return {
            "status": "success",
            "data": result.dict()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Activity search error: {str(e)}"
        )

@router.get("/search")
async def search_activities_get(
    latitude: float,
    longitude: float,
    radius: int = 5,
    adults: int = 1
):
    """Search activities - GET endpoint"""
    request = ActivitySearchRequest(
        latitude=latitude,
        longitude=longitude,
        radius=radius,
        adults=adults
    )
    
    return await search_activities(request)