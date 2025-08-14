from llama_index.core.agent.workflow import FunctionAgent
from typing import Dict, Any, Optional, List
import logging
from llama_index.core.agent.workflow import AgentStream, AgentOutput, ToolCallResult, ToolCall
from llama_index.core.workflow import Context
from pydantic import BaseModel, Field
from enum import Enum
import os
from agents.restaurant_agent import call_restaurant_agent
from service.restaurant.restaurant_agent_integration import call_restaurant_service_ddgs
from service.flight_service import call_flight_service
from service.hotel_service import call_hotel_service
from utils.llm_manager import get_powerful_llm


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        self.api_token = api_token
        self._workflow = None
        self._initialized = False
        
        logger.info("ItineraryWriter initialized")
    
    async def initialize(self) -> None:
        """Initialize the workflow and agents."""
        if self._initialized:
            return
            
        try:
            logger.info("Initializing itinerary writer service...")
            
            # Use the centralized LLM manager to get a powerful LLM
            llm = get_powerful_llm()
            
            # Create the workflow
            # Use the new DDGS restaurant service instead of the Tavily-based one
            self._workflow = FunctionAgent(
                name="orchestrator_agent",
                llm=llm,
                tools=[call_restaurant_service_ddgs, call_flight_service, call_hotel_service],
                system_prompt=(
    "You are an expert travel itinerary writer and orchestrator. "
    "You are given a user's travel request and a list of tools that can help research and gather travel information. "
    "You are to orchestrate the tools to research flights, hotels, and restaurants based on the user's specific travel requirements, then compile a comprehensive itinerary. "
    
    "Your task is to:\n"
    "1. Analyze the user's travel request to extract key details (origin, destination, dates, preferences, budget, interests)\n"
    "2. Use call_flight_service to fetch flight options based on the specified origin, destination, dates, and class preferences\n"
    "3. Use call_hotel_service to search for hotel accommodations at the destination using the travel dates\n"
    "4. Use call_restaurant_service_ddgs to find top restaurants at the destination that match the user's budget preferences and interests\n"
    "5. Compile all this information into a structured ItineraryWriterOutput format\n"
    
    "CRITICAL INSTRUCTIONS:\n"
    "- You MUST use the available tools to gather current, accurate information\n"
    "- Extract and focus on the specific destination, dates, and preferences mentioned in the user's request\n"
    "- Prioritize recommendations that align with the user's stated interests and budget constraints\n"
    "- Ensure all recommendations fit within the specified budget and travel dates\n"
    "- Once you have gathered all necessary information, format it into the required ItineraryWriterOutput structure\n"
    "- Do NOT get stuck in reasoning loops - make tool calls, gather information, then produce the final structured output\n"
    "- Always provide personalized recommendations based on the user's specific requirements and interests\n"),
                output_cls=ItineraryWriterOutput,
                initial_state={
                    "restaurants": [],
                    "flights": [],
                    "hotels": [],
                },
            )
            
            self._initialized = True
            logger.info("Itinerary writer service initialized successfully")
            
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
        try:
            workflow = await self.get_workflow()
            logger.info(f"Running itinerary workflow with query: {query}")
            
            # Run the workflow and await the handler to get the result
            handler = workflow.run(ctx=ctx, user_msg=query, **kwargs)
            async for event in handler.stream_events():
                if isinstance(event, AgentStream):
                    if event.delta:
                        print(event.delta, end="", flush=True)
                elif isinstance(event, AgentOutput):
                    if event.tool_calls:
                        print(
                            "🛠️  Planning to use tools:",
                            [call.tool_name for call in event.tool_calls],
                        )
                elif isinstance(event, ToolCallResult):
                    print(f"🔧 Tool Result ({event.tool_name}):")
                    print(f"  Arguments: {event.tool_kwargs}")
                    print(f"  Output: {event.tool_output}")
                elif isinstance(event, ToolCall):
                    print(f"🔨 Calling Tool: {event.tool_name}")
                    print(f"  With arguments: {event.tool_kwargs}")
            result = await handler
            
            logger.info("Itinerary workflow executed successfully")
            logger.info(f"Itinerary workflow result: {result}")
            
            # The result is the final output from the workflow
            # For AgentWorkflow, this typically contains the agent's response
            return result
            
        except Exception as e:
            logger.error(f"Itinerary workflow execution failed: {e}")
            raise ItineraryWriterError(f"Workflow execution failed: {e}")

    
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