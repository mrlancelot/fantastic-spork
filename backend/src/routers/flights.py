"""Flight Services Router - Amadeus Integration"""

from fastapi import APIRouter, HTTPException
from typing import Optional
from ..services.flights import (
    AmadeusFlightService,
    FlightSearchRequest,
    FlexibleFlightSearch,
    FlexibleSearchRequest,
    CheapestDateSearch,
    CheapestDateSearchRequest
)
from ..services.travel_services import (
    FlightStatusService,
    FlightStatusRequest,
    CheckInLinksService,
    CheckInLinksRequest
)

router = APIRouter()

@router.post("/search")
async def search_flights(request: FlightSearchRequest):
    """
    Search flights using Amadeus GDS
    Real-time flight data, no mock responses
    """
    try:
        service = AmadeusFlightService()
        result = await service.search(request)
        
        if not result.outbound_flights:
            raise HTTPException(
                status_code=404,
                detail="No flights found for the given criteria"
            )
        
        return {
            "status": "success",
            "data": result.dict()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Amadeus API error: {str(e)}"
        )

@router.post("/flexible")
async def search_flexible_dates(request: FlexibleSearchRequest):
    """Search for cheapest dates within a month"""
    try:
        service = FlexibleFlightSearch()
        result = await service.search_flexible_dates(request)
        
        if not result.all_options:
            raise HTTPException(
                status_code=404,
                detail="No flexible date options found"
            )
        
        return {
            "status": "success",
            "data": result.dict()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Flexible search error: {str(e)}"
        )

@router.post("/cheapest-dates")
async def search_cheapest_dates(request: CheapestDateSearchRequest):
    """Find cheapest travel dates for a route"""
    try:
        service = CheapestDateSearch()
        result = await service.search_cheapest_dates(request)
        
        if not result.dates:
            raise HTTPException(
                status_code=404,
                detail="No cheap date options found"
            )
        
        return {
            "status": "success",
            "data": result.dict()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Cheapest date search error: {str(e)}"
        )

@router.get("/status")
async def get_flight_status(
    carrier_code: str,
    flight_number: str,
    scheduled_departure_date: str
):
    """Get real-time flight status from Amadeus"""
    try:
        request = FlightStatusRequest(
            carrier_code=carrier_code,
            flight_number=flight_number,
            scheduled_departure_date=scheduled_departure_date
        )
        service = FlightStatusService()
        result = await service.get_flight_status(request)
        
        return {
            "status": "success",
            "data": result.dict()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Flight status error: {str(e)}"
        )

@router.get("/checkin-links")
async def get_checkin_links(airline_code: str):
    """Get airline check-in links"""
    try:
        request = CheckInLinksRequest(airline_code=airline_code)
        service = CheckInLinksService()
        result = await service.get_checkin_links(request)
        
        return {
            "status": "success",
            "data": result.dict()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Check-in links error: {str(e)}"
        )