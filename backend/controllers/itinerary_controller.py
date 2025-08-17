from fastapi import APIRouter, HTTPException, BackgroundTasks
from llama_index.core.workflow import Context
from agents.itinerary_writer import get_itinerary_writer, ItineraryWriterOutput
from schemas import ItineraryRequest, PriceRange, TripType
from utils.job_manager import get_job_manager, JobStatus
from utils.convex_client import get_db
import logging
import json
import uuid
import asyncio
import re
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def parse_duration_to_hours(duration_str: Optional[str]) -> float:
    """Parse duration string to float hours.
    Examples:
    - "2h 30m" -> 2.5
    - "1h" -> 1.0
    - "45m" -> 0.75
    - "5h 42m" -> 5.7
    - None or empty -> 0.0
    """
    if not duration_str:
        return 0.0
    
    # Convert to string if not already
    duration_str = str(duration_str).strip()
    
    # Initialize hours and minutes
    total_hours = 0.0
    
    # Pattern for hours: match numbers followed by h/hour/hours
    hour_pattern = r'(\d+\.?\d*)\s*h(?:our)?s?\b'
    hour_match = re.search(hour_pattern, duration_str, re.IGNORECASE)
    if hour_match:
        total_hours += float(hour_match.group(1))
    
    # Pattern for minutes: match numbers followed by m/min/minute/minutes
    minute_pattern = r'(\d+\.?\d*)\s*m(?:in(?:ute)?s?)?\b'
    minute_match = re.search(minute_pattern, duration_str, re.IGNORECASE)
    if minute_match:
        total_hours += float(minute_match.group(1)) / 60.0
    
    # If no patterns matched, try to parse as a plain number (assume hours)
    if not hour_match and not minute_match:
        try:
            total_hours = float(duration_str)
        except ValueError:
            return 0.0
    
    return round(total_hours, 2)  # Round to 2 decimal places

router = APIRouter(tags=["AI Agents"])


