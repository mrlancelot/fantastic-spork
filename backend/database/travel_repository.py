"""
Travel Repository
Handles all database operations for travel-related data using repository pattern
"""

from typing import List, Optional, Dict, Any
import json
import traceback
import logging
import asyncio
from datetime import datetime
from functools import wraps

from database.models import (
    Itinerary, ItineraryDay, Activity,
    Flight, Hotel, Restaurant, Job
)
from database.convex_manager import get_convex_manager
from database.convex_mapper import (
    to_convex_flight, to_convex_hotel, to_convex_restaurant,
    to_convex_itinerary, to_convex_job, to_convex_itinerary_day,
    to_convex_activity
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def validate_required_fields(fields: List[str]):
    """Decorator to validate required fields in data dictionary"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Find the data argument
            data = None
            if args and isinstance(args[0], dict):
                data = args[0]
            elif 'data' in kwargs:
                data = kwargs['data']
            elif len(args) > 1 and isinstance(args[1], dict):
                data = args[1]
            
            if data:
                missing_fields = [f for f in fields if f not in data or data[f] is None]
                if missing_fields:
                    raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
            
            return await func(self, *args, **kwargs)
        return wrapper
    return decorator


class TravelRepository:
    """Repository for all travel-related database operations"""
    
    def __init__(self):
        logger.info("Initializing TravelRepository")
        self.convex = get_convex_manager()
        self._operation_timeout = 30  # seconds
        # Temporary mapping between our string IDs and Convex IDs
        self._job_id_mapping = {}  # {string_id: convex_id}
        logger.debug(f"Repository initialized with timeout={self._operation_timeout}s")
    
    # ==================== FLIGHT OPERATIONS ====================
    async def create_flights_batch(self, flights: List[Dict[str, Any]], 
                                  itinerary_id: Optional[str] = None) -> List[str]:
        """
        Save top 3 flights sorted by price (ascending)
        
        Args:
            flights: List of flight data dictionaries
            itinerary_id: Optional itinerary to link flights to
            
        Returns:
            List of created flight IDs
        """
        logger.info(f"=== SAVING FLIGHTS BATCH: {len(flights)} flights ===")
        logger.debug(f"Itinerary ID: {itinerary_id}")
        
        if not flights:
            logger.warning("No flights to save")
            return []
        
        # Sort by price and take top 3 cheapest
        sorted_flights = sorted(flights, key=lambda x: x.get('price', float('inf')))[:3]
        logger.info(f"Selected top {len(sorted_flights)} cheapest flights")
        flight_ids = []
        
        for idx, flight_data in enumerate(sorted_flights):
            try:
                # Create flight model
                flight = Flight(
                    itinerary_id=itinerary_id,
                    origin=flight_data.get('origin', ''),
                    destination=flight_data.get('destination', ''),
                    airline=flight_data.get('airline', 'Unknown'),
                    flight_number=flight_data.get('flight_number'),
                    departure_date=flight_data.get('departure_date', ''),
                    arrival_date=flight_data.get('arrival_date'),
                    price=float(flight_data.get('price', 0)),
                    stops=int(flight_data.get('stops', 0)),
                    duration=flight_data.get('duration'),
                    booking_url=flight_data.get('booking_url')
                )
                
                # Validate required fields
                if not all([flight.origin, flight.destination, flight.airline, 
                           flight.departure_date, flight.price]):
                    raise ValueError("Missing required flight fields")
                
                # Convert to Convex schema and save
                try:
                    convex_data = to_convex_flight(flight.dict())
                    logger.debug(f"Calling Convex mutation 'createFlight' for flight {idx + 1}")
                    result = await asyncio.wait_for(
                        self.convex.mutation("createFlight", convex_data),
                        timeout=self._operation_timeout
                    )
                    if result:
                        flight_ids.append(flight.id)
                        logger.info(f"✓ Saved flight {idx + 1}: {flight.airline} - ${flight.price} (Convex ID: {result})")
                    else:
                        logger.warning(f"⚠️ Flight {idx + 1} save returned None")
                except asyncio.TimeoutError:
                    logger.error(f"Timeout saving flight {idx + 1}")
                except Exception as e:
                    logger.error(f"Error saving flight {idx + 1}: {e}")
                
            except Exception as e:
                logger.error(f"Failed to save flight {idx}: {e}")
                # Continue with next flight
        
        logger.info(f"✓ FLIGHTS BATCH COMPLETE: Saved {len(flight_ids)}/{len(sorted_flights)} flights")
        return flight_ids
    
    # ==================== HOTEL OPERATIONS ====================
    async def create_hotels_batch(self, hotels: List[Dict[str, Any]], 
                                 itinerary_id: Optional[str] = None) -> List[str]:
        """
        Save top 5 hotels: 2 cheapest + 3 best rated
        
        Args:
            hotels: List of hotel data dictionaries
            itinerary_id: Optional itinerary to link hotels to
            
        Returns:
            List of created hotel IDs
        """
        logger.info(f"=== SAVING HOTELS BATCH: {len(hotels)} hotels ===")
        logger.debug(f"Itinerary ID: {itinerary_id}")
        
        if not hotels:
            logger.warning("No hotels to save")
            return []
        
        # Get 2 cheapest by price
        sorted_by_price = sorted(hotels, key=lambda x: float(x.get('price', float('inf'))))[:2]
        selected_hotels = sorted_by_price.copy()
        logger.debug(f"Selected {len(sorted_by_price)} cheapest hotels")
        
        # Get 3 best by rating (excluding already selected)
        selected_ids = {id(h) for h in selected_hotels}
        remaining = [h for h in hotels if id(h) not in selected_ids]
        sorted_by_rating = sorted(remaining, key=lambda x: float(x.get('rating', 0)), reverse=True)[:3]
        selected_hotels.extend(sorted_by_rating)
        logger.info(f"Selected total {len(selected_hotels)} hotels (2 cheapest + {len(sorted_by_rating)} best rated)")
        
        hotel_ids = []
        
        for hotel_data in selected_hotels:
            try:
                # Create hotel model
                hotel = Hotel(
                    itinerary_id=itinerary_id,
                    name=hotel_data.get('name', 'Unknown Hotel'),
                    address=hotel_data.get('address', ''),
                    check_in_date=hotel_data.get('check_in_date', ''),
                    check_out_date=hotel_data.get('check_out_date', ''),
                    price=float(hotel_data.get('price', 0)),
                    rating=float(hotel_data.get('rating')) if hotel_data.get('rating') else None,
                    amenities=hotel_data.get('amenities', []),
                    source=hotel_data.get('source', 'booking'),
                    property_type=hotel_data.get('property_type'),
                    booking_url=hotel_data.get('booking_url'),
                    image_url=hotel_data.get('image_url'),
                    reviews_count=hotel_data.get('reviews_count')
                )
                
                # Convert to Convex schema and save
                try:
                    convex_data = to_convex_hotel(hotel.dict())
                    logger.debug(f"Calling Convex mutation 'createHotel' for {hotel.name}")
                    result = await asyncio.wait_for(
                        self.convex.mutation("createHotel", convex_data),
                        timeout=self._operation_timeout
                    )
                    if result:
                        hotel_ids.append(hotel.id)
                        logger.info(f"✓ Saved hotel: {hotel.name} - ${hotel.price} (Convex ID: {result})")
                    else:
                        logger.warning(f"⚠️ Hotel save returned None for {hotel.name}")
                except asyncio.TimeoutError:
                    logger.error(f"Timeout saving hotel {hotel.name}")
                except Exception as e:
                    logger.error(f"Error saving hotel {hotel.name}: {e}")
                
            except Exception as e:
                logger.error(f"Failed to save hotel: {e}")
                logger.error(f"Hotel data: {hotel_data}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                # Continue with next hotel
        
        logger.info(f"✓ HOTELS BATCH COMPLETE: Saved {len(hotel_ids)}/{len(selected_hotels)} hotels")
        return hotel_ids
    
    # ==================== RESTAURANT OPERATIONS ====================
    async def create_restaurants_batch(self, restaurants: List[Dict[str, Any]], 
                                      itinerary_id: Optional[str] = None) -> List[str]:
        """
        Save all restaurant recommendations (max 30)
        
        Args:
            restaurants: List of restaurant data dictionaries
            itinerary_id: Optional itinerary to link restaurants to
            
        Returns:
            List of created restaurant IDs
        """
        logger.info(f"=== SAVING RESTAURANTS BATCH: {len(restaurants)} restaurants ===")
        logger.debug(f"Itinerary ID: {itinerary_id}")
        
        if not restaurants:
            logger.warning("No restaurants to save")
            return []
        
        # Limit to 30 restaurants
        restaurants_to_save = restaurants[:30]
        logger.info(f"Will save up to {len(restaurants_to_save)} restaurants")
        restaurant_ids = []
        
        for idx, restaurant_data in enumerate(restaurants_to_save, 1):
            try:
                # Create restaurant model
                restaurant = Restaurant(
                    itinerary_id=itinerary_id,
                    name=restaurant_data.get('name', 'Unknown Restaurant'),
                    address=restaurant_data.get('address', ''),
                    cuisine=restaurant_data.get('cuisine', []),
                    price_range=restaurant_data.get('price_range', '$$'),
                    rating=float(restaurant_data.get('rating')) if restaurant_data.get('rating') else None,
                    phone=restaurant_data.get('phone'),
                    website=restaurant_data.get('website'),
                    hours=restaurant_data.get('hours'),
                    status="found",
                    source_url=restaurant_data.get('source_url'),
                    description=restaurant_data.get('description')
                )
                
                # Validate required fields - cuisine can be empty array
                if not all([restaurant.name, restaurant.address, restaurant.price_range]):
                    logger.warning(f"Missing required fields for restaurant {idx}: name={restaurant.name}, address={restaurant.address}, price_range={restaurant.price_range}")
                    raise ValueError("Missing required restaurant fields")
                
                # Convert to Convex schema and save
                try:
                    convex_data = to_convex_restaurant(restaurant.dict())
                    result = await asyncio.wait_for(
                        self.convex.mutation("createRestaurant", convex_data),
                        timeout=self._operation_timeout
                    )
                    if result:
                        restaurant_ids.append(restaurant.id)
                except asyncio.TimeoutError:
                    logger.error(f"Timeout saving restaurant {restaurant.name}")
                except Exception as e:
                    logger.error(f"Error saving restaurant {restaurant.name}: {e}")
                
                if idx <= 5 or idx % 5 == 0:  # Log first 5 and every 5th
                    logger.info(f"✓ Saved restaurant {idx}/{len(restaurants_to_save)}: {restaurant.name}")
                
            except Exception as e:
                logger.error(f"Failed to save restaurant {idx}: {e}")
                logger.error(f"Restaurant data: {restaurant_data}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                # Continue with next restaurant
        
        logger.info(f"✓ RESTAURANTS BATCH COMPLETE: Saved {len(restaurant_ids)}/{len(restaurants_to_save)} restaurants")
        return restaurant_ids
    
    # ==================== ITINERARY OPERATIONS ====================
    @validate_required_fields(['destination', 'start_date', 'end_date'])
    async def create_itinerary(self, data: Dict[str, Any]) -> str:
        """
        Create a parent itinerary record
        
        Args:
            data: Itinerary data including destination, dates, etc.
            
        Returns:
            Created itinerary ID
            
        Raises:
            ValueError: If required fields are missing
            TimeoutError: If operation times out
        """
        try:
            itinerary = Itinerary(**data)
            convex_data = to_convex_itinerary(itinerary.dict())
            
            logger.debug(f"Calling Convex mutation 'createItinerary' for {itinerary.destination}")
            logger.debug(f"Convex data: {convex_data}")
            convex_id = await asyncio.wait_for(
                self.convex.mutation("createItinerary", convex_data),
                timeout=self._operation_timeout
            )
            if not convex_id:
                raise RuntimeError("Failed to create itinerary - no result returned")
            logger.info(f"✓ Created itinerary: {itinerary.id} (Convex: {convex_id}) for {itinerary.destination}")
            # Return the Convex ID so it can be used for child records
            return convex_id
        except asyncio.TimeoutError:
            logger.error(f"Timeout creating itinerary for {data.get('destination')}")
            raise
        except Exception as e:
            logger.error(f"Failed to create itinerary: {e}")
            raise
    
    async def create_itinerary_day(self, itinerary_id: str, day_number: int, date: str) -> str:
        """
        Create a day record for an itinerary
        
        Args:
            itinerary_id: Parent itinerary ID
            day_number: Day number (1, 2, 3, etc.)
            date: Date string (e.g., "Monday, August 19")
            
        Returns:
            Created day ID
        """
        logger.debug(f"Creating itinerary day {day_number} for itinerary {itinerary_id}")
        day = ItineraryDay(
            itinerary_id=itinerary_id,  # This is now a Convex ID
            day_number=day_number,
            date=date
        )
        # Map the data but use the Convex ID directly for itineraryId
        convex_data = to_convex_itinerary_day(day.dict())
        convex_data["itineraryId"] = itinerary_id  # Use Convex ID directly
        
        logger.debug(f"Calling Convex mutation 'createItineraryDay'")
        convex_id = await self.convex.mutation("createItineraryDay", convex_data)
        logger.info(f"✓ Created day {day_number}: {date} (Convex: {convex_id})")
        # Return the Convex ID for activities to reference
        return convex_id
    
    async def create_activity(self, itinerary_id: str, day_id: str, activity_data: Dict[str, Any]) -> str:
        """
        Create an activity for a specific day
        
        Args:
            day_id: Parent day ID
            activity_data: Activity details
            
        Returns:
            Created activity ID
            
        Raises:
            ValueError: If required fields are missing
        """
        logger.debug(f"Creating activity for day {day_id}: {activity_data.get('title', 'Unknown')}")
        
        # Validate required fields
        required_fields = ['title', 'time', 'duration', 'location', 'activity_type', 'additional_info']
        for field in required_fields:
            if field not in activity_data or not activity_data[field]:
                logger.warning(f"Missing required activity field: {field}")
                raise ValueError(f"Missing required activity field: {field}")
        
        activity = Activity(itinerary_day_id=day_id, **activity_data)
        # Map the data but use the Convex IDs directly
        convex_data = to_convex_activity(activity.dict())
        # Override with actual Convex IDs
        convex_data["itineraryId"] = itinerary_id  # Convex ID from createItinerary
        convex_data["itineraryDayId"] = day_id  # Convex ID from createItineraryDay
        
        logger.debug(f"Calling Convex mutation 'createActivity'")
        convex_id = await self.convex.mutation("createActivity", convex_data)
        logger.info(f"✓ Created activity: {activity.title} at {activity.time} (Convex: {convex_id})")
        return convex_id
    
    # ==================== JOB OPERATIONS ====================
    @validate_required_fields(['type', 'status'])
    async def create_job(self, data: Dict[str, Any]) -> str:
        """
        Create a job for tracking long-running operations
        
        Args:
            data: Job data including type, status, input
            
        Returns:
            Created job ID
            
        Raises:
            ValueError: If required fields are missing
        """
        logger.info(f"=== CREATING JOB: type={data.get('type')}, status={data.get('status')} ===")
        try:
            # Ensure input is JSON serializable
            if 'input' in data and not isinstance(data['input'], str):
                data['input'] = json.dumps(data['input'])
                logger.debug("Converted job input to JSON string")
            
            job = Job(**data)
            job_dict = job.dict()
            logger.debug(f"Job model created with ID: {job.id}")
            convex_data = to_convex_job(job_dict)
            logger.debug(f"Convex data prepared for job creation")
            
            logger.debug(f"Calling Convex mutation 'createJob'")
            convex_id = await asyncio.wait_for(
                self.convex.mutation("createJob", convex_data),
                timeout=self._operation_timeout
            )
            if not convex_id:
                raise RuntimeError("Failed to create job - no result returned")
            
            # Store mapping between our string ID and Convex ID
            self._job_id_mapping[job.id] = convex_id
            logger.info(f"✓ Created job: {job.id} (Convex: {convex_id}) of type {job.type}")
            logger.debug(f"Job ID mapping stored: {job.id} -> {convex_id}")
            return job.id
        except asyncio.TimeoutError:
            logger.error(f"Timeout creating job of type {data.get('type')}")
            raise
        except Exception as e:
            logger.error(f"Failed to create job: {e}")
            raise
    
    async def update_job_status(
        self, 
        job_id: str, 
        status: str, 
        progress: Optional[int] = None,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> bool:
        """
        Update job status and optionally progress/result/error
        
        Args:
            job_id: Job ID to update
            status: New status
            progress: Optional progress percentage (0-100)
            result: Optional result data
            error: Optional error message
            
        Returns:
            True if update successful
        """
        logger.info(f"=== UPDATING JOB: {job_id} to status={status}, progress={progress} ===")
        try:
            # Get Convex ID from our mapping
            convex_id = self._job_id_mapping.get(job_id)
            if not convex_id:
                logger.warning(f"⚠️ No Convex ID found for job {job_id} in mapping")
                logger.debug(f"Current job mappings: {list(self._job_id_mapping.keys())}")
                return False
            
            update_data = {
                "job_id": job_id,  # Use string ID as expected by mutation
                "status": status
            }
            
            if progress is not None:
                update_data["progress"] = max(0, min(100, progress))  # Ensure 0-100
            
            if result is not None:
                update_data["result"] = json.dumps(result) if not isinstance(result, str) else result
            
            if error is not None:
                # Truncate error to reasonable length
                update_data["error"] = error[:1000] if len(error) > 1000 else error
            
            logger.debug(f"Calling Convex mutation 'updateJob' with data: {update_data}")
            mutation_result = await asyncio.wait_for(
                self.convex.mutation("updateJob", update_data),
                timeout=self._operation_timeout
            )
            logger.info(f"✓ Updated job {job_id}: status={status}, progress={progress}")
            return mutation_result is not None
        except asyncio.TimeoutError:
            logger.error(f"❌ Timeout updating job {job_id}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to update job {job_id}: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False