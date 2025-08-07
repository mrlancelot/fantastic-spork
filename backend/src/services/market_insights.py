"""Amadeus Market Insights and Analytics APIs"""

import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from amadeus import Client, ResponseError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============== FLIGHT INSPIRATION MODELS ==============
class FlightInspirationRequest(BaseModel):
    origin: str
    max_price: Optional[int] = None
    departure_date: Optional[str] = None
    one_way: bool = False
    duration: Optional[int] = None  # Trip duration in days
    direct: bool = False
    non_stop: bool = False

class InspirationDestination(BaseModel):
    destination: str
    destination_name: str
    departure_date: str
    return_date: Optional[str]
    price: float
    price_formatted: str
    airline: Optional[str]
    direct: bool

class FlightInspirationResponse(BaseModel):
    origin: str
    currency: str
    destinations: List[InspirationDestination]
    total_found: int
    message: Optional[str]


# ============== TRAVEL ANALYTICS MODELS ==============
class TravelAnalyticsRequest(BaseModel):
    origin_city_code: str
    period: str  # Format: YYYY-MM
    max_results: int = 10

class TravelDestination(BaseModel):
    destination: str
    destination_name: str
    travelers: Optional[int]
    flights: Optional[int]
    percentage: Optional[float]

class MostTraveledResponse(BaseModel):
    origin: str
    period: str
    destinations: List[TravelDestination]
    total_travelers: Optional[int]
    message: Optional[str]

class MostBookedResponse(BaseModel):
    origin: str
    period: str
    destinations: List[TravelDestination]
    message: Optional[str]


# ============== BUSIEST PERIOD MODELS ==============
class BusiestPeriodRequest(BaseModel):
    city_code: str
    period: str  # Format: YYYY
    direction: str = "ARRIVING"  # ARRIVING or DEPARTING

class BusyPeriod(BaseModel):
    period: str
    start_date: str
    end_date: str
    travelers: int
    rank: int

class BusiestPeriodResponse(BaseModel):
    city: str
    year: str
    direction: str
    periods: List[BusyPeriod]
    message: Optional[str]


# ============== FLIGHT DELAY PREDICTION MODELS ==============
class FlightDelayRequest(BaseModel):
    origin: str
    destination: str
    departure_date: str
    departure_time: str
    arrival_date: str
    arrival_time: str
    airline_code: str
    flight_number: str
    aircraft_code: Optional[str] = None

class DelayPrediction(BaseModel):
    probability: float
    result: str  # LESS_THAN_30_MINUTES, OVER_30_MINUTES
    confidence: float

class FlightDelayResponse(BaseModel):
    flight: str
    prediction: DelayPrediction
    message: Optional[str]


# ============== TRIP PURPOSE PREDICTION MODELS ==============
class TripPurposeRequest(BaseModel):
    origin: str
    destination: str
    departure_date: str
    return_date: str
    search_date: Optional[str] = None  # When the search was made

class PurposePrediction(BaseModel):
    purpose: str  # BUSINESS or LEISURE
    probability: float
    confidence: str  # HIGH, MEDIUM, LOW

class TripPurposeResponse(BaseModel):
    origin: str
    destination: str
    prediction: PurposePrediction
    message: Optional[str]


# ============== AIRPORT ROUTES MODELS ==============
class AirportRoutesRequest(BaseModel):
    airport_code: str
    max_results: int = 50

class Route(BaseModel):
    destination: str
    destination_name: str
    airlines: List[str]
    seasonal: bool

class AirportRoutesResponse(BaseModel):
    origin: str
    origin_name: str
    routes: List[Route]
    total_routes: int
    message: Optional[str]


# ============== HOTEL SENTIMENTS MODELS ==============
class HotelSentimentsRequest(BaseModel):
    hotel_ids: List[str]  # Amadeus hotel IDs

class Sentiment(BaseModel):
    hotel_id: str
    hotel_name: Optional[str]
    overall_rating: float
    total_reviews: int
    sentiments: Dict[str, float]  # category -> score
    positive_aspects: List[str]
    negative_aspects: List[str]

class HotelSentimentsResponse(BaseModel):
    hotels: List[Sentiment]
    message: Optional[str]


# ============== FLIGHT PRICE ANALYSIS MODELS ==============
class PriceAnalysisRequest(BaseModel):
    origin: str
    destination: str
    departure_date: str
    currency: str = "USD"
    one_way: bool = False

class PriceMetrics(BaseModel):
    min_price: float
    max_price: float
    mean_price: float
    median_price: float
    quartile_25: float
    quartile_75: float

class PriceAnalysisResponse(BaseModel):
    origin: str
    destination: str
    departure_date: str
    metrics: PriceMetrics
    currency: str
    message: Optional[str]


