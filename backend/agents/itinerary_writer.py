from llama_index.core.agent.workflow import FunctionAgent
from typing import Dict, Any, Optional, List
import logging
import json
import traceback
from datetime import datetime
from llama_index.core.agent.workflow import AgentStream, AgentOutput, ToolCallResult, ToolCall
from llama_index.core.workflow import Context
from pydantic import BaseModel, Field
from enum import Enum
import os
from agents.restaurant_agent import call_restaurant_agent
from service.flight_service import call_flight_service
from service.hotel_service import call_hotel_service
from utils.llm_manager import get_budget_llm
from database.travel_repository import TravelRepository


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class ItineraryWriterError(Exception):
    """Custom exception for itinerary writer errors."""
    pass

class ActivityType(str, Enum):
    """Types of activities in an itinerary."""
    FLIGHT = "flight"
    HOTEL = "hotel"
    MEAL = "meal"
    ACTIVITY = "activity"
    TRANSPORT = "transport"

class ItineraryActivity(BaseModel):
    """Individual activity within a day's itinerary."""
    time: str = Field(description="Time in 24-hour HH:MM format (e.g., '10:00', '15:30', '19:00')")
    title: str = Field(description="Activity title (e.g., 'Flight to LAX', 'Welcome Dinner')")
    description: str = Field(description="Detailed description of the activity")
    location: Optional[str] = Field(default=None, description="Location or address")
    duration: Optional[str] = Field(default=None, description="Duration in format 'Xh Ym' (e.g., '3h 45m', '2h', '45m')")
    activity_type: ActivityType = Field(description="Type of activity")
    additional_info: Optional[str] = Field(default=None, description="Additional details or notes")

class DayItinerary(BaseModel):
    """Itinerary for a single day."""
    day_number: int = Field(description="Day number (1, 2, 3, etc.)")
    date: str = Field(description="Date in format 'Day Name, Month Day' (e.g., 'Saturday, August 9')")
    year: int = Field(description="Year as integer (e.g., 2025)")
    activities: List[ItineraryActivity] = Field(description="List of activities for this day, sorted by time")

class ItineraryWriterOutput(BaseModel):
    """Complete multi-day itinerary output."""
    title: str = Field(description="Itinerary title")
    personalization: str = Field(description="Personalization note (e.g., 'Personalized for your interests: Outdoor activities, nature, adventure sports')")
    total_days: int = Field(description="Total number of days in the itinerary")
    days: List[DayItinerary] = Field(description="List of daily itineraries")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Your Itinerary",
                "personalization": "Personalized for your interests: Outdoor activities, nature, adventure sports",
                "total_days": 2,
                "days": [
                    {
                        "day_number": 1,
                        "date": "Saturday, August 9",
                        "year": 2025,
                        "activities": [
                            {
                                "time": "10:00",
                                "title": "Flight to LAX",
                                "description": "Depart from SFO",
                                "location": None,
                                "duration": "3h 45m",
                                "activity_type": "flight",
                                "additional_info": "Fixed timing"
                            },
                            {
                                "time": "15:30",
                                "title": "Hotel Check-in",
                                "description": "Central Hotel Downtown",
                                "location": "LAX",
                                "duration": None,
                                "activity_type": "hotel",
                                "additional_info": None
                            },
                            {
                                "time": "19:00",
                                "title": "Welcome Dinner",
                                "description": "Local cuisine restaurant recommended for first-time visitors",
                                "location": "Downtown area",
                                "duration": "2h",
                                "activity_type": "meal",
                                "additional_info": None
                            }
                        ]
                    }
                ]
            }
        }
    

