from fastapi import APIRouter, HTTPException
import json
from typing import Optional

from service.flight_service import call_flight_service
from schemas import FlightRequest

router = APIRouter(tags=["Flights - Search & Booking"])


@router.get("/flights")
async def get_flights(
    from_city: str = "SFO",
    to_city: str = "NRT",
    departure_date: str = "2025-11-11",
    return_date: Optional[str] = "2025-11-18",
    adults: int = 1,
    travel_class: str = "economy"
) -> dict:
    """Smart flight search with multiple airports"""
    try:
        result_json = await call_flight_service(from_city, to_city, departure_date, return_date, adults, travel_class)
        result = json.loads(result_json)
        return {
            "status": "success",
            "flights": result.get("flights", []),
            "flight_options": result.get("flight_options", []),
            "total_found": result.get("total", 0),
            "best_price": result.get("best_price"),
            "analysis": result.get("analysis", {}),
            "recommendations": result.get("recommendations", {}),
            "summary": result.get("summary", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flight search failed: {str(e)}")