# ============== SERVICE IMPLEMENTATIONS ==============

class MarketInsightsService:
    """Amadeus Market Insights Service"""
    
    def __init__(self):
        client_id = os.getenv("AMADEUS_API_KEY")
        client_secret = os.getenv("AMADEUS_Secret")
        
        if not client_id or not client_secret:
            raise ValueError("Amadeus credentials not set")
        
        self.amadeus = Client(
            client_id=client_id,
            client_secret=client_secret,
            hostname='test'
        )
    
    async def get_flight_inspiration(self, request: FlightInspirationRequest) -> FlightInspirationResponse:
        """Get flight inspiration - where can I go?"""
        try:
            params = {
                'origin': request.origin
            }
            
            if request.max_price:
                params['maxPrice'] = request.max_price
            if request.departure_date:
                params['departureDate'] = request.departure_date
            if request.one_way:
                params['oneWay'] = 'true'
            if request.duration:
                params['duration'] = request.duration
            if request.non_stop:
                params['nonStop'] = 'true'
            
            response = self.amadeus.shopping.flight_destinations.get(**params)
            
            destinations = []
            if hasattr(response, 'data'):
                for dest in response.data[:20]:
                    destinations.append(InspirationDestination(
                        destination=dest.get('destination'),
                        destination_name=dest.get('destination'),  # Would need lookup
                        departure_date=dest.get('departureDate'),
                        return_date=dest.get('returnDate'),
                        price=float(dest.get('price', {}).get('total', 0)),
                        price_formatted=f"${float(dest.get('price', {}).get('total', 0)):.0f}",
                        airline=dest.get('links', {}).get('flightOffers'),
                        direct=dest.get('links', {}).get('flightOffers') is not None
                    ))
            
            return FlightInspirationResponse(
                origin=request.origin,
                currency='USD',
                destinations=destinations,
                total_found=len(destinations),
                message=f"Found {len(destinations)} destinations within your criteria"
            )
            
        except ResponseError as e:
            logger.error(f"Flight inspiration error: {e}")
            return FlightInspirationResponse(
                origin=request.origin,
                currency='USD',
                destinations=[],
                total_found=0,
                message=f"Error getting flight inspiration: {str(e)}"
            )
    
    async def get_most_traveled(self, request: TravelAnalyticsRequest) -> MostTraveledResponse:
        """Get most traveled destinations from a city"""
        try:
            response = self.amadeus.travel.analytics.air_traffic.traveled.get(
                originCityCode=request.origin_city_code,
                period=request.period,
                max=request.max_results
            )
            
            destinations = []
            total = 0
            
            if hasattr(response, 'data'):
                for dest in response.data:
                    analytics = dest.get('analytics', {})
                    travelers = analytics.get('travelers', {}).get('score', 0)
                    total += travelers
                    
                    destinations.append(TravelDestination(
                        destination=dest.get('destination'),
                        destination_name=dest.get('destination'),
                        travelers=travelers,
                        flights=analytics.get('flights', {}).get('score'),
                        percentage=None
                    ))
            
            # Calculate percentages
            for dest in destinations:
                if dest.travelers and total > 0:
                    dest.percentage = (dest.travelers / total) * 100
            
            return MostTraveledResponse(
                origin=request.origin_city_code,
                period=request.period,
                destinations=destinations,
                total_travelers=total,
                message=f"Top {len(destinations)} traveled destinations from {request.origin_city_code}"
            )
            
        except ResponseError as e:
            logger.error(f"Most traveled error: {e}")
            return MostTraveledResponse(
                origin=request.origin_city_code,
                period=request.period,
                destinations=[],
                total_travelers=0,
                message=f"Error getting travel analytics: {str(e)}"
            )
    
    async def get_most_booked(self, request: TravelAnalyticsRequest) -> MostBookedResponse:
        """Get most booked destinations from a city"""
        try:
            response = self.amadeus.travel.analytics.air_traffic.booked.get(
                originCityCode=request.origin_city_code,
                period=request.period,
                max=request.max_results
            )
            
            destinations = []
            
            if hasattr(response, 'data'):
                for dest in response.data:
                    analytics = dest.get('analytics', {})
                    
                    destinations.append(TravelDestination(
                        destination=dest.get('destination'),
                        destination_name=dest.get('destination'),
                        travelers=analytics.get('travelers', {}).get('score'),
                        flights=analytics.get('flights', {}).get('score'),
                        percentage=None
                    ))
            
            return MostBookedResponse(
                origin=request.origin_city_code,
                period=request.period,
                destinations=destinations,
                message=f"Top {len(destinations)} booked destinations from {request.origin_city_code}"
            )
            
        except ResponseError as e:
            logger.error(f"Most booked error: {e}")
            return MostBookedResponse(
                origin=request.origin_city_code,
                period=request.period,
                destinations=[],
                message=f"Error getting booking analytics: {str(e)}"
            )
    
    async def get_busiest_period(self, request: BusiestPeriodRequest) -> BusiestPeriodResponse:
        """Get busiest travel periods for a city"""
        try:
            response = self.amadeus.travel.analytics.air_traffic.busiest_period.get(
                cityCode=request.city_code,
                period=request.period,
                direction=request.direction
            )
            
            periods = []
            
            if hasattr(response, 'data'):
                for i, period_data in enumerate(response.data):
                    periods.append(BusyPeriod(
                        period=period_data.get('period'),
                        start_date=period_data.get('period', '').split('/')[0] if '/' in period_data.get('period', '') else period_data.get('period'),
                        end_date=period_data.get('period', '').split('/')[1] if '/' in period_data.get('period', '') else period_data.get('period'),
                        travelers=period_data.get('analytics', {}).get('travelers', {}).get('score', 0),
                        rank=i + 1
                    ))
            
            return BusiestPeriodResponse(
                city=request.city_code,
                year=request.period,
                direction=request.direction,
                periods=periods,
                message=f"Top {len(periods)} busiest periods for {request.city_code}"
            )
            
        except ResponseError as e:
            logger.error(f"Busiest period error: {e}")
            return BusiestPeriodResponse(
                city=request.city_code,
                year=request.period,
                direction=request.direction,
                periods=[],
                message=f"Error getting busiest periods: {str(e)}"
            )
    
    async def predict_flight_delay(self, request: FlightDelayRequest) -> FlightDelayResponse:
        """Predict flight delay probability"""
        try:
            params = {
                'originLocationCode': request.origin,
                'destinationLocationCode': request.destination,
                'departureDate': request.departure_date,
                'departureTime': request.departure_time,
                'arrivalDate': request.arrival_date,
                'arrivalTime': request.arrival_time,
                'aircraftCode': request.aircraft_code or '320',
                'carrierCode': request.airline_code,
                'flightNumber': request.flight_number
            }
            
            response = self.amadeus.travel.predictions.flight_delay.get(**params)
            
            if hasattr(response, 'data') and response.data:
                pred_data = response.data[0]
                
                prediction = DelayPrediction(
                    probability=pred_data.get('probability', 0),
                    result=pred_data.get('result', 'UNKNOWN'),
                    confidence=pred_data.get('probability', 0)
                )
                
                return FlightDelayResponse(
                    flight=f"{request.airline_code}{request.flight_number}",
                    prediction=prediction,
                    message="Delay prediction calculated"
                )
            
            return FlightDelayResponse(
                flight=f"{request.airline_code}{request.flight_number}",
                prediction=DelayPrediction(probability=0.5, result="UNKNOWN", confidence=0.5),
                message="Unable to predict delay"
            )
            
        except ResponseError as e:
            logger.error(f"Delay prediction error: {e}")
            return FlightDelayResponse(
                flight=f"{request.airline_code}{request.flight_number}",
                prediction=DelayPrediction(probability=0.5, result="UNKNOWN", confidence=0.5),
                message=f"Error predicting delay: {str(e)}"
            )
    
    async def predict_trip_purpose(self, request: TripPurposeRequest) -> TripPurposeResponse:
        """Predict if trip is business or leisure"""
        try:
            params = {
                'originLocationCode': request.origin,
                'destinationLocationCode': request.destination,
                'departureDate': request.departure_date,
                'returnDate': request.return_date
            }
            
            if request.search_date:
                params['searchDate'] = request.search_date
            
            response = self.amadeus.travel.predictions.trip_purpose.get(**params)
            
            if hasattr(response, 'data') and response.data:
                pred_data = response.data[0]
                result = pred_data.get('result', 'LEISURE')
                probability = pred_data.get('probability', 0.5)
                
                confidence = 'HIGH' if probability > 0.8 else 'MEDIUM' if probability > 0.6 else 'LOW'
                
                prediction = PurposePrediction(
                    purpose=result,
                    probability=probability,
                    confidence=confidence
                )
                
                return TripPurposeResponse(
                    origin=request.origin,
                    destination=request.destination,
                    prediction=prediction,
                    message=f"Trip likely for {result.lower()} ({probability*100:.0f}% confidence)"
                )
            
            return TripPurposeResponse(
                origin=request.origin,
                destination=request.destination,
                prediction=PurposePrediction(purpose="LEISURE", probability=0.5, confidence="LOW"),
                message="Unable to predict trip purpose"
            )
            
        except ResponseError as e:
            logger.error(f"Trip purpose prediction error: {e}")
            return TripPurposeResponse(
                origin=request.origin,
                destination=request.destination,
                prediction=PurposePrediction(purpose="LEISURE", probability=0.5, confidence="LOW"),
                message=f"Error predicting trip purpose: {str(e)}"
            )
    
    async def get_airport_routes(self, request: AirportRoutesRequest) -> AirportRoutesResponse:
        """Get all routes from an airport"""
        try:
            response = self.amadeus.airport.direct_destinations.get(
                departureAirportCode=request.airport_code,
                max=request.max_results
            )
            
            routes = []
            
            if hasattr(response, 'data'):
                for route_data in response.data:
                    destination = route_data.get('destination')
                    if destination:  # Only add if destination exists
                        routes.append(Route(
                            destination=destination,
                            destination_name=destination,  # Would need additional lookup
                            airlines=[],  # Would need additional lookup
                            seasonal=False
                        ))
            
            return AirportRoutesResponse(
                origin=request.airport_code,
                origin_name=request.airport_code,
                routes=routes,
                total_routes=len(routes),
                message=f"Found {len(routes)} direct routes from {request.airport_code}"
            )
            
        except ResponseError as e:
            logger.error(f"Airport routes error: {e}")
            return AirportRoutesResponse(
                origin=request.airport_code,
                origin_name=request.airport_code,
                routes=[],
                total_routes=0,
                message=f"Error getting airport routes: {str(e)}"
            )
    
    async def get_hotel_sentiments(self, request: HotelSentimentsRequest) -> HotelSentimentsResponse:
        """Get hotel sentiment analysis"""
        try:
            sentiments = []
            
            for hotel_id in request.hotel_ids[:5]:  # Limit to 5 hotels
                try:
                    response = self.amadeus.e_reputation.hotel_sentiments.get(
                        hotelIds=hotel_id
                    )
                    
                    if hasattr(response, 'data') and response.data:
                        sentiment_data = response.data[0]
                        
                        sentiments.append(Sentiment(
                            hotel_id=hotel_id,
                            hotel_name=None,
                            overall_rating=sentiment_data.get('overallRating', 0),
                            total_reviews=sentiment_data.get('numberOfReviews', 0),
                            sentiments=sentiment_data.get('sentiments', {}),
                            positive_aspects=[],
                            negative_aspects=[]
                        ))
                except:
                    continue
            
            return HotelSentimentsResponse(
                hotels=sentiments,
                message=f"Retrieved sentiments for {len(sentiments)} hotels"
            )
            
        except ResponseError as e:
            logger.error(f"Hotel sentiments error: {e}")
            return HotelSentimentsResponse(
                hotels=[],
                message=f"Error getting hotel sentiments: {str(e)}"
            )
    
    async def analyze_flight_prices(self, request: PriceAnalysisRequest) -> PriceAnalysisResponse:
        """Analyze flight price metrics"""
        try:
            params = {
                'originIataCode': request.origin,
                'destinationIataCode': request.destination,
                'departureDate': request.departure_date,
                'currencyCode': request.currency
            }
            
            if request.one_way:
                params['oneWay'] = 'true'
            
            response = self.amadeus.analytics.itinerary_price_metrics.get(**params)
            
            if hasattr(response, 'data') and response.data:
                metrics_data = response.data[0].get('priceMetrics', [{}])[0]
                
                metrics = PriceMetrics(
                    min_price=metrics_data.get('min', 0),
                    max_price=metrics_data.get('max', 0),
                    mean_price=metrics_data.get('mean', 0),
                    median_price=metrics_data.get('median', 0),
                    quartile_25=metrics_data.get('quartile25', 0),
                    quartile_75=metrics_data.get('quartile75', 0)
                )
                
                return PriceAnalysisResponse(
                    origin=request.origin,
                    destination=request.destination,
                    departure_date=request.departure_date,
                    metrics=metrics,
                    currency=request.currency,
                    message="Price analysis complete"
                )
            
            return PriceAnalysisResponse(
                origin=request.origin,
                destination=request.destination,
                departure_date=request.departure_date,
                metrics=PriceMetrics(min_price=0, max_price=0, mean_price=0, median_price=0, quartile_25=0, quartile_75=0),
                currency=request.currency,
                message="No price data available"
            )
            
        except ResponseError as e:
            logger.error(f"Price analysis error: {e}")
            return PriceAnalysisResponse(
                origin=request.origin,
                destination=request.destination,
                departure_date=request.departure_date,
                metrics=PriceMetrics(min_price=0, max_price=0, mean_price=0, median_price=0, quartile_25=0, quartile_75=0),
                currency=request.currency,
                message=f"Error analyzing prices: {str(e)}"
            )