async def process_itinerary_async(job_id: str, request: ItineraryRequest, itinerary_uuid: str):
    """Background task to process itinerary generation"""
    job_manager = get_job_manager()
    db = get_db()
    
    try:
        # Mark job as processing
        job_manager.start_job(job_id)
        
        # Build comprehensive query from request data
        query_parts = []

        # Flight information
        trip_info = f"Planning a {request.trip_type.replace('_', ' ')} trip from {request.from_city} to {request.to_city}"
        query_parts.append(trip_info)

        # Dates
        if request.departure_date:
            query_parts.append(f"departing on {request.departure_date}")
        if request.return_date and request.trip_type == TripType.ROUND_TRIP:
            query_parts.append(f"returning on {request.return_date}")

        # Travel class and passengers
        class_info = f"for {request.adults} adult(s) in {request.travel_class.replace('_', ' ')} class"
        query_parts.append(class_info)

        # Travel interests
        if request.interests:
            query_parts.append(f"Travel interests and preferences: {request.interests}")

        # Price range for restaurants
        if request.price_range:
            price_guidance = {
                PriceRange.BUDGET: "budget-friendly options under $25 per person",
                PriceRange.MID_RANGE: "mid-range options $25-50 per person",
                PriceRange.UPSCALE: "upscale dining options $50+ per person",
            }
            query_parts.append(
                f"Restaurant budget preference: {price_guidance[request.price_range]}"
            )

        # Combine all parts into a comprehensive query
        full_query = (
            ". ".join(query_parts)
            + ". Please create a detailed itinerary with flights recommendations, hotel recommendations, restaurant recommendations, and activities."
        )

        logger.info(f"Processing job {job_id} with query: {full_query}")
        
        # Execute the itinerary workflow
        itinerary_writer = get_itinerary_writer()
        workflow = await itinerary_writer.get_workflow()
        ctx = Context(workflow)
        result = await itinerary_writer.run_workflow(full_query, ctx=ctx)
        
        # Parse result
        response_data = {}
        if isinstance(result, str):
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            try:
                response_data = json.loads(result.strip())
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON from string result")
                response_data = {}
        elif hasattr(result, 'structured_response') and result.structured_response:
            response_data = result.structured_response
        elif hasattr(result, 'response'):
            if isinstance(result.response, str):
                try:
                    if "```json" in result.response:
                        cleaned = result.response.split("```json")[1].split("```")[0]
                    elif "```" in result.response:
                        cleaned = result.response.split("```")[1].split("```")[0]
                    else:
                        cleaned = result.response
                    response_data = json.loads(cleaned.strip())
                except json.JSONDecodeError:
                    response_data = {}
            else:
                response_data = result.response
        elif isinstance(result, dict):
            response_data = result
        
        # Save itinerary to database
        # TODO: Replace with actual user ID from Clerk auth when integrated
        user_id = "user_" + str(uuid.uuid4())[:8]  # Temporary user ID
        
        itinerary_data = {
            "userId": user_id,  # Required field
            "destination": request.to_city,
            "startDate": request.departure_date,
            "endDate": request.return_date or request.departure_date,
            "interests": [request.interests] if request.interests else [],
            "status": "published",
            "data": response_data
        }
        
        # Only add budget if it has a value (it's optional)
        # Don't send None for optional fields
        # Budget could come from request or from response_data
        budget_value = None  # We don't have budget in request, it's optional
        
        itinerary_id = db.save_itinerary(itinerary_data)
        logger.info(f"Saved itinerary {itinerary_id} to database")
        
        # Save activities
        days = response_data.get("days", [])
        activity_ids = []
        for day in days:
            for activity in day.get("activities", []):
                activity_data = {
                    "itineraryId": itinerary_id,
                    "day": day.get("day_number", 1),
                    "time": activity.get("time", ""),
                    "title": activity.get("title", ""),
                    "description": activity.get("description"),
                    "location": activity.get("location"),
                    "duration": parse_duration_to_hours(activity.get("duration")),  # Parse duration to float hours
                    "type": activity.get("activity_type")
                }
                activity_id = db.save_activity(activity_data)
                activity_ids.append(activity_id)
        
        logger.info(f"Saved {len(activity_ids)} activities to database")
        
        # Save flight recommendations
        flight_ids = []
        for flight in response_data.get("flight_recommendations", []):
            flight_data = {
                "itineraryId": itinerary_id,
                "userId": user_id,  # Use same user ID as itinerary
                "origin": request.from_city,
                "destination": request.to_city,
                "departureDate": request.departure_date,
                "returnDate": request.return_date,
                "airline": flight.get("airline", "Unknown"),
                "flightNumber": flight.get("flight_number", f"FL{uuid.uuid4().hex[:6].upper()}"),
                "price": float(flight.get("price", 0)),
                "currency": "USD",
                "duration": flight.get("duration"),
                "class": request.travel_class,
                "stops": flight.get("stops", 0),
                "status": "searching"
            }
            flight_id = db.save_flight(flight_data)
            flight_ids.append(flight_id)
        
        # Save hotel recommendations
        hotel_ids = []
        for hotel in response_data.get("hotel_recommendations", []):
            # Extract price properly (it might be in a "price" field as string like "$2,962")
            price_str = hotel.get("price", "0")
            if isinstance(price_str, str):
                # Remove $ and commas, then convert to float
                price_cleaned = price_str.replace('$', '').replace(',', '').strip()
                try:
                    price = float(price_cleaned)
                except:
                    price = 0.0
            else:
                price = float(price_str)
            
            # Skip hotels with invalid prices
            if price <= 0 or price > 100000:
                logger.warning(f"Skipping hotel {hotel.get('name')} with invalid price: {price_str}")
                continue
                
            hotel_data = {
                "itineraryId": itinerary_id,
                "userId": user_id,  # Use same user ID as itinerary
                "name": hotel.get("name", "Unknown Hotel"),
                "address": hotel.get("address", ""),
                "city": request.to_city,
                "country": "",
                "checkInDate": request.departure_date,
                "checkOutDate": request.return_date or request.departure_date,
                "price": price,
                "currency": "USD",
                "rating": hotel.get("rating"),
                "amenities": hotel.get("amenities", []),
                "status": "searching"
            }
            hotel_id = db.save_hotel(hotel_data)
            hotel_ids.append(hotel_id)
        
        # Complete job with result
        result_data = {
            "itinerary_id": itinerary_id,
            "itinerary_uuid": itinerary_uuid,
            "activity_count": len(activity_ids),
            "flight_count": len(flight_ids),
            "hotel_count": len(hotel_ids)
        }
        
        job_manager.complete_job(job_id, result_data)
        logger.info(f"Job {job_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {str(e)}")
        job_manager.fail_job(job_id, str(e))


@router.post("/itinerary")
async def create_itinerary(request: ItineraryRequest, background_tasks: BackgroundTasks):
    """
    Create a personalized travel itinerary based on flight details and travel interests.
    Returns a job ID for polling status.
    """
    try:
        # Log incoming request
        logger.info("="*60)
        logger.info("INCOMING REQUEST:")
        logger.info(json.dumps(request.model_dump(), indent=2, default=str))
        logger.info("="*60)
        
        # Create job
        job_manager = get_job_manager()
        itinerary_uuid = str(uuid.uuid4())
        
        # Create job record and get the job ID
        # TODO: Get actual user ID from auth when integrated
        job_id = job_manager.create_job(
            job_type="itinerary_generation",
            user_id=None,  # Will be set when Clerk auth is integrated
            payload={
                "request": request.model_dump(),
                "itinerary_uuid": itinerary_uuid
            }
        )
        
        # Start background processing
        background_tasks.add_task(
            process_itinerary_async,
            job_id,
            request,
            itinerary_uuid
        )
        
        # Return job ID immediately
        return {
            "status": "accepted",
            "job_id": job_id,
            "itinerary_uuid": itinerary_uuid,
            "message": "Itinerary generation started. Poll /itinerary/status/{job_id} for status.",
            "polling_interval_seconds": 5
        }
        
    except Exception as e:
        logger.error(f"Failed to create itinerary job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create itinerary: {str(e)}")


