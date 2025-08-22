from fastapi import APIRouter, HTTPException
import json
from typing import Optional

from service.hotel_service import call_hotel_service

router = APIRouter(tags=["Hotels - Search & Booking"])


@router.get("/hotels")
async def get_hotels(
    destination: str = "Tokyo",
    check_in: str = "2025-11-11",
    check_out: str = "2025-11-18",
    adults: int = 2,
    rooms: int = 1
) -> dict:
    try:
        result_json = await call_hotel_service(
            destination=destination,
            check_in=check_in,
            check_out=check_out,
            adults=adults,
            rooms=rooms
        )
        result = json.loads(result_json)
        return {
            "status": "success",
            "hotels": result.get("hotels", []),
            "total_found": result.get("total", 0),
            "best_price": result.get("best_price"),
            "analysis": result.get("analysis", {}),
            "recommendations": result.get("recommendations", {}),
            "filters": result.get("filters", {}),
            "request_details": {
                "destination": destination,
                "check_in": check_in,
                "check_out": check_out,
                "adults": adults,
                "rooms": rooms
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hotel search failed: {str(e)}")