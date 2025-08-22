import json
import logging
import traceback
from fastapi import APIRouter, HTTPException
from llama_index.core.workflow import Context
from agents.itinerary_writer import get_itinerary_writer, ItineraryWriterOutput
from schemas import ItineraryRequest, PriceRange, TripType
from database.travel_repository import TravelRepository

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
router = APIRouter(tags=["AI Agents"])


@router.post("/itinerary")
async def create_itinerary(request: ItineraryRequest) -> ItineraryWriterOutput:
    """
    Create a personalized travel itinerary based on flight details and travel interests.
    """
    logger.info(f"=== STARTING ITINERARY CREATION ===")
    logger.info(f"Request: from={request.from_city}, to={request.to_city}, departure={request.departure_date}, return={request.return_date}")
    logger.info(f"Details: adults={request.adults}, class={request.travel_class}, type={request.trip_type}")
    logger.debug(f"Full request data: {request.dict()}")
    
    repository = TravelRepository()
    job_id = None
    
    try:
        # Create a job to track progress
        job_data = {
            "type": "itinerary_generation",
            "status": "pending",
            "input": request.dict(),
            "progress": 0
        }
        logger.debug(f"Creating job with data: {job_data}")
        job_id = await repository.create_job(job_data)
        logger.info(f"✓ Created job {job_id} for itinerary generation")
        
        # Update job status to processing
        logger.debug(f"Updating job {job_id} status to 'processing' (progress=10)")
        await repository.update_job_status(job_id, "processing", progress=10)
        logger.info(f"✓ Job {job_id} status updated to processing")
        
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
        logger.info(f"Built query with {len(query_parts)} parts")
        logger.debug(f"Full query: {full_query}")

        # Update job status for workflow start
        logger.debug(f"Updating job {job_id} status to 'processing' (progress=20)")
        await repository.update_job_status(job_id, "processing", progress=20)  # Use allowed status
        logger.info(f"✓ Starting workflow execution")
        
        # Execute the itinerary workflow
        logger.debug("Getting itinerary writer instance")
        itinerary_writer = get_itinerary_writer()
        logger.info("✓ Got itinerary writer instance")
        
        # Initialize the writer
        logger.debug("Initializing itinerary writer")
        await itinerary_writer.initialize()
        logger.info("✓ Itinerary writer initialized")
        
        # Create workflow context with job tracking
        logger.debug("Creating workflow context")
        workflow = await itinerary_writer.get_workflow()
        ctx = Context(workflow)
        
        # Add job_id to context for progress updates
        ctx.data = {"job_id": job_id}
        logger.debug(f"Context data set with job_id: {job_id}")
        
        # Run the workflow (this will call flights, hotels, restaurants)
        logger.info("=== STARTING WORKFLOW EXECUTION ===")
        result = await itinerary_writer.run_workflow(full_query, ctx=ctx)
        logger.info(f"✓ Workflow completed, result type: {type(result)}")
        logger.debug(f"Result preview: {str(result)[:500]}..." if result else "Result is empty")
        
        # Update job status to generating itinerary
        logger.debug(f"Updating job {job_id} status to 'processing' (progress=80)")
        await repository.update_job_status(job_id, "processing", progress=80)  # Use allowed status
        logger.info("✓ Processing itinerary results")

        # Prepare request data for database save
        request_data = {
            "user_id": getattr(request, "user_id", None),
            "destination": request.to_city,
            "to_city": request.to_city,
            "from_city": request.from_city,
            "departure_date": request.departure_date,
            "return_date": request.return_date,
            "start_date": request.departure_date,
            "end_date": request.return_date
        }

        # Check if result has structured_response attribute (proper Pydantic model)
        if hasattr(result, 'structured_response') and result.structured_response:
            # Proper structured response from the agent
            response_data = result.structured_response
            if isinstance(response_data, dict):
                # It's a dictionary, use it directly
                output = ItineraryWriterOutput(
                    status="success",
                    title=response_data.get("title", "Travel Itinerary"),
                    personalization=response_data.get(
                        "personalization", "Personalized travel itinerary"
                    ),
                    total_days=response_data.get("total_days", 0),
                    days=response_data.get("days", []),
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
                
                # Save itinerary to database
                try:
                    itinerary_id = await itinerary_writer.save_itinerary_to_db(
                        output,
                        request_data,
                        job_id
                    )
                    logger.info(f"Saved itinerary {itinerary_id} to database")
                    
                    # Update job to completed
                    logger.debug(f"Updating job {job_id} to completed status")
                    await repository.update_job_status(
                        job_id, 
                        "completed", 
                        progress=100,
                        result={"itinerary_id": itinerary_id}
                    )
                    logger.info(f"✓ Job {job_id} marked as completed")
                except Exception as e:
                    logger.error(f"❌ Failed to save itinerary to database: {e}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    # Don't fail the response, just log the error
                
                return output
            else:
                # It's a Pydantic model, use its attributes
                output = ItineraryWriterOutput(
                    status="success",
                    title=response_data.title,
                    personalization=response_data.personalization,
                    total_days=response_data.total_days,
                    days=response_data.days,
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
                
                # Save itinerary to database
                try:
                    logger.info("=== SAVING ITINERARY TO DATABASE ===")
                    logger.debug(f"Saving with request_data: {request_data}")
                    logger.debug(f"Response data type: {type(response_data)}")
                    itinerary_id = await itinerary_writer.save_itinerary_to_db(
                        response_data,
                        request_data,
                        job_id
                    )
                    logger.info(f"✓ Saved itinerary {itinerary_id} to database")
                    
                    # Update job to completed
                    logger.debug(f"Updating job {job_id} to completed status")
                    await repository.update_job_status(
                        job_id, 
                        "completed", 
                        progress=100,
                        result={"itinerary_id": itinerary_id}
                    )
                    logger.info(f"✓ Job {job_id} marked as completed")
                except Exception as e:
                    logger.error(f"❌ Failed to save itinerary to database: {e}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    # Don't fail the response, just log the error
                
                return output
        elif isinstance(result, str):
            # Result is a JSON string, parse it
            import json
            try:
                # Remove markdown code blocks if present
                if "```json" in result:
                    start = result.find("```json") + 7
                    end = result.find("```", start)
                    result = result[start:end].strip()
                elif "```" in result:
                    start = result.find("```") + 3
                    end = result.find("```", start)
                    result = result[start:end].strip()
                
                parsed_data = json.loads(result)
                output = ItineraryWriterOutput(
                    status="success",
                    title=parsed_data.get("title", "Travel Itinerary"),
                    personalization=parsed_data.get(
                        "personalization", "Personalized travel itinerary"
                    ),
                    total_days=parsed_data.get("total_days", 0),
                    days=parsed_data.get("days", []),
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
                
                # Save itinerary to database
                try:
                    logger.info("=== SAVING ITINERARY TO DATABASE (from JSON) ===")
                    logger.debug(f"Saving with request_data: {request_data}")
                    logger.debug(f"Parsed data has {parsed_data.get('total_days', 0)} days")
                    # Create ItineraryWriterOutput from parsed data
                    from agents.itinerary_writer import ItineraryWriterOutput as AgentOutput
                    agent_output = AgentOutput(**parsed_data)
                    
                    itinerary_id = await itinerary_writer.save_itinerary_to_db(
                        agent_output,
                        request_data,
                        job_id
                    )
                    logger.info(f"✓ Saved itinerary {itinerary_id} to database")
                    
                    # Update job to completed
                    logger.debug(f"Updating job {job_id} to completed status")
                    await repository.update_job_status(
                        job_id, 
                        "completed", 
                        progress=100,
                        result={"itinerary_id": itinerary_id}
                    )
                    logger.info(f"✓ Job {job_id} marked as completed")
                except Exception as e:
                    logger.error(f"❌ Failed to save itinerary to database: {e}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    # Don't fail the response, just log the error
                
                return output
            except json.JSONDecodeError as e:
                if job_id:
                    await repository.update_job_status(
                        job_id, 
                        "failed", 
                        error=f"Failed to parse itinerary JSON: {str(e)}"
                    )
                raise HTTPException(status_code=500, detail=f"Failed to parse itinerary JSON: {str(e)}")
        else:
            # Unexpected result type
            if job_id:
                await repository.update_job_status(
                    job_id, 
                    "failed", 
                    error=f"Unexpected result type: {type(result)}"
                )
            raise HTTPException(status_code=500, detail=f"Unexpected result type: {type(result)}")
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        logger.error(f"❌ HTTP exception in itinerary creation")
        raise
    except Exception as e:
        # Log the full error for debugging
        logger.error(f"❌ ITINERARY CREATION FAILED: {e}")
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        
        # Update job status if we have a job_id
        if job_id:
            error_details = {
                "message": str(e),
                "traceback": traceback.format_exc()[:1000]  # Truncate to 1000 chars
            }
            await repository.update_job_status(
                job_id, 
                "failed", 
                error=json.dumps(error_details)
            )
        
        raise HTTPException(status_code=500, detail=f"Itinerary creation failed: {str(e)}")