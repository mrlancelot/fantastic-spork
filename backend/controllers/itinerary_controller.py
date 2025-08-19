from fastapi import APIRouter, HTTPException
from llama_index.core.workflow import Context
from agents.itinerary_writer import get_itinerary_writer, ItineraryWriterOutput
from schemas import ItineraryRequest, PriceRange, TripType

router = APIRouter(tags=["AI Agents"])


@router.post("/itinerary")
async def create_itinerary(request: ItineraryRequest) -> ItineraryWriterOutput:
    """
    Create a personalized travel itinerary based on flight details and travel interests.
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

        # Execute the itinerary workflow
        itinerary_writer = get_itinerary_writer()
        workflow = await itinerary_writer.get_workflow()
        ctx = Context(workflow)
        result = await itinerary_writer.run_workflow(full_query, ctx=ctx)

        return ItineraryWriterOutput(
            status="success",
            title=result.structured_response.get("title", "Travel Itinerary"),
            personalization=result.structured_response.get(
                "personalization", "Personalized travel itinerary"
            ),
            total_days=result.structured_response.get("total_days", 0),
            days=result.structured_response.get("days", []),
            trip_details={
                "trip_type": request.trip_type,
                "route": f"{request.from_city} → {request.to_city}",
                "departure_date": request.departure_date,
                "return_date": request.return_date,
                "passengers": request.adults,
                "travel_class": request.travel_class,
                "interests": request.interests,
                "price_range": request.price_range,
            },
            message="Itinerary created successfully",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Itinerary creation failed: {str(e)}")
