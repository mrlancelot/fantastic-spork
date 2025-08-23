from fastapi import APIRouter, HTTPException
import json
from typing import Optional
import logging

from service.hotel_service import call_hotel_service
from database.travel_repository import TravelRepository

logger = logging.getLogger(__name__)
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
        # Initialize repository
        repository = TravelRepository()
        
        # Call hotel service to search for hotels
        result_json = await call_hotel_service(
            destination=destination,
            check_in=check_in,
            check_out=check_out,
            adults=adults,
            rooms=rooms
        )
        result = json.loads(result_json)
        
        # Extract hotels from result
        hotels = result.get("hotels", [])
        
        # Save hotels to database if we have results
        saved_hotel_ids = []
        if hotels:
            logger.info(f"Saving {len(hotels)} hotels to database")
            
            # Prepare hotel data for database
            hotels_data = []
            for hotel in hotels:
                hotel_data = {
                    "name": hotel.get("name", "Unknown Hotel"),
                    "address": hotel.get("location", destination),
                    "check_in_date": check_in,
                    "check_out_date": check_out,
                    "price": hotel.get("price") if hotel.get("price") is not None else None,
                    "rating": hotel.get("rating"),
                    "amenities": hotel.get("amenities", []),
                    "source": hotel.get("source", "booking"),
                    "source_url": hotel.get("source_url"),
                    "reviews_count": hotel.get("reviews_count"),
                    "guests": adults,  # Add guests from request
                    "rooms": rooms    # Add rooms from request
                }
                hotels_data.append(hotel_data)
            
            # Save hotels in batch
            saved_hotel_ids = await repository.create_hotels_batch(hotels_data)
            logger.info(f"Successfully saved {len(saved_hotel_ids)} hotels to database")
        
        return {
            "status": "success",
            "hotels": hotels,
            "total_found": result.get("total", 0),
            "best_price": result.get("best_price"),
            "analysis": result.get("analysis", {}),
            "recommendations": result.get("recommendations", {}),
            "filters": result.get("filters", {}),
            "saved_count": len(saved_hotel_ids),
            "request_details": {
                "destination": destination,
                "check_in": check_in,
                "check_out": check_out,
                "adults": adults,
                "rooms": rooms
            }
        }
    except Exception as e:
        logger.error(f"Hotel search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Hotel search failed: {str(e)}")