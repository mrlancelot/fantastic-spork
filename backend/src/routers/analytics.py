"""Market Analytics Router - Amadeus Intelligence"""

from fastapi import APIRouter, HTTPException
from typing import Optional
from ..services.market_insights import (
    MarketInsightsService,
    FlightInspirationRequest,
    TravelAnalyticsRequest,
    BusiestPeriodRequest,
    FlightDelayRequest,
    TripPurposeRequest,
    AirportRoutesRequest,
    PriceAnalysisRequest
)

router = APIRouter()

@router.get("/flight-inspiration")
async def get_flight_inspiration(
    origin: str,
    max_price: Optional[int] = None,
    departure_date: Optional[str] = None,
    one_way: bool = False,
    duration: Optional[int] = None
):
    """Get flight inspiration - where can I go within budget?"""
    try:
        request = FlightInspirationRequest(
            origin=origin,
            max_price=max_price,
            departure_date=departure_date,
            one_way=one_way,
            duration=duration
        )
        service = MarketInsightsService()
        result = await service.get_flight_inspiration(request)
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Flight inspiration error: {str(e)}"
        )

@router.get("/most-traveled")
async def get_most_traveled(
    origin_city_code: str,
    period: str,
    max_results: int = 10
):
    """Get most traveled destinations from a city"""
    try:
        request = TravelAnalyticsRequest(
            origin_city_code=origin_city_code,
            period=period,
            max_results=max_results
        )
        service = MarketInsightsService()
        result = await service.get_most_traveled(request)
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Travel analytics error: {str(e)}"
        )

@router.get("/most-booked")
async def get_most_booked(
    origin_city_code: str,
    period: str,
    max_results: int = 10
):
    """Get most booked destinations from a city"""
    try:
        request = TravelAnalyticsRequest(
            origin_city_code=origin_city_code,
            period=period,
            max_results=max_results
        )
        service = MarketInsightsService()
        result = await service.get_most_booked(request)
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Booking analytics error: {str(e)}"
        )

@router.get("/busiest-period")
async def get_busiest_period(
    city_code: str,
    period: str,
    direction: str = "ARRIVING"
):
    """Get busiest travel periods for a city"""
    try:
        request = BusiestPeriodRequest(
            city_code=city_code,
            period=period,
            direction=direction
        )
        service = MarketInsightsService()
        result = await service.get_busiest_period(request)
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Busiest period error: {str(e)}"
        )

@router.post("/flight-delay-prediction")
async def predict_flight_delay(request: FlightDelayRequest):
    """ML-powered flight delay prediction"""
    try:
        service = MarketInsightsService()
        result = await service.predict_flight_delay(request)
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Delay prediction error: {str(e)}"
        )

@router.post("/trip-purpose-prediction")
async def predict_trip_purpose(request: TripPurposeRequest):
    """Predict if trip is business or leisure"""
    try:
        service = MarketInsightsService()
        result = await service.predict_trip_purpose(request)
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Trip purpose prediction error: {str(e)}"
        )

@router.get("/airport-routes")
async def get_airport_routes(
    airport_code: str,
    max_results: int = 50
):
    """Get all direct routes from an airport"""
    try:
        request = AirportRoutesRequest(
            airport_code=airport_code,
            max_results=max_results
        )
        service = MarketInsightsService()
        result = await service.get_airport_routes(request)
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Airport routes error: {str(e)}"
        )

@router.post("/price-analysis")
async def analyze_prices(request: PriceAnalysisRequest):
    """Analyze flight price metrics for a route"""
    try:
        service = MarketInsightsService()
        result = await service.analyze_flight_prices(request)
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Price analysis error: {str(e)}"
        )