class ItineraryWriter:
    """Service class for managing itinerary writing workflows."""
    
    def __init__(self, api_token: Optional[str] = None):
        """Initialize the itinerary writer service.
        
        Args:
            api_token: Optional API token for MCP agents
        """
        logger.info("=== INITIALIZING ITINERARY WRITER ===")
        self.api_token = api_token
        self._workflow = None
        self._initialized = False
        self.repository = TravelRepository()
        
        logger.info("✓ ItineraryWriter initialized")
    
    async def initialize(self) -> None:
        """Initialize the workflow and agents."""
        if self._initialized:
            logger.debug("Already initialized, skipping")
            return
            
        try:
            logger.info("=== INITIALIZING WORKFLOW AND AGENTS ===")
            
            # Use the centralized LLM manager to get a budget LLM
            logger.debug("Getting budget LLM from manager")
            llm = get_budget_llm()
            logger.info("✓ Got budget LLM instance")
            
            # Create the workflow
            logger.debug("Creating FunctionAgent workflow")
            self._workflow = FunctionAgent(
                name="orchestrator_agent",
                llm=llm,
                tools=[call_restaurant_agent, call_flight_service, call_hotel_service],
                system_prompt=(
    "You are an expert travel itinerary writer and orchestrator. "
    "You are given a user's travel request and a list of tools that can help research and gather travel information. "
    "You are to orchestrate the tools to research flights, hotels, and restaurants based on the user's specific travel requirements, then compile a comprehensive itinerary. "
    
    "Your task is to:\n"
    "1. Analyze the user's travel request to extract key details (origin, destination, dates, preferences, budget, interests)\n"
    "2. Use call_flight_service to fetch flight options based on the specified origin, destination, dates, and class preferences\n"
    "3. Use call_hotel_service to search for hotel accommodations at the destination using the travel dates\n"
    "4. Use call_restaurant_agent to find top restaurants at the destination that match the user's budget preferences and interests\n"
    "5. Compile all this information into a structured ItineraryWriterOutput format\n"
    
    "CRITICAL OUTPUT INSTRUCTIONS:\n"
    "- You MUST return a properly structured ItineraryWriterOutput with ALL required fields:\n"
    "  * title: A descriptive title for the itinerary (e.g., 'San Jose to Tokyo Travel Itinerary')\n"
    "  * personalization: A note about how the itinerary is personalized (e.g., 'Personalized for technology and food interests')\n"
    "  * total_days: The total number of days in the trip\n"
    "  * days: A list of DayItinerary objects, each containing:\n"
    "    - day_number: Sequential day number (1, 2, 3, etc.)\n"
    "    - date: Date in format 'Day Name, Month Day' (e.g., 'Friday, October 10')\n"
    "    - year: The year as an integer (e.g., 2025)\n"
    "    - activities: List of ItineraryActivity objects with time, title, description, location, duration, activity_type, and additional_info\n"
    "\n"
    "- Each day should include activities like:\n"
    "  * Morning: Departure flight or hotel checkout\n"
    "  * Afternoon: Arrival, hotel check-in, or sightseeing\n"
    "  * Evening: Restaurant recommendations from your research\n"
    "  * Activities should be based on the actual flight times, hotels, and restaurants you found\n"
    "\n"
    "- Use the data from your tool calls to populate the itinerary with real information\n"
    "- Ensure all recommendations fit within the specified budget and travel dates\n"
    "- Do NOT return raw JSON data from tools - transform it into the ItineraryWriterOutput format\n"
    "- Always provide personalized recommendations based on the user's specific requirements and interests\n"),
                output_cls=ItineraryWriterOutput,
                initial_state={
                    "restaurants": [],
                    "flights": [],
                    "hotels": [],
                },
            )
            
            self._initialized = True
            logger.info("✓ Itinerary writer service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize itinerary writer service: {e}")
            raise ItineraryWriterError(f"Initialization failed: {e}")
    
    async def get_workflow(self) -> FunctionAgent:
        """Get the initialized workflow.
        
        Returns:
            The FunctionAgent instance
            
        Raises:
            ItineraryWriterError: If workflow is not initialized
        """
        if not self._initialized:
            await self.initialize()
            
        if self._workflow is None:
            raise ItineraryWriterError("Workflow not properly initialized")
            
        return self._workflow
    
    async def run_workflow(self, query: str, ctx: Context, **kwargs) -> Any:
        """Run the workflow with a given query.
        
        Args:
            query: The query to process
            ctx: The workflow context
            **kwargs: Additional parameters for the workflow
            
        Returns:
            The workflow response
            
        Raises:
            ItineraryWriterError: If workflow execution fails
        """
        logger.info("=== RUNNING ITINERARY WORKFLOW ===")
        logger.debug(f"Query length: {len(query)} characters")
        logger.debug(f"Query preview: {query[:200]}...")
        
        try:
            workflow = await self.get_workflow()
            logger.info("✓ Got workflow instance, starting execution")
            
            # Run the workflow and await the handler to get the result
            logger.debug("Creating workflow handler")
            handler = workflow.run(ctx=ctx, user_msg=query, **kwargs)
            
            logger.info("Streaming workflow events...")
            tool_calls_made = []
            async for event in handler.stream_events():
                if isinstance(event, AgentStream):
                    if event.delta:
                        print(event.delta, end="", flush=True)
                elif isinstance(event, AgentOutput):
                    if event.tool_calls:
                        tools = [call.tool_name for call in event.tool_calls]
                        logger.info(f"🛠️ Planning to use tools: {tools}")
                        print(f"🛠️ Planning to use tools: {tools}")
                elif isinstance(event, ToolCallResult):
                    logger.info(f"🔧 Tool Result ({event.tool_name}): Success")
                    logger.debug(f"  Arguments: {event.tool_kwargs}")
                    logger.debug(f"  Output preview: {str(event.tool_output)[:200]}...")
                    print(f"🔧 Tool Result ({event.tool_name}):")
                    print(f"  Arguments: {event.tool_kwargs}")
                    print(f"  Output: {event.tool_output}")
                elif isinstance(event, ToolCall):
                    tool_calls_made.append(event.tool_name)
                    logger.info(f"🔨 Calling Tool: {event.tool_name}")
                    logger.debug(f"  With arguments: {event.tool_kwargs}")
                    print(f"🔨 Calling Tool: {event.tool_name}")
                    print(f"  With arguments: {event.tool_kwargs}")
            
            logger.info(f"Workflow event streaming complete. Tools called: {tool_calls_made}")
            result = await handler
            
            logger.info("✓ Itinerary workflow executed successfully")
            logger.debug(f"Result type: {type(result)}")
            logger.debug(f"Result preview: {str(result)[:500]}..." if result else "Result is None")
            
            # The result is the final output from the workflow
            # For AgentWorkflow, this typically contains the agent's response
            return result
            
        except Exception as e:
            logger.error(f"❌ Itinerary workflow execution failed: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise ItineraryWriterError(f"Workflow execution failed: {e}")

    
    async def save_itinerary_to_db(self, itinerary_output: ItineraryWriterOutput, 
                                   request_data: Dict[str, Any], 
                                   job_id: Optional[str] = None) -> str:
        """Save the itinerary to database in normalized format.
        
        Args:
            itinerary_output: The structured itinerary output
            request_data: Original request data (destination, dates, etc.)
            job_id: Optional job ID to update
            
        Returns:
            Created itinerary ID
        """
        logger.info("=== SAVING ITINERARY TO DATABASE ===")
        logger.debug(f"Itinerary has {len(itinerary_output.days)} days")
        logger.debug(f"Request data: {request_data}")
        
        try:
            # Create parent itinerary record
            itinerary_data = {
                "user_id": request_data.get("user_id"),
                "destination": request_data.get("destination", request_data.get("to_city", "")),
                "start_date": request_data.get("start_date", request_data.get("departure_date", "")),
                "end_date": request_data.get("end_date", request_data.get("return_date", "")),
                "status": "published"
            }
            logger.debug(f"Creating itinerary with data: {itinerary_data}")
            
            itinerary_id = await self.repository.create_itinerary(itinerary_data)
            logger.info(f"✓ Created parent itinerary: {itinerary_id}")
            
            # Create normalized days and activities
            logger.info(f"Creating {len(itinerary_output.days)} days with activities")
            for day in itinerary_output.days:
                logger.debug(f"Processing day {day.day_number}: {day.date}")
                
                # Create day record
                day_id = await self.repository.create_itinerary_day(
                    itinerary_id=itinerary_id,
                    day_number=day.day_number,
                    date=day.date
                )
                logger.info(f"✓ Created day {day.day_number}: {day.date} (ID: {day_id})")
                
                # Create activities for this day
                logger.debug(f"Creating {len(day.activities)} activities for day {day.day_number}")
                for idx, activity in enumerate(day.activities):
                    activity_data = {
                        "title": activity.title,
                        "time": activity.time,
                        "duration": activity.duration or "1h",
                        "location": activity.location or request_data.get("destination", ""),
                        "activity_type": activity.activity_type.value,
                        "additional_info": activity.additional_info or activity.description,
                        "order": idx
                    }
                    
                    activity_id = await self.repository.create_activity(itinerary_id, day_id, activity_data)
                    logger.debug(f"Created activity: {activity.title}")
            
            # Update job if provided
            if job_id:
                await self.repository.update_job_status(
                    job_id,
                    "completed",
                    result={
                        "itinerary_id": itinerary_id,
                        "total_days": itinerary_output.total_days,
                        "activities_count": sum(len(day.activities) for day in itinerary_output.days)
                    }
                )
            
            return itinerary_id
            
        except Exception as e:
            logger.error(f"❌ Failed to save itinerary to database: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            if job_id:
                logger.debug(f"Updating job {job_id} to failed status")
                error_msg = json.dumps({
                    "message": str(e),
                    "traceback": traceback.format_exc()[:800]
                })
                await self.repository.update_job_status(job_id, "failed", error=error_msg)
            raise
    
    def get_workflow_state(self) -> Dict[str, Any]:
        """Get the current workflow state.
        
        Returns:
            The current workflow state
        """
        if self._workflow is None:
            return {}
            
        return {
            "initialized": self._initialized,
            "has_workflow": self._workflow is not None,
        }

# Singleton instance management
_itinerary_writer_instance: Optional[ItineraryWriter] = None

def get_itinerary_writer(api_token: Optional[str] = None) -> ItineraryWriter:
    """Get or create the itinerary writer singleton.
    
    Args:
        api_token: Optional API token for MCP agents
        
    Returns:
        The ItineraryWriter singleton instance
    """
    global _itinerary_writer_instance
    
    if _itinerary_writer_instance is None:
        _itinerary_writer_instance = ItineraryWriter(api_token=api_token)
        logger.info("Created new ItineraryWriter singleton instance")
    
    return _itinerary_writer_instance

# Convenience function for backward compatibility
def get_agent_workflow_service(api_token: Optional[str] = None) -> ItineraryWriter:
    """Get the itinerary writer instance (backward compatibility).
    
    Args:
        api_token: Optional API token for MCP agents
        
    Returns:
        The ItineraryWriter instance
        
    Note:
        This function maintains backward compatibility with the old naming.
        Prefer using get_itinerary_writer() for new code.
    """
    return get_itinerary_writer(api_token=api_token)

def get_agent_workflow(api_token: Optional[str] = None) -> ItineraryWriter:
    """Get the itinerary writer instance (backward compatibility).
    
    Args:
        api_token: Optional API token for MCP agents
        
    Returns:
        The ItineraryWriter instance
        
    Note:
        This is a backward compatibility function that returns the service.
        Prefer using get_itinerary_writer() for new code.
    """
    return get_itinerary_writer(api_token=api_token)