@router.get("/itinerary/status/{job_id}")
async def get_itinerary_status(job_id: str):
    """
    Get the status of an itinerary generation job.
    Poll this endpoint every 5 seconds to check if the job is complete.
    """
    try:
        job_manager = get_job_manager()
        job = job_manager.get_job_status(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        response = {
            "job_id": job_id,
            "status": job.get("status"),
            "created_at": job.get("createdAt"),
            "started_at": job.get("startedAt"),
            "completed_at": job.get("completedAt"),
            "error": job.get("error")
        }
        
        # If completed, include result
        if job.get("status") == JobStatus.COMPLETED:
            result = job.get("result", {})
            response["result"] = {
                "itinerary_id": result.get("itinerary_id"),
                "itinerary_uuid": result.get("itinerary_uuid"),
                "activity_count": result.get("activity_count"),
                "flight_count": result.get("flight_count"),
                "hotel_count": result.get("hotel_count")
            }
            response["next_step"] = f"Fetch complete itinerary from /itinerary/{result.get('itinerary_uuid')}"
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")


@router.get("/itinerary/{itinerary_uuid}")
async def get_itinerary(itinerary_uuid: str):
    """
    Fetch complete itinerary data by UUID.
    Call this after the job is completed to get all itinerary details.
    """
    try:
        db = get_db()
        
        # Query itinerary by UUID (stored in data field)
        # Note: This is a simplified query - in production you'd have a UUID field
        complete_data = db.query("queries:getCompleteItinerary", {"itineraryId": itinerary_uuid})
        
        if not complete_data:
            raise HTTPException(status_code=404, detail="Itinerary not found")
        
        return {
            "status": "success",
            "itinerary": complete_data.get("itinerary"),
            "activities": complete_data.get("activities"),
            "flights": complete_data.get("flights"),
            "hotels": complete_data.get("hotels"),
            "restaurants": complete_data.get("restaurants")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch itinerary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch itinerary: {str(e)}")


# Keep the old synchronous endpoint temporarily for backward compatibility
@router.post("/itinerary/sync")
async def create_itinerary_sync(request: ItineraryRequest):
    """
    [DEPRECATED] Synchronous itinerary creation - use /itinerary instead for async processing.
    """
    try:
        # Build comprehensive query from request data
        query_parts = []

        # Flight information
        trip_info = f"Planning a {request.trip_type.replace('_', ' ')} trip from {request.from_city} to {request.to_city}"
        query_parts.append(trip_info)

        # Dates
        if request.departure_date:
            query_parts.append(f"departing on {request.departure_date}")
        if request.return_date and request.trip_type == TripType.ROUND_TRIP:
            query_parts.append(f"returning on {request.return_date}")

        # Travel class and passengers
        class_info = f"for {request.adults} adult(s) in {request.travel_class.replace('_', ' ')} class"
        query_parts.append(class_info)

        # Travel interests
        if request.interests:
            query_parts.append(f"Travel interests and preferences: {request.interests}")

        # Price range for restaurants
        if request.price_range:
            price_guidance = {
                PriceRange.BUDGET: "budget-friendly options under $25 per person",
                PriceRange.MID_RANGE: "mid-range options $25-50 per person",
                PriceRange.UPSCALE: "upscale dining options $50+ per person",
            }
            query_parts.append(
                f"Restaurant budget preference: {price_guidance[request.price_range]}"
            )

        # Combine all parts into a comprehensive query
        full_query = (
            ". ".join(query_parts)
            + ". Please create a detailed itinerary with flights recommendations, hotel recommendations, restaurant recommendations, and activities."
        )

        # Log the query being sent to agent
        logger.info("QUERY TO AGENT:")
        logger.info(full_query)
        logger.info("-"*60)
        
        # Execute the itinerary workflow
        itinerary_writer = get_itinerary_writer()
        workflow = await itinerary_writer.get_workflow()
        ctx = Context(workflow)
        result = await itinerary_writer.run_workflow(full_query, ctx=ctx)
        
        # Log raw result from agent
        logger.info("RAW RESULT FROM AGENT:")
        logger.info(f"Type: {type(result)}")
        logger.info(f"Content: {str(result)[:1000]}...")  # First 1000 chars
        logger.info("-"*60)

        # Handle the actual response structure from the agent
        # The agent may return a JSON string or a structured response
        response_data = {}
        
        # First, try to extract the raw response
        if isinstance(result, str):
            # If result is a string, try to parse it as JSON
            # Clean up the response if it has markdown code blocks
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            try:
                response_data = json.loads(result.strip())
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON from string result: {result[:200]}")
                response_data = {}
        elif hasattr(result, 'structured_response') and result.structured_response:
            response_data = result.structured_response
        elif hasattr(result, 'response'):
            if isinstance(result.response, str):
                # Try to parse as JSON if it's a string
                try:
                    if "```json" in result.response:
                        cleaned = result.response.split("```json")[1].split("```")[0]
                    elif "```" in result.response:
                        cleaned = result.response.split("```")[1].split("```")[0]
                    else:
                        cleaned = result.response
                    response_data = json.loads(cleaned.strip())
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse JSON from response: {result.response[:200]}")
                    response_data = {}
            else:
                response_data = result.response
        elif isinstance(result, dict):
            response_data = result
        
        # Log the parsed response for debugging
        logger.info(f"Parsed response_data: {json.dumps(response_data, indent=2) if response_data else 'Empty'}")
        
        # Check if days already exists in the parsed response
        if "days" in response_data:
            # Use the already-parsed days array directly
            days = response_data.get("days", [])
            flight_recommendations = response_data.get("flight_recommendations", [])
            hotel_recommendations = response_data.get("hotel_recommendations", [])
            
            # Fix date format to be YYYY-MM-DD for frontend parsing
            from datetime import datetime, timedelta
            base_date = datetime.strptime(request.departure_date, "%Y-%m-%d") if request.departure_date else datetime.now()
            
            for i, day in enumerate(days):
                current_date = base_date + timedelta(days=i)
                day["date"] = current_date.strftime("%Y-%m-%d")
                day["day_name"] = current_date.strftime("%A")
                day["month_day"] = current_date.strftime("%B %d")
                
            logger.info(f"Using pre-parsed days array with {len(days)} days")
        else:
            # Fall back to extracting from old structure if needed
            itinerary_data = response_data.get("itinerary", {})
            flight_recommendations = response_data.get("flight_recommendations", [])
            hotel_recommendations = response_data.get("hotel_recommendations", [])
            
            # Transform the day-based itinerary structure to the expected format
            days = []
            if itinerary_data:
                # The itinerary has keys like 'day_1', 'day_2', etc.
                day_num = 1
                while f"day_{day_num}" in itinerary_data:
                    day_data = itinerary_data[f"day_{day_num}"]
                    
                    # Transform activities and restaurant recommendations into ItineraryActivity format
                    activities = []
                    
                    # Add general activities
                    for idx, activity in enumerate(day_data.get("activities", []), 1):
                        activities.append({
                            "time": f"{9 + idx * 2:02d}:00",  # Generate times starting from 09:00
                            "title": activity[:50] if len(activity) > 50 else activity,  # Truncate long titles
                            "description": activity,
                            "location": request.to_city,
                            "duration": None,
                            "activity_type": "activity",
                            "additional_info": None
                        })
                    
                    # Add restaurant recommendations as meal activities
                    for restaurant in day_data.get("restaurant_recommendations", []):
                        activities.append({
                            "time": "19:00",  # Default dinner time
                            "title": f"Dinner at {restaurant.get('name', 'Local Restaurant')}",
                            "description": restaurant.get("description", ""),
                            "location": restaurant.get("name", ""),
                            "duration": "2h",
                            "activity_type": "meal",
                            "additional_info": restaurant.get("description", "")
                        })
                    
                    days.append({
                        "day_number": day_num,
                        "date": f"Day {day_num}",
                        "year": 2025,  # Default year
                        "activities": activities
                    })
                    
                    day_num += 1
        
        # Create a custom response that includes all the data
        final_response = {
            "status": "success",
            "title": f"Your {request.to_city} Travel Itinerary",
            "personalization": f"Personalized for your interests: {request.interests}",
            "total_days": len(days),
            "days": days,
            "flight_recommendations": flight_recommendations,
            "hotel_recommendations": hotel_recommendations,
            "trip_details": {
                "trip_type": request.trip_type,
                "route": f"{request.from_city} → {request.to_city}",
                "departure_date": request.departure_date,
                "return_date": request.return_date,
                "passengers": request.adults,
                "travel_class": request.travel_class,
                "interests": request.interests,
                "price_range": request.price_range,
            },
            "message": "Itinerary created successfully",
        }
        
        # Log final response
        logger.info("="*60)
        logger.info("FINAL RESPONSE TO FRONTEND:")
        logger.info(json.dumps(final_response, indent=2, default=str))
        logger.info("="*60)
        
        return final_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Itinerary creation failed: {str(e)}")
