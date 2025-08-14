from fastapi import APIRouter, HTTPException
from llama_index.core.workflow import Context
from agents.itinerary_writer import get_itinerary_writer, ItineraryWriterOutput
from schemas import ItineraryRequest, PriceRange, TripType
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(tags=["AI Agents"])


@router.post("/itinerary")
async def create_itinerary(request: ItineraryRequest):
    """
    Create a personalized travel itinerary based on flight details and travel interests.
    """
    try:
        # Log incoming request
        logger.info("="*60)
        logger.info("INCOMING REQUEST:")
        logger.info(json.dumps(request.model_dump(), indent=2, default=str))
        logger.info("="*60)
        
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
